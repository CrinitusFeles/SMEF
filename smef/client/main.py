
from __future__ import annotations

from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow
from qtmodern.windows import ModernWindow
from qtpy.uic import loadUi
from smef.client.settings_widget import ConnectionsSettings

from smef.fi7000_interface.config import FL7000_Config
from smef.fi7000_interface.fl7000_driver import FL7000_Interface
from smef.client.main_widget import MainWidget
from smef.client.viewer import Viewer
from smef.client.new_session import NewSession
from loguru import logger
from PyQt5.QtWidgets import QApplication
from smef.utils import open_file_system

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('ui', 'main.ui'), self)
        self.setWindowTitle('СМЭП Клиент v2.1.0')
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
        self.main_widget.open_session_viewer_button.pressed.connect(self.open_viewer)
        self.main_widget.connection_settings_button.pressed.connect(self.settings_widget.show)
        self.main_widget.plotter_interval_spin_box.valueChanged.connect(self.device.set_measuring_period)
        self.main_widget.units_changed.connect(self._plot_process)
        self.main_widget.plotter_interval_spin_box.valueChanged.connect(
            lambda period: self.timer.setInterval(int(period * 1000)))
        self.main_widget.start_pressed.connect(self.start_measuring)
        self.main_widget.pause_pressed.connect(self.timer.stop)
        self.main_widget.stop_pressed.connect(self.finish_session)
        self.new_session_widget.updade_sensors_button.pressed.connect(self.check_connection)
        self.new_session_widget.session_inited.connect(self.init_new_session)
        self.new_session_widget.calibrations_check_btn.pressed.connect(self.check_calibrations)
        self.center()

        self.device_ports: list[int] = []

    def open_viewer(self) -> None:
        if result_path := open_file_system():
            self.viewer.plotter.read_file(result_path)
            self.viewer.show()

    def init_new_session(self, output_path: str) -> None:
        logger.info(f'Session output: {output_path}')
        labels: list[str] = self.new_session_widget.get_checked_text()
        self.main_widget.plotter.delete_all_data()
        self.main_widget.plotter_start_button.setEnabled(True)
        self.main_widget.new_session_button.setEnabled(False)
        # self.main_widget.plotter_stop_button.setEnabled(True)
        colors: list[str] = ['red', 'blue', 'orange', 'brown', 'gray']
        for i, label in enumerate(labels):
            self.main_widget.plotter.add_data_line(f'Датчик {label}', colors[i])

    def start_measuring(self):
        if not self.device.connection_status:
            self.device.connect(self.config.settings.ip, [probe.port for probe in self.device.probes
                                                          if probe.probe_id in self.new_session_widget.get_checked_text()])
        self.timer.start(int(self.main_widget.plotter_interval_spin_box.value() * 1000))

    def finish_session(self) -> None:
        self.device.disconnect()
        self.device.clear_data()
        self.timer.stop()
        self.main_widget.new_session_button.setEnabled(True)
        self.main_widget.plotter_start_button.setEnabled(False)
        self.main_widget.plotter_stop_button.setEnabled(False)
        print('session finished')

    def check_connection(self) -> None:
        probes = self.device.get_connected()
        self.config.settings.alive_sensors = [probe.probe_id for probe in probes]
        [self.new_session_widget.add_sensors(probe.probe_id) for probe in probes]

    def close(self):
        super().close()
        print('close')

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.desktop().screenNumber(QtWidgets.QApplication.desktop().cursor().pos())
        centerPoint = QtWidgets.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

    def _plot_process(self) -> None:
        if self.device.df.size:
            self.main_widget.plotter.dataframe = self.device.df
            self.main_widget.plotter.plot_df(self.device.get_data(self.main_widget.current_units))

            # self.main_widget.plotter.update_plot_data(np.array([random.random() * 5 + 50, random.random() + 1,
            #                                         random.random() * 2 + 3]))
            self.main_widget.update_minmax_table()

    def check_calibrations(self):
        status_list = self.new_session_widget.get_checkbox_values()

if __name__ == '__main__':
    app = QApplication([])
    main_window = MainWindow()
    mw = ModernWindow(main_window)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    mw.show()
    app.exec_()