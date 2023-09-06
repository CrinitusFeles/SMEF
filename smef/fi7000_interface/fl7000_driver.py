import socket
import re
import numpy as np
from numpy import ndarray
from loguru import logger
from smef.fi7000_interface.calibrations import load_calibration_by_id, Calibration



class FL7000:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sock: socket.socket
        self.probe_id: int = -1
        self.probe_calibration: Calibration
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
            except TimeoutError as tm:
                logger.error(f'{tm}:\n{self.sock}')
            except OSError as ex:
                logger.error(f'Error at {self.sock}:\n{ex}')
                logger.info('Probable reason: device already connected')

        else:
            logger.info(f'{self.ip}:{self.port} already connected')
        if self.identify():
            logger.info(f'{self.ip}:{self.port} connected')

    def identify(self) -> int:
        self.probe_id = self.read_probe_id_zeroless()
        if self.probe_id:
            self.probe_calibration = load_calibration_by_id(self.probe_id)
        return self.probe_id

    def get_probe_id(self) -> int:
        return self.probe_id

    def get_probe_calibration(self) -> Calibration:
        return self.probe_calibration

    def calibrate_measure(self, freq: float) -> ndarray:
        if self.probe_calibration is not None:
            uncalibrated_x_y_z = np.array([*self.read_probe_measure()[:3]])
            x_y_z_calib_params = self.probe_calibration.calibrate_value(freq, *uncalibrated_x_y_z)
            calibrated_measure = uncalibrated_x_y_z + x_y_z_calib_params
            return np.append(calibrated_measure, np.linalg.norm(calibrated_measure))  # x, y, z, norm
        else:
            return np.array([])

    def cmd_process(self, cmd: str) -> str | None:
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
                logger.error(f'Error at {self.sock}:\n{ex}')
                logger.info(f'Read {len(answer)} bytes: {answer}')
                return None
        else:
            logger.error('Device not connected')
            return None

    def read_probe_measure(self) -> tuple[float, ...] | None:
        answer = self.cmd_process('D\r')
        if answer is not None:
            x, y, z, s = [float(x) for x in re.findall(r'\d{2}\.\d{2}', answer)]
            return x, y, z, s

    def read_device_info(self) -> list[str] | None:
        answer = self.cmd_process('*IDN?\r')
        if answer is not None:
            return answer.split(',')

    def read_probe_info(self) -> list[str] | None:
        answer = self.cmd_process('I\r')
        if answer is not None:
            return answer.split(',')[1:-1]

    def read_probe_id(self) -> str | None:
        answer = self.read_probe_info()
        if answer is not None:
            return answer[1]

    def read_probe_id_zeroless(self) -> int | None:
        answer = self.read_probe_id()
        if answer is not None:
            return int(answer.lstrip("0"))


if __name__ == '__main__':
    ip = 'localhost'
    devices: list[FL7000] = [FL7000(ip, 4001),
                             FL7000(ip, 4002),
                             FL7000(ip, 4003),
                             FL7000(ip, 4004),
                             FL7000(ip, 4005)]
    devices[2].connect_device()
    devices[1].connect_device()
    # print(devices[0])
    # print(devices[0].read_probe_measure())
    # print(devices[0].calibrate_measure(100000))
    # print(devices[2].read_probe_id_zeroless())
    # print(devices[2].read_device_info())
