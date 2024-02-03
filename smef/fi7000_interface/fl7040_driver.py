from dataclasses import dataclass
from datetime import datetime
# from datetime import datetime
import socket
from pathlib import Path
import re
from threading import Thread
import time
from matplotlib.pylab import f

import numpy as np

import pandas as pd
from loguru import logger
from smef.fi7000_interface.calibrations import ProbeCalibrator
from smef.utils import get_label


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
        suffix: str = f'{self.data.freq / 1e6:.2f} МГц' if isinstance(self.data, DataCalib) else ''
        return pd.DataFrame({'Timestamp': [time.time()],
                             f'{self.probe_id} x\n{suffix}': [self.data.x],
                             f'{self.probe_id} y\n{suffix}': [self.data.y],
                             f'{self.probe_id} z\n{suffix}': [self.data.z],
                             f'{self.probe_id} В/м\n{suffix}': [self.data.s],
                             f'{self.probe_id} дБмкВ/м\n{suffix}': [self.data.s_log],
                             f'{self.probe_id} Вт/м²\n{suffix}': [self.data.s_w]})

class FL7040_Probe:
    sock: socket.socket
    def __init__(self, ip: str, port: int) -> None:
        self.ip: str = ip
        self.port: int = port
        self.probe_id: str = ''
        self.device_model: str = ''
        self.revision: str = ''
        self.date: str = ''
        self.calibrator: ProbeCalibrator | None = None
        # self.calibration_path: Path = Path(__file__).parent.joinpath('sensor_calibrations')
        self.connection_status = False
        self.label: str = ''
        self.connectable: bool = False
        self._thread: Thread
        self.calibration_freq: float | None = None
        self.measuring_flag: bool = False
        self.df: pd.DataFrame = pd.DataFrame()
        self.df_calib: pd.DataFrame = pd.DataFrame()
        self.measure_period_sec: float = 1.0
        self.result_ready: bool = False
        self.measure_permission: bool = True
        self.output_path: Path = Path(__file__).parent

    def __str__(self) -> str:
        return f'FL7000 Description\nAddress: {self.ip}:{self.port}\n' \
               f'Connection status: {self.connection_status}\n' \
               f'Probe ID: {self.probe_id}\nCalibration: {self.calibrator}'

    def set_output_path(self, path: Path) -> None:
        self.output_path = path

    def connect_device(self) -> bool:
        if self.connection_status:
            logger.info(f'{self.ip}:{self.port} already connected')
            return True
        try:
            logger.info(f'{self.ip}:{self.port} connection attempt')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(0.5)
            self.sock.connect((self.ip, self.port))
            self.connection_status = True
            self.device_model, self.probe_id, self.revision, self.date = self.read_probe_info()
            self.probe_id = self.probe_id.lstrip('0')
            self.probe_id = f'{get_label(self.probe_id)}({self.probe_id})'
            self.connectable = True
            logger.success(f'{self.ip}:{self.port} {self.probe_id} successfully connected')
            return True
        except (TimeoutError, OSError, ValueError) as err:
            logger.error(f'Error at {self.sock}:\n{err}')
        return False

    def calibrate_probe(self, calibrator: ProbeCalibrator) -> None:
        self.calibrator = calibrator

    def disconnect(self) -> None:
        if self.connection_status:
            self.measuring_flag = False
            if hasattr(self, '_thread'):
                self._thread.join(1)
            self.sock.close()
            self.connection_status = False
            logger.debug(f'Probe {self.port} disconnected')
        else:
            logger.error(f'Probe {self.port} was not connected')

    def get_df_data(self, freq: float | None = None) -> pd.DataFrame:
        return self.df_calib if freq else self.df

    def calibrate_measure(self, data: DataRaw, freq: float) -> DataCalib:
        if self.calibrator:
            uncalibrated = np.array([data.x, data.y, data.z])
            calib_params = self.calibrator.calibrate_value(uncalibrated, freq)
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
            start_time: float = time.time()
            raw_result: DataRaw = self.read_probe_measure()
            if self.calibration_freq:
                result = FieldResult(self.probe_id, datetime.now(),
                                     self.calibrate_measure(raw_result, self.calibration_freq))
                df_data = result.dataframe()
                concat_list = [self.df_calib, df_data]
                self.df_calib = pd.concat(concat_list, axis=0,
                                          ignore_index=True)
            result_df = FieldResult(self.probe_id, datetime.now(),
                                    raw_result).dataframe()
            self.df = pd.concat([self.df, result_df], axis=0,
                                ignore_index=True)
            filepath: Path = self.output_path.joinpath(self.probe_id + '.csv')
            self.df.tail(1).to_csv(filepath, sep='\t', mode='a', encoding='utf-8', header=not Path.exists(filepath),
                           index=False, decimal=',')
            delta: float = time.time() - start_time
            if self.measure_period_sec - delta > 0:
                time.sleep(self.measure_period_sec - delta)
            else:
                time.sleep(0.001)

    def start_measuring(self):
        if not self.measuring_flag:
            self._thread = Thread(name=f'Probe {self.port} thread', target=self._single_measure_routine, daemon=True)
            self.measuring_flag = True
            self._thread.start()
        else:
            logger.error(f'Probe {self.port} already in measuring process')

    def set_measure_period(self, period_sec: float) -> None:
        self.measure_period_sec = period_sec

    def clear_data(self) -> None:
        self.df_calib = pd.DataFrame()
        self.df = pd.DataFrame()

if __name__ == '__main__':
    ip = '10.6.1.95'
    devices: list[FL7040_Probe] = [
        # FL7040_Probe(ip, 4005),
        # FL7040_Probe(ip, 4004),
        FL7040_Probe(ip, 4003),
        # FL7040_Probe(ip, 4002),
        # FL7040_Probe(ip, 4001),
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
