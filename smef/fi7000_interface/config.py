from __future__ import annotations
import os
from typing import Any, Optional
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from qtmodern.windows import ModernWindow
from ruamel.yaml import YAML, round_trip_dump

default_config = {
    'name': 'config',
    'device_ip': '10.6.1.95',
    'ports': [4001, 4002, 4003, 4004, 4005],
    'connected_sensors': [False, False, False, False, False],
    'alive_sensors': [False, False, False, False, False],
    'dark_theme': False,
    'units': 'В/м',
    'norma_check': False,
    'norma_value': 0,
    'measure_period': 1,
    'plot_header': '',
    'slide_window_time_h': 1,
    'last_output_path': '',
    'generator_ip': '',
    'generator_port': 8080,
    'right_axis': None,
    'left_axis': {
        'label': 'Напряженность поля',
        'units': None,
        'legend_label': ''
    },
    'bottom_axis': {
        'label': 'Время',
        'units': None
    },
    'top_axis': {
        'label': '',
        'units': ''
    },
    'anim_period': 1000,
    'theme': 'dark',
    'style': {
        'dark': {
            'plot_background_color': '#232323',
            'frame_background_color': '#353535',
            'legend_background': '14141420',
            'legend_boundary': 'k',
            'axis_labels_color': '#AAAAAA',
            'crosshair_color': '#6bcd99',
            'norma_line_color': '#603f9f'
        },
        'light': {
            'plot_background_color': '#FFFFFF',
            'frame_background_color': '#EEEEEE',
            'legend_background': '#FFFFFF30',
            'legend_boundary': '#AAAAAA',
            'axis_labels_color': '#555555',
            'crosshair_color': '#6bcd99',
            'norma_line_color':  '#603f9f'
        }
    },
    'image_folder': './Images/',
    'session_folder': './Output/',  # uses only at first start of application for creating session folder
}


def load_config(name: str, default_config: Any):
    config_folder_path = 'Config'
    config_path = os.path.join(config_folder_path, f'{name}.yaml')
    if not os.path.isdir(config_folder_path):
        os.makedirs(config_folder_path, exist_ok=True)
    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding="utf-8") as config_file:
            config_obj = YAML().load(config_file)
            if config_obj != {}:
                return config_obj
            else:
                return create_config(name, default_config)
    else:
        return create_config(name, default_config)


def create_config(name: str, config_obj: Any):
    config_path = os.path.join('Config', f'{name}.yaml')
    with open(config_path, 'w', encoding="utf-8") as ofp:
        round_trip_dump(config_obj, ofp, indent=4, block_seq_indent=2)
    return config_obj


def open_file_system(directory=False) -> Optional[list[str] | str]:
    dialog = QtWidgets.QFileDialog()
    dialog.setWindowTitle('Choose Directories')
    dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    if directory:
        dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        return str(dialog.selectedFiles()[0])

    dialog.deleteLater()
