import subprocess
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
from .connections_settings import *
from PyQt5.QtGui import QRegExpValidator
from .app_logger import *

logger = get_logger(__name__)


class ConnectionsSettings(QWidget, Ui_connections_settings):
    def __init__(self, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Настройки соединения')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.server_ip_line_edit.setText(kwargs.get('server_ip', 'localhost'))
        self.s1_port_line_edit.setText(str(kwargs.get('s1_port', 4001)))
        self.s2_port_line_edit.setText(str(kwargs.get('s2_port', 4002)))
        self.s3_port_line_edit.setText(str(kwargs.get('s3_port', 4003)))
        self.s4_port_line_edit.setText(str(kwargs.get('s4_port', 4004)))
        self.s5_port_line_edit.setText(str(kwargs.get('s5_port', 4005)))
        self.generator_ip_line_edit.setText(kwargs.get('generator_ip', ''))
        self.generator_port_line_edit.setText(str(kwargs.get('generator_port', 0)))

        self.server_ping_button.pressed.connect(self.ping_server)
        self.generatop_ping_button.pressed.connect(self.ping_generator)

        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"  # Part of the regular expression
        # Regulare expression
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        ip_validator = QRegExpValidator(ip_regex, self)
        self.server_ip_line_edit.setValidator(ip_validator)
        self.generator_ip_line_edit.setValidator(ip_validator)

    def ping_server(self):
        ping(self.server_ip_line_edit.text())

    def ping_generator(self):
        ping(self.generator_ip_line_edit.text())


def ping(ip: str):
    out, error = subprocess.Popen(["ping", "-l", "1", ip], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE).communicate()
    answer = out.decode('IBM866')
    if answer[-14:-10] == '100%':
        print('connection lost')
    else:
        print('connection OK')