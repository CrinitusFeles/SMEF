

from datetime import datetime
from threading import Thread
import time
from smef.fi7000_interface.config import FL7000_Config
from smef.fi7000_interface.fl7040_driver import FL7040_Probe, FieldResult


class FL7000_Interface:
    def __init__(self) -> None:
        self.config = FL7000_Config()
        # self.config.write_config()
        self.ip: str = self.config.settings.ip
        self.probes: list[FL7040_Probe] = [FL7040_Probe(self.ip, port) for port in self.config.settings.ports]
        self._thread: Thread
        self.calibrate_freq: float | None = None
        self.connection_status: bool = False

    def _collect_data(self):
        while True:
            result: list[FieldResult] = [probe.measured_data.get(timeout=probe.measure_period_ms) for probe in self.probes]
            print(result)
            time.sleep(1)
        #     probe.result_ready.

    def set_measuring_period(self, period_ms: int) -> None:
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
        calib_path: str = 'X:\\NextCloudStorage\\ImportantData\\PyQt_projects\\SMEF\\sensor_calibrations' #self.config.settings.calibration_path
        [probe.calibrate_probe(calib_path) for probe in self.probes if probe.connection_status]
        [probe.start_measuring() for probe in self.probes if probe.connection_status]
        self._thread = Thread(name='Collecting data', target=self._collect_data, daemon=True)
        self._thread.start()
        return all([probe.connection_status for probe in self.probes])

if __name__ == '__main__':
    device = FL7000_Interface()
    print(device.connect('localhost', [4001, 4002]))

    try:
        while True:
            in_data = input('>')
    except KeyboardInterrupt:
        print('x_x')