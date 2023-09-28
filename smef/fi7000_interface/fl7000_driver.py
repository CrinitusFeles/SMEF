
from pathlib import Path
from threading import Thread
import time
from typing import Literal
import pandas as pd
from pandas import DataFrame
from smef.fi7000_interface.config import FL7000_Config
from smef.fi7000_interface.fl7040_driver import FL7040_Probe, FieldResult

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 370)

class FL7000_Interface:
    def __init__(self, config: FL7000_Config) -> None:
        self.config: FL7000_Config = config
        self.probes: list[FL7040_Probe] = [FL7040_Probe(self.config.settings.ip, port)
                                           for port in self.config.settings.ports]
        self._thread: Thread
        self.calibrate_freq: float | None = None
        self.connection_status: bool = False
        self.df = DataFrame()
        self.measure_period_sec: float = 1.0
        self._running_flag: bool = False
        self.units: list[Literal['В/м', 'дБмкВ/м', 'Вт/м²']] = ['В/м', 'дБмкВ/м', 'Вт/м²']
        self.current_units: Literal['В/м', 'дБмкВ/м', 'Вт/м²'] = 'В/м'

    def get_connected_probes(self) -> list[FL7040_Probe]:
        return [probe for probe in self.probes if probe.connection_status]

    def _collect_data(self) -> None:
        while self._running_flag:
            start_time: float = time.time()

            [probe.wait_result() for probe in self.probes if probe.connection_status]

            results: list[FieldResult] = [probe.get_measured_data() for probe in self.get_connected_probes()]
            [probe.permit_measure() for probe in self.probes]  # pd.Timestamp(datetime.now())
            df: DataFrame = pd.concat([pd.DataFrame({'Timestamp': [time.time()]}),
                                       *[result.dataframe().iloc[:, 1:] for result in results]], axis=1)
            self.df: DataFrame =  pd.concat([self.df, df], ignore_index=True)
            # print(self.df.iloc[:, [0, 4, 10]].to_numpy().transpose())
            # print(df)
            delta: float = time.time() - start_time
            if delta < self.measure_period_sec:
                time.sleep(self.measure_period_sec - delta)

    def calibrate_dataframe(self, freq: int):
        pass

    def clear_data(self):
        self.df = DataFrame()

    def get_data(self, units: int):
        self.current_units = self.units[units]
        column_nums: list[int] = [val for val in range(4 + units, 6 * len(self.get_connected_probes()) + 1, 6)]
        print(self.df.iloc[:, [0, *column_nums]])
        return self.df.iloc[:, [0, *column_nums]].to_numpy().transpose()

    def set_measuring_period(self, period_sec: float) -> None:
        self.measure_period_sec = period_sec
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
        calib_path: Path = Path(self.config.settings.calibration_path)
        [probe.calibrate_probe(calib_path) for probe in self.get_connected_probes()]
        [probe.start_measuring() for probe in self.get_connected_probes()]
        self._thread = Thread(name='Collecting data', target=self._collect_data, daemon=True)
        self._running_flag = True
        self._thread.start()
        return all([probe.connection_status for probe in self.probes])

    def disconnect(self):
        [probe.disconnect() for probe in self.get_connected_probes()]
        self._running_flag = False
        self._thread.join(1)
        self.connection_status = False

if __name__ == '__main__':
    device = FL7000_Interface(FL7000_Config())
    print(device.connect('10.6.1.95', [4001, 4003]))
    device.set_measuring_period(1)
    try:
        while True:
            in_data = input('>')
    except KeyboardInterrupt:
        print('x_x')