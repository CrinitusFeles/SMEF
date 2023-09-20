from dataclasses import dataclass
from datetime import datetime
# from datetime import datetime
from queue import Queue
import socket
from pathlib import Path
import re
from threading import Thread
import time
import pandas as pd
import numpy as np
from loguru import logger
from smef.fi7000_interface.calibrations import load_calibration_by_id, Calibration

@dataclass
class DataRaw:
    x: float
    y: float
    z: float
    s: float  # V/m
    s_log: float  # дБмкВ/м
    s_w: float  # Вт/м2


@dataclass
class DataCalib(DataRaw):
    freq: float

@dataclass
class FieldResult:
    probe_id: str
    timestamp: datetime
    data: DataCalib | DataRaw

    def dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({'Timestamp': [pd.Timestamp(self.timestamp).ceil('S')],
                             f'{self.probe_id} x': [self.data.x],
                             f'{self.probe_id} y': [self.data.y],
                             f'{self.probe_id} z': [self.data.z],
                             f'{self.probe_id} s_v': [self.data.s],
                             f'{self.probe_id} s_dBm': [self.data.s_log],
                             f'{self.probe_id} s_w': [self.data.s_w]})

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
        self.result_ready: bool = False
        self.measure_permission: bool = True

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
            s = np.linalg.norm(calibrated_measure).astype(float)
            if s == 0:
                s_log =  20 * np.log10(0.001 * 10**6)
            s_log =  20 * np.log10(s * 10**6)
            s_w = s / 377
            return DataCalib(*calibrated_measure, s=s, s_log=s_log, s_w=s_w, freq=freq)
        logger.error(f'Incorrect calibration! {self.port} {self.probe_id}')
        return DataCalib(data.x, data.y, data.z, data.s, data.s_log, data.s_w, freq)

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
            x, y, z, s = [float(x) for x in re.findall(r'\d{2}\.\d{2}', answer)]
            if s == 0:
                s_log =  20 * np.log10(0.001 * 10**6)
            else:
                s_log =  20 * np.log10(s * 10**6)
            s_w = s / 377
            point = DataRaw(s, y, z, s, s_log, s_w)
            return point
        logger.error('Failed to reconnect')
        return DataRaw(0, 0, 0, 0, 0, 0)

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

    def permit_measure(self):
        self.measure_permission = True

    def _single_measure_routine(self) -> None:
        while self.measuring_flag:
            while not self.measure_permission:
                pass
            self.measured_data.put_nowait(FieldResult(self.probe_id, datetime.now(), self.read_probe_measure()))
            self.result_ready = True
            self.measure_permission = False

    def _stream_measure_routine(self) -> None:
        while self.measuring_flag:
            self.measured_data.put_nowait(FieldResult(self.probe_id, datetime.now(), self.read_probe_measure()))
            self.result_ready = True
            time.sleep(self.measure_period_ms / 1000)

    def wait_result(self) -> None:
        while not self.result_ready:
            pass

    def get_measured_data(self) -> FieldResult:
        self.result_ready = False
        return self.measured_data.get_nowait()

    def start_measuring(self):
        if not self.measuring_flag:
            self._thread = Thread(name=f'Probe {self.port} thread', target=self._single_measure_routine, daemon=True)
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
