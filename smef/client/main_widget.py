from __future__ import annotations

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication
from qtmodern.windows import ModernWindow

from smef.fi7000_interface.config import FL7000_Config
from smef.client.viewer import Viewer


class MainWidget(Viewer):
    start_pressed: QtCore.pyqtSignal = pyqtSignal()
    stop_pressed: QtCore.pyqtSignal = pyqtSignal()
    pause_pressed: QtCore.pyqtSignal = pyqtSignal()

    dark_theme_checkbox: QtWidgets.QCheckBox

    new_session_button: QtWidgets.QPushButton
    open_session_viewer_button: QtWidgets.QPushButton
    connection_settings_button: QtWidgets.QPushButton
    plotter_start_button: QtWidgets.QPushButton
    plotter_stop_button: QtWidgets.QPushButton

    slide_window_time_spinbox: QtWidgets.QSpinBox
    plotter_interval_spin_box: QtWidgets.QSpinBox
    def __init__(self, config: FL7000_Config) -> None:
        super().__init__(config, 'mainwidget.ui')
        self.dark_theme_checkbox.stateChanged.connect(self.change_theme)
        self.plotter_start_button.pressed.connect(self.start_measuring)
        self.plotter_stop_button.pressed.connect(self.stop_measuring)
        self.slide_window_time_spinbox.valueChanged.connect(
            lambda size: self.plotter.set_sliding_window_size(size * 3600))

    def start_measuring(self) -> None:
        if self.plotter_start_button.text() == 'Старт':
            self.plotter_start_button.setText('Пауза')
            self.plotter_stop_button.setEnabled(True)
            self.plotter.auto_scale()
            self.start_pressed.emit()
        elif self.plotter_start_button.text() == 'Пауза':
            self.plotter_start_button.setText('Старт')
            self.pause_pressed.emit()

    def stop_measuring(self) -> None:
        self.plotter_start_button.setText('Старт')
        self.stop_pressed.emit()

    def change_theme(self, state: bool) -> None:
        super().change_theme(state)
        self.dark_theme_checkbox.setChecked(state)


if __name__ == '__main__':
    app = QApplication([])
    config = FL7000_Config()
    main_window = MainWidget(config)
    mw = ModernWindow(main_window)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    mw.show()
    app.exec_()
