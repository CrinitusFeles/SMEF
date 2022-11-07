import os

from PyQt5 import QtCore
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QRegExpValidator
from qtmodern.windows import ModernWindow
from qtpy.uic import loadUi

from smef.app_logger import get_logger

logger = get_logger(__name__)


class ConnectionsSettings(QWidget):
    update_data_signal = QtCore.pyqtSignal(dict)

    def __init__(self, config: dict = None):
        super().__init__()

        loadUi(os.path.join(os.path.dirname(__file__), 'connections_settings.ui'), self)
        self.setWindowTitle('Настройки подключения')
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.groupBox.hide()      
        self.setFixedSize(600, 400)
        self.accept_button.clicked.connect(self.accept_settings)
        self.cancel_button.clicked.connect(self.close)

        self.config = config  # 🔌 🚫
        if self.config is not None:
            self.server_ip_line_edit.setText(self.config['device_ip'])
            self.s1_port_line_edit.setText(str(self.config['ports'][0]))
            self.s2_port_line_edit.setText(str(self.config['ports'][1]))
            self.s3_port_line_edit.setText(str(self.config['ports'][2]))
            self.s4_port_line_edit.setText(str(self.config['ports'][3]))
            self.s5_port_line_edit.setText(str(self.config['ports'][4]))
            self.generator_ip_line_edit.setText(self.config['generator_ip'])
            self.generator_port_line_edit.setText(str(self.config['generator_port']))

        self.status_label_list = [self.s1_status_label,
                                  self.s2_status_label,
                                  self.s3_status_label,
                                  self.s4_status_label,
                                  self.s5_status_label]
        [label.setText('Отключен') for label in self.status_label_list]
        self.generator_status_label.setText('Отключен')

        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # Part of the regular expression
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        ip_validator = QRegExpValidator(ip_regex, self)
        self.server_ip_line_edit.setValidator(ip_validator)
        self.generator_ip_line_edit.setValidator(ip_validator)

    def set_connection_status_labels(self, status_list: list[bool]):
        [label.setText('Отключен' if status is False else 'Подключен') for label, status in zip(self.status_label_list, status_list)]

    def get_port_values(self):
        return [int(self.s1_port_line_edit.text()),
                int(self.s2_port_line_edit.text()),
                int(self.s3_port_line_edit.text()),
                int(self.s4_port_line_edit.text()),
                int(self.s5_port_line_edit.text())]

    def accept_settings(self):
        self.config['device_ip'] = self.server_ip_line_edit.text()
        self.config['ports'] = self.get_port_values()
        self.config['alive_sensors'] = [True if label.text() == 'Подключен' else False for label in self.status_label_list]
        self.config['generator_ip'] = self.generator_ip_line_edit.text() if self.generator_ip_line_edit.text() != '' else None
        self.config['generator_port'] = int(self.generator_port_line_edit.text()) if self.generator_port_line_edit.text() != '' else None
        self.update_data_signal.emit(self.config)
        self.close()


if __name__ == '__main__':
    app = QApplication([])
    window = ConnectionsSettings()
    window.show()
    app.exec_()
