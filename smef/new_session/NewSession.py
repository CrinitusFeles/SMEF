import os
import time
from PyQt5 import QtWidgets, QtCore
from qtpy.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from smef.app_logger import get_logger
from PyQt5.QtWidgets import QWidget, QMessageBox
from smef.fi7000_interface.config import load_config
from smef.fi7000_interface.config import open_file_system, default_config, create_config
logger = get_logger(__name__)


class NewSession(QWidget):
    request_probe_list = QtCore.pyqtSignal()
    session_inited = QtCore.pyqtSignal(str)

    def __init__(self, config: dict | None = None):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'new_session_window.ui'), self)
        self.setWindowTitle('Новый сеанс')
        self.config = config or {}
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # ----- Connections -----
        self.path_tool_button.pressed.connect(self.path_tool_button_pressed)
        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)
        self.generate_name_button.pressed.connect(self.generate_name)
        # =========================
        self.path_line_edit.setText(self.config.get('last_output_path', os.getcwd()))

        self.check_box_list = [self.s1_checkbox, self.s2_checkbox, self.s3_checkbox, self.s4_checkbox, self.s5_checkbox]
        [checkbox.setChecked(self.config['connected_sensors'][i]) for i, checkbox in enumerate(self.check_box_list)]
        self.set_checkbox_enabled(self.config['alive_sensors'])

        self.generate_name()

        self.inited_session_flag = False

    def set_checkbox_enabled(self, alive_sensors: list[bool]):
        for i, checkbox in enumerate(self.check_box_list):
            if not alive_sensors[i]:
                checkbox.setEnabled(False)
                checkbox.setChecked(False)
            else:
                checkbox.setEnabled(True)

    def get_checkbox_values(self) -> list[bool]:
        return [checkbox.isChecked() for checkbox in self.check_box_list]

    def accept_clicked(self) -> None:
        if self.config is None:
            self.config = load_config('config', default_config)

        self.config['connected_sensors'] = self.get_checkbox_values()

        if self.path_line_edit.text() != '':
            if not os.path.isdir(self.path_line_edit.text()):
                logger.info('Create new output folder ' + self.path_line_edit.text())
                os.makedirs(self.path_line_edit.text(), exist_ok=True)
            if self.filename_line_edit.text() != '':
                if True in self.get_checkbox_values():
                    self.inited_session_flag = True
                    create_config(self.config['name'], self.config)
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
        self.path_line_edit.setText(open_file_system(directory=True))
        self.config['last_output_path'] = self.path_line_edit.text()

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
