from pathlib import Path
import time
from PyQt6 import QtWidgets, QtCore
from qtpy.uic import loadUi

from PyQt6.QtWidgets import QWidget, QMessageBox
from smef.fi7000_interface.config import FL7000_Config
from loguru import logger
from smef.utils import open_file_system

class NewSession(QWidget):
    session_inited = QtCore.pyqtSignal(str)

    updade_sensors_button: QtWidgets.QPushButton
    generate_name_button: QtWidgets.QPushButton

    path_tool_button: QtWidgets.QToolButton

    accept_button: QtWidgets.QPushButton
    cancel_button: QtWidgets.QPushButton
    session_comment_editor: QtWidgets.QTextBrowser
    path_line_edit: QtWidgets.QLineEdit
    filename_line_edit: QtWidgets.QLineEdit

    sensors_scroll_area: QtWidgets.QScrollArea
    scroll_layout: QtWidgets.QVBoxLayout

    def __init__(self, config: FL7000_Config | None = None) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('ui', 'new_session_window.ui'), self)
        self.setWindowTitle('Новый сеанс')
        self.config: FL7000_Config = config or FL7000_Config()
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # ----- Connections -----
        self.path_tool_button.pressed.connect(self.path_tool_button_pressed)
        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)
        self.generate_name_button.pressed.connect(self.generate_name)
        # =========================
        self.path_line_edit.setText(str(self.config.settings.output_path))

        self.check_boxes: list[QtWidgets.QCheckBox] = []
        # [checkbox.setChecked(self.config['connected_sensors'][i]) for i, checkbox in enumerate(self.check_box_list)]
        self.set_checkbox_enabled(self.config.settings.alive_sensors)

        self.generate_name()

        self.inited_session_flag = False
        self.center()

    def set_checkbox_enabled(self, alive_sensors: list[bool]) -> None:
        for i, checkbox in enumerate(self.check_boxes):
            if not alive_sensors[i]:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            else:
                checkbox.setEnabled(True)

    def get_checkbox_values(self) -> list[bool]:
        return [checkbox.isChecked() for checkbox in self.check_boxes]

    def checked_text(self) -> list[str]:
        # return [checkbox.text().split(' ')[-1] for checkbox in self.check_boxes if checkbox.isChecked()]
        return [checkbox.text() for checkbox in self.check_boxes if checkbox.isChecked()]

    def accept_clicked(self) -> None:
        ok_btn = QMessageBox.StandardButton.Ok
        if self.path_line_edit.text() != '':
            session_path: Path = Path(self.path_line_edit.text()).joinpath(self.filename_line_edit.text())
            if not Path(self.path_line_edit.text()).is_dir():
                logger.info(f'Creating new output folder {self.path_line_edit.text()}')
                Path(self.path_line_edit.text()).mkdir(exist_ok=True)
            if self.filename_line_edit.text() != '':
                if any(self.get_checkbox_values()):
                    self.inited_session_flag = True
                    self.session_inited.emit(str(session_path))
                    self.close()
                else:
                    msg: str = "Хотя бы один из датчиков должен быть подключен."
                    QMessageBox.warning(self, 'Warning', msg, ok_btn, ok_btn)
            else:
                msg = "Укажите название сеанса."
                QMessageBox.warning(self, 'Warning', msg, ok_btn, ok_btn)
        else:
            msg = "Укажите путь к папке с сессией."
            QMessageBox.warning(self, 'Warning', msg, ok_btn, ok_btn)

    def path_tool_button_pressed(self) -> None:
        path: str | None = open_file_system(directory=True)
        if path:
            self.path_line_edit.setText(path)
            self.config.settings.output_path = self.path_line_edit.text()
            self.config.write_config()

    def add_sensors(self, sensor_id: str) -> None:
        checkbox = QtWidgets.QCheckBox()
        checkbox.setText(sensor_id)
        self.check_boxes.append(checkbox)
        self.scroll_layout.addWidget(checkbox)

    def clear_checbox_list(self):
        [checkbox.deleteLater() for checkbox in self.check_boxes]
        self.check_boxes.clear()

    def cancel_clicked(self) -> None:
        logger.info('Cancel button clicked')
        self.close()

    def generate_name(self) -> None:
        self.filename_line_edit.setText(time.strftime("%Y-%m-%d_%H.%M",
                                                      time.localtime()))

    def center(self) -> None:
        frameGm = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            center_point = screen.geometry().center()
            frameGm.moveCenter(center_point)
            self.move(frameGm.topLeft())

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NewSession()
    [window.add_sensors('i') for _ in range(20)]
    window.show()
    app.exec()
