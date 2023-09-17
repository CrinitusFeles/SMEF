from dataclasses import dataclass
from datetime import datetime
from queue import Queue
import socket
from pathlib import Path
import re
from threading import Condition, Thread
import time
import numpy as np
from loguru import logger
from smef.fi7000_interface.calibrations import load_calibration_by_id, Calibration

@dataclass
class DataRaw:
    x: float
    y: float
    z: float
    s: float

@dataclass
class DataCalib(DataRaw):
    freq: float

@dataclass
class FieldResult:
    timestamp: datetime
    data: DataCalib | DataRaw

class FL7040_Probe:
    sock: socket.socket
    def __init__(self, ip: str, port: int) -> None:
        self.ip: str = ip
        self.port: int = port
        self.probe_id: str = ''
        self.device_model: str = ''
        self.revision: str = ''
        self.date: str = ''
        self.probe_calibration: Calibration | None = None
        # self.calibration_path: Path = Path(__file__).parent.joinpath('sensor_calibrations')
        self.connection_status = False
        self.label: str = ''
        self._thread: Thread
        self.calibration_freq: float | None = None
        self.measuring_flag: bool = False
        self.measured_data: Queue[FieldResult] = Queue(1000)
        self.measure_period_ms: int = 1000
        self.result_ready: Condition = Condition()

    def __str__(self) -> str:
        return f'FL7000 Description\nAddress: {self.ip}:{self.port}\n' \
               f'Connection status: {self.connection_status}\n' \
               f'Probe ID: {self.probe_id}\nCalibration: {self.probe_calibration}'

    def connect_device(self) -> bool:
        if self.connection_status:
            logger.info(f'{self.ip}:{self.port} already connected')
            return True
        try:
            logger.info(f'{self.ip}:{self.port} connection attempt')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(2)
            self.sock.connect((self.ip, self.port))
            self.connection_status = True
            self.device_model, self.probe_id, self.revision, self.date = self.read_probe_info()
            logger.success(f'{self.ip}:{self.port} {self.probe_id} successfully connected')
            return True
        except (TimeoutError, OSError, ValueError) as err:
            logger.error(f'Error at {self.sock}:\n{err}')
        return False

    def calibrate_probe(self, path: str | Path) -> None:
        self.probe_calibration = load_calibration_by_id(path, self.probe_id)

    def disconnect(self) -> None:
        if self.connection_status:
            self.sock.close()
        else:
            logger.error(f'Probe {self.port} was not connected')

    def calibrate_measure(self, freq: float) -> DataCalib:
        data: DataRaw = self.read_probe_measure()
        if self.probe_calibration:
            uncalibrated = np.array([data.x, data.y, data.z])
            calib_params = self.probe_calibration.calibrate_value(freq, *uncalibrated)
            calibrated_measure = uncalibrated + calib_params
            return DataCalib(*calibrated_measure, s=np.linalg.norm(calibrated_measure).astype(float), freq=freq)
        logger.error(f'Incorrect calibration! {self.port} {self.probe_id}')
        return DataCalib(data.x, data.y, data.z, data.s, freq)

    def cmd_process(self, cmd: bytes) -> str | None:
        data: bytes = b''
        if not self.connection_status:
            logger.error(f'Device {self.port} {self.probe_id} not connected')
            return None
        try:
            self.sock.send(cmd)
            while True:
                data += self.sock.recv(1024)
                if data.endswith(b'\n\r'):
                    break
            return data.decode()
        except TimeoutError as ex:
            self.connection_status = False
            logger.error(f'Error at {self.sock}:\n{ex}\nRead {len(data)} bytes: {data}')
            return None

    def read_probe_measure(self) -> DataRaw:
        answer: str | None = self.cmd_process(b'D\r')
        if not answer:
            logger.debug('Trying to reconnect...')
            if self.connect_device():
                answer = self.cmd_process(b'D\r')
        if answer:
            point = DataRaw(*[float(x) for x in re.findall(r'\d{2}\.\d{2}', answer)])
            return point
        logger.error('Failed to reconnect')
        return DataRaw(0, 0, 0, 0)

    def read_device_info(self) -> list[str] | None:
        answer: str | None = self.cmd_process(b'*IDN?\r')
        if answer is not None:
            return answer.split(',')

    def read_probe_info(self) -> list[str]:
        answer: str | None = self.cmd_process(b'I\r')
        if answer:
            result: list[str] = answer.split(',')
            if result:
                return result[1:-1]
        raise ValueError(f'Reading probe id error! Answer: {answer}')

    def _measure_routine(self) -> None:
        while self.measuring_flag:
            with self.result_ready:
                measure_time: datetime = datetime.now()
                # if not self.calibration_freq:
                result = self.read_probe_measure()
                # else:
                #     result = self.calibrate_measure(self.calibration_freq)
                self.measured_data.put_nowait(FieldResult(measure_time, result))
                self.result_ready.notify_all()
            time.sleep(self.measure_period_ms / 1000)

    def start_measuring(self):
        if not self.measuring_flag:
            self._thread = Thread(name=f'Probe {self.port} thread', target=self._measure_routine, daemon=True)
            self.measuring_flag = True
            self._thread.start()
        else:
            logger.error(f'Probe {self.port} already in measuring process')

    def set_measure_period(self, period_ms: int) -> None:
        self.measure_period_ms = period_ms

if __name__ == '__main__':
    ip = '10.6.1.95'
    devices: list[FL7040_Probe] = [
        FL7040_Probe(ip, 4005),
        FL7040_Probe(ip, 4004),
        FL7040_Probe(ip, 4003),
        FL7040_Probe(ip, 4002),
        FL7040_Probe(ip, 4001),
    ]
    for device in devices:
        try:
            device.connect_device()
            print(device.read_probe_measure())
        except ValueError as err:
            print(err)



    # print(devices[0])
    # print(devices[0].read_probe_measure())
    # print(devices[0].calibrate_measure(100000))
    # print(devices[2].read_probe_id_zeroless())
    # print(devices[2].read_device_info())
