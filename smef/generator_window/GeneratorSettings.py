from pathlib import Path

from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import Qt
from qtpy.uic import loadUi

class GeneratorSettings(QWidget):
    accept_button: QPushButton
    cancel_button: QPushButton
    def __init__(self) -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('ui', 'generator_window.ui'), self)
        self.setWindowTitle('Настройки генератора')
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

        self.accept_button.pressed.connect(self.accept_clicked)
        self.cancel_button.pressed.connect(self.cancel_clicked)

    def accept_clicked(self) -> None:
        self.close()

    def cancel_clicked(self) -> None:
        self.close()