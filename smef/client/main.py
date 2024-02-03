
from __future__ import annotations
from datetime import datetime
from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from qtmodern.windows import ModernWindow
from qtpy.uic import loadUi
from smef.client.settings_widget import ConnectionsSettings

from smef.fi7000_interface.config import FL7000_Config
from smef.fi7000_interface.fl7000_driver import FL7000_Interface
from smef.client.main_widget import MainWidget
from smef.client.viewer import Viewer
from smef.client.new_session import NewSession
from loguru import logger
from PyQt6.QtWidgets import QApplication
from smef.utils import open_file_system

class MainWindow(QMainWindow):
    main_layout: QtWidgets.QVBoxLayout
    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('ui', 'main.ui'), self)
        self.setWindowTitle('СМЭП Клиент v2.2.0')
        self.config = FL7000_Config()
        self.device = FL7000_Interface(self.config)
        self.main_widget = MainWidget(self.config)
        self.viewer = Viewer(self.config)
        self.new_session_widget = NewSession(self.config)
        self.settings_widget = ConnectionsSettings(self.config)
        self.main_layout.addWidget(self.main_widget)

        self.main_widget.plotter_start_button.setEnabled(False)
        self.main_widget.plotter_stop_button.setEnabled(False)

        self.timer = QTimer()
        self.timer.timeout.connect(self._plot_process)

        self.main_widget.new_session_button.pressed.connect(self.new_session_widget.show)
        self.main_widget.dark_theme_checkbox.stateChanged.connect(self.viewer.change_theme)
        self.main_widget.new_session_button.pressed.connect(self.new_session_widget.generate_name)
        self.main_widget.open_session_viewer_button.pressed.connect(self.open_viewer)
        self.main_widget.connection_settings_button.pressed.connect(self.settings_widget.show)
        self.main_widget.plotter_interval_spin_box.valueChanged.connect(self.device.set_measuring_period)
        self.main_widget.calib_probs_check_box.stateChanged.connect(self.calibrate_measures)
        self.main_widget.units_changed.connect(self._plot_process)
        self.main_widget.plotter_interval_spin_box.valueChanged.connect(
            lambda period: self.timer.setInterval(int(period * 1000)))
        self.main_widget.start_pressed.connect(self.start_measuring)
        self.main_widget.pause_pressed.connect(self.timer.stop)
        self.main_widget.stop_pressed.connect(self.finish_session)
        self.main_widget.update_calib_pressed.connect(self.update_calibs)
        self.viewer.units_changed.connect(self.viewer.update_plotter)
        self.viewer.calib_probs_check_box.stateChanged.connect(self.viewer.update_plotter)
        self.viewer.calib_freq_spin_box.valueChanged.connect(self.viewer.update_plotter)
        self.new_session_widget.updade_sensors_button.pressed.connect(self.check_connection)
        self.new_session_widget.session_inited.connect(self.init_new_session)
        self.center()

        self.device_ports: list[int] = []

        self.session_start_datetime: datetime = datetime.now()

    def open_viewer(self) -> None:
        if result_path := open_file_system(True):
            self.viewer.show()
            self.viewer.load_session(Path(result_path), self.device.calibrator)

    def calibrate_measures(self, state: bool) -> None:
        if state:
            self.device.recalibrate_df(self.main_widget.calib_freq_spin_box.value() * 1e6)
        else:
            self.device.recalibrate_df(None)

    def update_calibs(self) -> None:
        try:
            calib_path = Path(self.main_widget.calib_path_line_edit.text())
            self.device.update_calibrator(calib_path)
            self.viewer.update_calibrator(self.device.calibrator)
            self.config.settings.calibration_path = calib_path
            self.config.write_config()
            QMessageBox.information(self, 'Обновление калибровок',
                                    'Калибровки успешно обновлены',
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
        except (KeyError, ValueError, OSError) as err:
            QMessageBox.critical(self, 'Обновление калибровок',
                        'Не удалось обновить калибровки\n'\
                        'Возможно, указан неправильный путь',
                        QMessageBox.StandardButton.Ok,
                        QMessageBox.StandardButton.Ok)
            logger.error(err)

    def init_new_session(self, output_path: str) -> None:
        logger.info(f'Session output: {output_path}')
        labels: list[str] = self.new_session_widget.checked_text()
        self.main_widget.to_initial_state(labels)
        description: str = self.new_session_widget.session_comment_editor.toPlainText()
        Path.mkdir(Path(output_path), exist_ok=True)
        file_path: Path = Path(output_path).joinpath('description.txt')
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(description)
        self.device.set_output_path(Path(output_path))
        self.session_start_datetime = datetime.now()
        status_bar: QtWidgets.QStatusBar | None = self.statusBar()
        timestamp: str = self.session_start_datetime.isoformat(" ", "seconds")
        if status_bar:
            status_bar.showMessage(f'Начало сеанса {timestamp}')

    def start_measuring(self) -> None:
        if not self.device.connection_status:
            ports: list[int] = [probe.port for probe in self.device.probes
                                if probe.probe_id in self.new_session_widget.checked_text()]
            self.device.connect(self.config.settings.ip, ports)
        self.timer.start(int(self.main_widget.plotter_interval_spin_box.value() * 1000))

    def finish_session(self) -> None:
        finish_time = datetime.now().isoformat(" ", "seconds")
        self.device.disconnect()
        self.timer.stop()
        self.main_widget.to_finish_state()
        self.device.clear_data()
        sesssions_folder = Path(self.new_session_widget.path_line_edit.text())
        filename: str = self.new_session_widget.filename_line_edit.text()
        str_path = str(sesssions_folder.joinpath(filename))
        msg: str = f"Данные по этому сеансу находятся в папке\n{str_path}"
        QMessageBox.information(self, 'Сеанс завершен', msg,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)
        status_bar: QtWidgets.QStatusBar | None = self.statusBar()
        timestamp: str = self.session_start_datetime.isoformat(" ", "seconds")
        if status_bar:
            status_bar.showMessage(f'Начало сеанса: {timestamp}; '\
                                   f'Конец сеанса: {finish_time}')
        print('session finished')

    def check_connection(self) -> None:
        probes = self.device.get_connected()
        self.config.settings.alive_sensors = [probe.probe_id for probe in probes]
        self.new_session_widget.clear_checbox_list()
        [self.new_session_widget.add_sensors(probe.probe_id) for probe in probes]

    def close(self) -> None:
        super().close()
        self.viewer.close()
        self.new_session_widget.close()
        self.settings_widget.close()
        print('close')

    def center(self) -> None:
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            center_point = screen.geometry().center()
            frameGm.moveCenter(center_point)
            self.move(frameGm.topLeft())

    def _plot_process(self) -> None:
        if not self.device.connection_status:
            logger.debug('device not connected')
            return
        calib_flag: bool = self.main_widget.calib_probs_check_box.isChecked()
        freq: float | None = self.main_widget.calib_freq_spin_box.value() * 1e6 if calib_flag else None
        if calib_flag:
            self.main_widget.calib_dataframes = self.device.get_dataframes(freq)
        else:
            self.main_widget.dataframes = self.device.get_dataframes(freq)
        dataframes = self.device.get_data(self.main_widget.current_units, freq)
        self.main_widget.plotter.plot_df(dataframes)
        self.main_widget.update_minmax_table()


def main() -> None:
    app = QApplication([])
    main_window = MainWindow()
    mw = ModernWindow(main_window)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    mw.show()
    app.exec()


if __name__ == '__main__':
    main()
