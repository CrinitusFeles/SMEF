import socket
from typing import Optional

import numpy as np
from numpy import ndarray

from smef.app_logger import get_logger
import re
from smef.fi7000_interface.calibrations import load_calibration_by_id, Calibration
logger = get_logger(__name__)


class FL7000:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock: Optional[socket.socket] = None
        self.probe_id: Optional[int] = None
        self.probe_calibration: Optional[Calibration] = None
        self.connection_status = False
        self.label = ''

    def __str__(self):
        return f'FL7000 Description\nAddress: {self.ip}:{self.port}\n' \
               f'Connection status: {self.connection_status}\n' \
               f'Device Info: {self.read_device_info()}\n' \
               f'Probe ID: {self.probe_id}\nProbe Info: {self.read_probe_info()}\nCalibration: {self.probe_calibration}'

    def connection_status_check(self) -> bool:
        return self.connection_status

    def connect_device(self):
        if not self.connection_status:
            try:
                logger.info(f'{self.ip}:{self.port} connection attempt')
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(1)
                self.sock.connect((self.ip, self.port))
                self.connection_status = True
            except OSError as ex:
                logger.error('Error at %s', 'socket', exc_info=ex)
                logger.info('Probable reason: device already connected')
        else:
            logger.info(f'{self.ip}:{self.port} already connected')
        if self.identify() is not None:
            logger.info(f'{self.ip}:{self.port} connected')

    def identify(self) -> Optional[int]:
        self.probe_id = self.read_probe_id_zeroless()
        if self.probe_id is not None:
            self.probe_calibration = load_calibration_by_id(self.probe_id)
        return self.probe_id

    def get_probe_id(self) -> int:
        return self.probe_id

    def get_probe_calibration(self) -> Calibration:
        return self.probe_calibration

    def calibrate_measure(self, freq: float) -> Optional[ndarray]:
        print('try to calibrate_measure')
        if self.probe_calibration is not None:
            print('calib is not none')
            uncalibrated_x_y_z = np.array([*self.read_probe_measure()[:3]])
            x_y_z_calib_params = self.probe_calibration.calibrate_value(freq, *uncalibrated_x_y_z)
            calibrated_measure = uncalibrated_x_y_z + x_y_z_calib_params
            return np.append(calibrated_measure, np.linalg.norm(calibrated_measure))  # x, y, z, norm
        else:
            return None

    def cmd_process(self, cmd: str) -> Optional[str]:
        answer = ''
        if self.connection_status:
            try:
                self.sock.send(cmd.encode())
                while True:
                    data = self.sock.recv(1024)
                    answer += data.decode()
                    if answer[-1] == '\r':
                        break
                return answer
            except Exception as ex:
                self.connection_status = False
                logger.error('Error at %s', 'socket', exc_info=ex)
                logger.info(f'Read {len(answer)} bytes: {answer}')
                return None
        else:
            logger.error('Device not connected')
            return None

    def read_probe_measure(self) -> Optional[tuple[float, float, float, float]]:
        answer = self.cmd_process('D\r')
        if answer is not None:
            x, y, z, s = [float(x) for x in re.findall(r'\d{2}\.\d{2}', answer)]
            return x, y, z, s

    def read_device_info(self) -> Optional[list[str]]:
        answer = self.cmd_process('*IDN?\r')
        if answer is not None:
            return answer.split(',')

    def read_probe_info(self) -> Optional[list[str]]:
        answer = self.cmd_process('I\r')
        if answer is not None:
            return answer.split(',')[1:-1]

    def read_probe_id(self) -> Optional[str]:
        answer = self.read_probe_info()
        if answer is not None:
            return answer[1]

    def read_probe_id_zeroless(self) -> Optional[int]:
        answer = self.read_probe_id()
        if answer is not None:
            return int(answer.lstrip("0"))


if __name__ == '__main__':
    devices = [FL7000('10.6.1.96', 4001),
               FL7000('10.6.1.96', 4002),
               FL7000('10.6.1.96', 4003),
               FL7000('10.6.1.96', 4004),
               FL7000('10.6.1.96', 4005)]
    devices[2].connect_device()
    devices[1].connect_device()
    # print(devices[0])
    # print(devices[0].read_probe_measure())
    # print(devices[0].calibrate_measure(100000))
    # print(devices[2].read_probe_id_zeroless())
    # print(devices[2].read_device_info())
