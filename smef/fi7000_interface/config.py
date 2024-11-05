
from pathlib import Path
from dynaconf import Dynaconf
from dynaconf import loaders
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils import object_merge
from dynaconf.vendor.ruamel import yaml


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
    def __init__(self, root_path: Path = Path.cwd()) -> None:
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
            images_folder=str(root_path.joinpath('ImagesOutput')),
            calibration_path=str(root_path.joinpath('sensor_calibrations')),
            ports=[4001, 4002, 4003, 4004, 4005],
            output_path=str(root_path.joinpath('sessions')),
            dark_theme=True,
            line_colors={'357217': 'red',
                         '357218': 'blue',
                         '357219': 'orange',
                         '357220': 'brown',
                         '357221': 'gray'},
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