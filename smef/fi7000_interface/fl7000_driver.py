

from datetime import datetime
from threading import Thread
import time
from functools import reduce
import pandas as pd
from pandas import DataFrame
from smef.fi7000_interface.config import FL7000_Config
from smef.fi7000_interface.fl7040_driver import FL7040_Probe, FieldResult

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 370)

class FL7000_Interface:
    def __init__(self) -> None:
        self.config = FL7000_Config()
        # self.config.write_config()
        self.ip: str = self.config.settings.ip
        self.probes: list[FL7040_Probe] = [FL7040_Probe(self.ip, port) for port in self.config.settings.ports]
        self._thread: Thread
        self.calibrate_freq: float | None = None
        self.connection_status: bool = False
        self.df = DataFrame()
        self.measure_period_ms: int = 1000
        self._running_flag: bool = False

    def _collect_data(self) -> None:
        while self._running_flag:
            start_time: float = time.time()

            [probe.wait_result() for probe in self.probes]

            results: list[FieldResult] = [probe.get_measured_data() for probe in self.probes]
            [probe.permit_measure() for probe in self.probes]
            df: DataFrame = reduce(lambda left, right: pd.merge_asof(left, right, on='Timestamp',
                                                                     tolerance=pd.Timedelta('5000ms')),
                                   [result.dataframe() for result in results])
            self.df: DataFrame =  pd.concat([self.df, df], ignore_index=True)
            print(self.df)
            # print(df)
            delta: float = time.time() - start_time
            if delta < (self.measure_period_ms / 1000):
                time.sleep(self.measure_period_ms / 1000 - delta)



    def set_measuring_period(self, period_ms: int) -> None:
        self.measure_period_ms = period_ms
        [probe.set_measure_period(period_ms) for probe in self.probes]

    @staticmethod
    def _fast_connect(probes: list[FL7040_Probe]) -> None:
        threads: list[Thread] = [Thread(target=probe.connect_device, daemon=True) for probe in probes]
        [thread.start() for thread in threads]
        [thread.join(2) for thread in threads]

    @staticmethod
    def check_connected(probes: list[FL7040_Probe]) -> list[bool]:
        FL7000_Interface._fast_connect(probes)
        result: list[bool] = [probe.connection_status for probe in probes]
        [probe.disconnect() for probe in probes]
        return result

    def connect(self, ip: str, ports: list[int]) -> bool:
        if self.connection_status:
            return True
        self.probes = [FL7040_Probe(ip, port) for port in ports]
        self._fast_connect(self.probes)
        self.connection_status = True
        calib_path: str = 'X:\\NextCloudStorage\\ImportantData\\PyQt_projects\\SMEF\\sensor_calibrations' #self.config.settings.calibration_path
        [probe.calibrate_probe(calib_path) for probe in self.probes if probe.connection_status]
        [probe.start_measuring() for probe in self.probes if probe.connection_status]
        self._thread = Thread(name='Collecting data', target=self._collect_data, daemon=True)
        self._running_flag = True
        self._thread.start()
        return all([probe.connection_status for probe in self.probes])

if __name__ == '__main__':
    device = FL7000_Interface()
    print(device.connect('localhost', [4001, 4002, 4004]))
    device.set_measuring_period(100)
    try:
        while True:
            in_data = input('>')
    except KeyboardInterrupt:
        print('x_x')