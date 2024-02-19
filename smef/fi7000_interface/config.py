
from importlib.abc import Loader
from pathlib import Path
from dynaconf import Dynaconf
from dynaconf import loaders
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils import object_merge
from dynaconf.vendor.ruamel import yaml

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
            'legend_background': '#14141420',
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



def my_write(settings_path, settings_data, merge=True):
    """Write data to a settings file.

    :param settings_path: the filepath
    :param settings_data: a dictionary with data
    :param merge: boolean if existing file should be merged with new data
    :param stdout: boolean if should output to stdout instead of file
    """
    settings_path = Path(settings_path)
    if settings_path.exists() and merge:  # pragma: no cover
        with open(str(settings_path), encoding='utf-8') as open_file:
            object_merge(yaml.load(open_file, Loader=yaml.UnsafeLoader), settings_data)

    with open(str(settings_path), "w", encoding='utf-8') as open_file:
        yaml.dump(
            settings_data,
            open_file,
            explicit_start=True,
            indent=4,
            block_seq_indent=2,
            allow_unicode=True,
            default_flow_style=False,
        )
loaders.yaml_loader.write = my_write

class FL7000_Config:
    def __init__(self, root_path: str | Path = Path(__file__).parent) -> None:
        self.config_path = root_path
        self.settings = Dynaconf(
            root_path=root_path,
            envvar_prefix="DYNACONF",
            encoding='utf-8',
            settings_files=['settings.yaml'],
            ip='10.6.1.95',
            generator_ip='10.6.1.95',
            generator_port='8080',
            plotter_title='',
            norma_color='purple',
            alive_sensors=[False]*5,
            images_folder=str(Path(__file__).parent.joinpath('ImagesOutput')),
            calibration_path=str(Path(__file__).parent.parent.joinpath('sensor_calibrations')),
            ports=[4001, 4002, 4003, 4004, 4005],
            output_path=str(Path.cwd().joinpath('sessions')),
            dark_theme=True,
            line_colors=['red', 'blue', 'orange', 'brown', 'gray'],

        )

    def __call__(self) -> Dynaconf:
        return self.settings

    def write_config(self) -> None:
        p = Path(self.config_path).joinpath('settings.yaml')
        loaders.write(str(p),
                      DynaBox(self.settings.as_dict()).to_dict(),
                      merge=False)




if __name__ == '__main__':
    config = FL7000_Config()
    config.write_config()
    print(config.settings.devices)