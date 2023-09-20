from pathlib import Path
import time
from PyQt5 import QtWidgets, QtCore
from qtpy.uic import loadUi

from PyQt5.QtWidgets import QWidget, QMessageBox
from smef.fi7000_interface.config import FL7000_Config
from loguru import logger
from smef.utils import open_file_system

class NewSession(QWidget):
    request_probe_list = QtCore.pyqtSignal()
    session_inited = QtCore.pyqtSignal(str)

    s1_checkbox: QtWidgets.QCheckBox
    s2_checkbox: QtWidgets.QCheckBox
    s3_checkbox: QtWidgets.QCheckBox
    s4_checkbox: QtWidgets.QCheckBox
    s5_checkbox: QtWidgets.QCheckBox
    updtade_sensors_button: QtWidgets.QPushButton
    generate_name_button: QtWidgets.QPushButton
    path_tool_button: QtWidgets.QToolButton
    accept_button: QtWidgets.QPushButton
    cancel_button: QtWidgets.QPushButton
    session_comment_editor: QtWidgets.QTextBrowser
    path_line_edit: QtWidgets.QLineEdit
    filename_line_edit: QtWidgets.QLineEdit
    def __init__(self, config: FL7000_Config | None = None, alive_sensors: list[bool] | None = None):
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('new_session_window.ui'), self)
        self.setWindowTitle('Новый сеанс')
        self.config: FL7000_Config = config or FL7000_Config()
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # ----- Connections -----
        self.path_tool_button.pressed.connect(self.path_tool_button_pressed)
        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)
        self.generate_name_button.pressed.connect(self.generate_name)
        # =========================
        self.path_line_edit.setText(str(self.config.settings.last_output_path))

        self.check_boxes: list[QtWidgets.QCheckBox] = [self.s1_checkbox, self.s2_checkbox, self.s3_checkbox,
                                                       self.s4_checkbox, self.s5_checkbox]
        # [checkbox.setChecked(self.config['connected_sensors'][i]) for i, checkbox in enumerate(self.check_box_list)]
        _alive_sensors: list[bool] = alive_sensors or [False] * 5
        self.set_checkbox_enabled(_alive_sensors)

        self.generate_name()

        self.inited_session_flag = False

    def set_checkbox_enabled(self, alive_sensors: list[bool]):
        for i, checkbox in enumerate(self.check_boxes):
            if not alive_sensors[i]:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            else:
                checkbox.setEnabled(True)

    def get_checkbox_values(self) -> list[bool]:
        return [checkbox.isChecked() for checkbox in self.check_boxes]

    def accept_clicked(self) -> None:
        if self.path_line_edit.text() != '':
            if not Path(self.path_line_edit.text()).is_dir():
                logger.info('Create new output folder ' + self.path_line_edit.text())
                Path(self.path_line_edit.text()).mkdir(exist_ok=True)
            if self.filename_line_edit.text() != '':
                if any(self.get_checkbox_values()):
                    self.inited_session_flag = True
                    self.session_inited.emit(self.path_line_edit.text() + '/' + self.filename_line_edit.text() + '.csv')
                    self.close()
                else:
                    QMessageBox.warning(self, 'Warning', "Хотя бы один из датчиков должен быть подключен.",
                                        QMessageBox.Ok, QMessageBox.Ok)
            else:
                QMessageBox.warning(self, 'Warning', "Укажите название сеанса.", QMessageBox.Ok, QMessageBox.Ok)
        else:
            QMessageBox.warning(self, 'Warning', "Укажите путь к папке с сессией.", QMessageBox.Ok, QMessageBox.Ok)

    def path_tool_button_pressed(self) -> None:
        path: str | None = open_file_system(directory=True)
        if path:
            self.path_line_edit.setText(path)
            self.config.settings.last_output_path = self.path_line_edit.text()
            self.config.write_config()

    def cancel_clicked(self) -> None:
        logger.info('Cancel button clicked')
        self.close()

    def generate_name(self) -> None:
        self.filename_line_edit.setText(time.strftime("%Y-%m-%d_%H.%M", time.localtime()))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = NewSession()
    window.show()
    app.exec_()
