
from pathlib import Path
from threading import Thread
from typing import Literal
import pandas as pd
from pandas import DataFrame
from smef.fi7000_interface.calibrations import Calibrator
from smef.fi7000_interface.config import FL7000_Config
from smef.fi7000_interface.fl7040_driver import FL7040_Probe

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 370)

class FL7000_Interface:
    def __init__(self, config: FL7000_Config) -> None:
        self.config: FL7000_Config = config
        self.probes: list[FL7040_Probe] = [FL7040_Probe(self.config.settings.ip, port)
                                           for port in self.config.settings.ports]
        self.calibrator: Calibrator = Calibrator(Path(self.config.settings.calibration_path))
        self.connection_status: bool = False
        self._measure_period_sec: float = 1.0
        self._units: list[Literal['В/м', 'дБмкВ/м', 'Вт/м²']] = ['В/м', 'дБмкВ/м', 'Вт/м²']
        self._current_units: Literal['В/м', 'дБмкВ/м', 'Вт/м²'] = 'В/м'

    def get_connected_probes(self) -> list[FL7040_Probe]:
        return [probe for probe in self.probes if probe.connection_status]

    def set_output_path(self, path: Path) -> None:
        [probe.set_output_path(path) for probe in self.probes]

    def get_probe(self, probe_id: str) -> FL7040_Probe | None:
        probe: list[FL7040_Probe] = [probe for probe in self.probes if probe.probe_id == probe_id]
        return probe[0] if len(probe) else None

    def get_data(self, units: int, freq: float | None = None) -> list[DataFrame]:
        self._current_units = self._units[units]
        dataframes: list[DataFrame] = [probe.get_df_data(freq) for probe in self.get_connected_probes()]
        return [df.iloc[:, [0, 4 + units]] for df in dataframes]

    def get_dataframes(self, freq: float | None = None) -> list[DataFrame]:
        return [probe.get_df_data(freq) for probe in self.get_connected_probes()]

    def recalibrate_df(self, freq: float) -> None:
        for probe in self.get_connected_probes():
            if probe.calibrator:
                probe.calibration_freq = freq
                df = probe.calibrator.calibrate_dataframe(freq, probe.df)
                probe.df_calib = df

    def set_measuring_period(self, period_sec: float) -> None:
        self._measure_period_sec = period_sec
        [probe.set_measure_period(period_sec) for probe in self.probes]

    @staticmethod
    def _fast_connect(probes: list[FL7040_Probe]) -> None:
        threads: list[Thread] = [Thread(target=probe.connect_device, daemon=True) for probe in probes]
        [thread.start() for thread in threads]
        [thread.join(2) for thread in threads]

    def get_connected(self) -> list[FL7040_Probe]:
        self._fast_connect(self.probes)
        result: list[FL7040_Probe] = self.get_connected_probes()
        [probe.disconnect() for probe in self.probes]
        return result

    def connect(self, ip: str, ports: list[int]) -> bool:
        if self.connection_status:
            return True
        unchecked_ports: list[int] = [port for port in ports if port not in self.config.settings.ports]
        self.probes.extend([FL7040_Probe(ip, port) for port in unchecked_ports])
        self._fast_connect([probe for probe in self.probes if probe.port in ports])
        self.connection_status = True
        [probe.calibrate_probe(self.calibrator(probe.probe_id)) for probe in self.get_connected_probes()]
        [probe.start_measuring() for probe in self.get_connected_probes()]
        return all([probe.connection_status for probe in self.probes])

    def disconnect(self):
        [probe.disconnect() for probe in self.get_connected_probes()]
        self.connection_status = False

    def clear_data(self):
        [probe.clear_data() for probe in self.probes]

if __name__ == '__main__':
    device = FL7000_Interface(FL7000_Config())
    print(device.connect('10.6.1.95', [4001, 4003]))
    device.set_measuring_period(1)
    try:
        while True:
            in_data = input('>')
    except KeyboardInterrupt:
        print('x_x')