from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton, QGroupBox
from PyQt5.QtGui import QRegExpValidator
from qtpy.uic import loadUi
from smef.fi7000_interface.config import FL7000_Config


class ConnectionsSettings(QWidget):
    update_data_signal = QtCore.pyqtSignal()

    server_ip_line_edit: QLineEdit
    s1_port_line_edit: QLineEdit
    s2_port_line_edit: QLineEdit
    s3_port_line_edit: QLineEdit
    s4_port_line_edit: QLineEdit
    s5_port_line_edit: QLineEdit
    s1_status_label: QLabel
    s2_status_label: QLabel
    s3_status_label: QLabel
    s4_status_label: QLabel
    s5_status_label: QLabel
    accept_button: QPushButton
    cancel_button: QPushButton
    server_ping_button: QPushButton
    generatop_ping_button: QPushButton
    generator_status_label: QLabel
    generator_port_line_edit: QLineEdit
    generator_ip_line_edit: QLineEdit
    generator_groupbox: QGroupBox
    def __init__(self, config: FL7000_Config) -> None:
        super().__init__()

        loadUi(Path(__file__).parent.joinpath('ui', 'connections_settings.ui'), self)
        self.setWindowTitle('Настройки подключения')
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # self.setFixedSize(600, 400)
        self.accept_button.clicked.connect(self.accept_settings)
        self.cancel_button.clicked.connect(self.cancel_btn_slot)

        self.config: FL7000_Config = config

        self.server_ip_line_edit.setText(self.config.settings.ip)
        self.port_lines_edit: list[QLineEdit] = [self.s1_port_line_edit, self.s2_port_line_edit, self.s3_port_line_edit,
                                                 self.s4_port_line_edit, self.s5_port_line_edit]
        [line_edit.setText(str(self.config.settings.ports[i])) for i, line_edit in enumerate(self.port_lines_edit)]
        self.generator_ip_line_edit.setText(self.config.settings.generator_ip)
        self.generator_port_line_edit.setText(str(self.config.settings.generator_port))

        self.status_label_list: list[QLabel] = [self.s1_status_label, self.s2_status_label, self.s3_status_label,
                                                self.s4_status_label, self.s5_status_label]
        [label.setVisible(False) for label in self.status_label_list]
        self.generator_groupbox.setVisible(False)
        [label.setText('Отключен') for label in self.status_label_list]
        self.generator_status_label.setText('Отключен')

        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # Part of the regular expression
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        ip_validator = QRegExpValidator(ip_regex, self)
        self.server_ip_line_edit.setValidator(ip_validator)
        self.generator_ip_line_edit.setValidator(ip_validator)
        self.center()

    def set_connection_status_labels(self, status_list: list[bool]) -> None:
        [label.setText('Отключен' if status is False else 'Подключен')
         for label, status in zip(self.status_label_list, status_list)]

    def get_port_values(self) -> list[int]:
        return [int(line_edit.text()) for line_edit in self.port_lines_edit]

    def accept_settings(self) -> None:
        self.config.settings.ip = self.server_ip_line_edit.text()
        self.config.settings.ports = self.get_port_values()
        self.config.settings.alive_sensors = [True if label.text() == 'Подключен' else False
                                                for label in self.status_label_list]
        self.config.settings.generator_ip = self.generator_ip_line_edit.text()
        self.config.settings.generator_port = int(self.generator_port_line_edit.text() or -1)
        self.config.write_config()
        self.update_data_signal.emit()
        self.close()

    def cancel_btn_slot(self) -> None:
        self.close()

    def center(self):
        frameGm = self.frameGeometry()
        screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        centerPoint = QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

if __name__ == '__main__':
    app = QApplication([])
    window = ConnectionsSettings(FL7000_Config())
    window.show()
    app.exec_()
