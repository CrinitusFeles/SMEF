from __future__ import annotations
import os
from pathlib import Path
import sys
import subprocess

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QFileDialog
from qtmodern.windows import ModernWindow

from smef.fi7000_interface.config import FL7000_Config
from smef.client.viewer import Viewer


def execFile(file: Path) -> None:
    print(sys.platform)
    if sys.platform == 'linux':
        subprocess.call(["xdg-open", file])
    else:
        os.startfile(file)

class MainWidget(Viewer):
    start_pressed: QtCore.pyqtSignal = pyqtSignal()
    stop_pressed: QtCore.pyqtSignal = pyqtSignal()
    pause_pressed: QtCore.pyqtSignal = pyqtSignal()
    update_calib_pressed: QtCore.pyqtSignal = pyqtSignal()

    dark_theme_checkbox: QtWidgets.QCheckBox
    calib_path_line_edit: QtWidgets.QLineEdit

    new_session_button: QtWidgets.QPushButton
    update_calib_button: QtWidgets.QPushButton
    open_session_viewer_button: QtWidgets.QPushButton
    connection_settings_button: QtWidgets.QPushButton
    plotter_start_button: QtWidgets.QPushButton
    plotter_stop_button: QtWidgets.QPushButton

    slide_window_time_spinbox: QtWidgets.QSpinBox
    plotter_interval_spin_box: QtWidgets.QSpinBox
    sliding_window_groupbox: QtWidgets.QGroupBox
    def __init__(self, config: FL7000_Config) -> None:
        super().__init__(config, 'mainwidget.ui')
        self.dark_theme_checkbox.stateChanged.connect(self.change_theme)
        self.plotter_start_button.pressed.connect(self.start_measuring)
        self.plotter_stop_button.pressed.connect(self.stop_measuring)
        self.sliding_window_groupbox.setVisible(False)
        self.slide_window_time_spinbox.valueChanged.connect(
            lambda size: self.plotter.set_sliding_window_size(size * 3600))
        self.calib_path_line_edit.setText(self.config.settings.calibration_path)

    def on_choose_calib_folder_button_pressed(self):
        title = 'Choose folder'
        folder_path: str = self.calib_path_line_edit.text()
        options = QtWidgets.QFileDialog.Option.DontUseNativeDialog
        options |= QtWidgets.QFileDialog.Option.ShowDirsOnly
        calib_path: str = QFileDialog.getExistingDirectory(self, title,
                                                           folder_path, options)
        self.calib_path_line_edit.setText(calib_path)

    def on_open_calib_button_pressed(self):
        dir_path = Path(self.calib_path_line_edit.text())
        try:
            execFile(dir_path)
        except FileNotFoundError:
            msg = f'Невозможно открыть директорию по указанному пути:\n{dir_path}'
            QtWidgets.QMessageBox.critical(self, 'Ошибка!', msg)

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

    def on_update_calib_button_pressed(self):
        self.update_calib_pressed.emit()

    def change_theme(self, state: bool) -> None:
        super().change_theme(state)
        self.dark_theme_checkbox.setChecked(state)

    def to_initial_state(self, labels: list[str]):
        self.plotter.delete_all_data()
        self.plotter_start_button.setEnabled(True)
        self.new_session_button.setEnabled(False)
        # [self.plotter.add_data_line(f'Датчик {label}') for label in labels]
        [self.plotter.add_data_line(label) for label in labels]
        self.plotter.auto_scale()

    def to_finish_state(self):
        self.new_session_button.setEnabled(True)
        self.plotter_start_button.setEnabled(False)
        self.plotter_stop_button.setEnabled(False)

if __name__ == '__main__':
    app = QApplication([])
    config = FL7000_Config()
    main_window = MainWidget(config)
    mw = ModernWindow(main_window)
    mw.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)  # fix flickering on resize window
    mw.show()
    app.exec()
