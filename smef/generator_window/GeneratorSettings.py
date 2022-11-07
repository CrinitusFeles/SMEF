import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from qtpy.uic import loadUi

try:
    from smef.generator_window import *
except Exception as ex:
    from generator_window import *



class GeneratorSettings(QWidget):
    def __init__(self):
        super().__init__()
        loadUi(os.path.join(os.path.dirname(__file__), 'generator_window.ui'), self)
        self.setWindowTitle('Настройки генератора')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)

    def accept_clicked(self):
        self.close()

    def cancel_clicked(self):
        self.close()