from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
try:
    from .generator_window import *
except Exception as ex:
    from generator_window import *



class GeneratorSettings(QWidget, Ui_generator_settings):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Настройки генератора')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)

    def accept_clicked(self):
        self.close()

    def cancel_clicked(self):
        self.close()