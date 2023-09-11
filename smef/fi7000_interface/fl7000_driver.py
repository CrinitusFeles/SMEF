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
        self.probe_id: str = ''
        self.device_model: str = ''
        self.revision: str = ''
        self.date: str = ''
        self.probe_calibration: Calibration
        self.calibration_path: str = 'X:\\NextCloudStorage\\ImportantData\\PyQt_projects\\SMEF\\sensor_calibrations'
        self.connection_status = False
        self.label: str = ''

    def __str__(self):
        return f'FL7000 Description\nAddress: {self.ip}:{self.port}\n' \
               f'Connection status: {self.connection_status}\n' \
               f'Probe ID: {self.probe_id}\nCalibration: {self.probe_calibration}'

    def connect_device(self):
        if self.connection_status:
            logger.info(f'{self.ip}:{self.port} already connected')
            return True
        try:
            logger.info(f'{self.ip}:{self.port} connection attempt')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1)
            self.sock.connect((self.ip, self.port))
            self.connection_status = True

            self.device_model, self.probe_id, self.revision, self.date = self.read_probe_info()
            self.probe_calibration = load_calibration_by_id(self.calibration_path, self.probe_id)
            return True
        except (TimeoutError, OSError) as err:
            logger.error(f'Error at {self.sock}:\n{err}')
        return False

    def calibrate_measure(self, freq: float) -> ndarray:
        if hasattr(self, 'probe_calibration'):
            if self.probe_calibration:
                data: tuple[float, ...] = self.read_probe_measure()
                uncalibrated_x_y_z = np.array([*data[:3]])
                x_y_z_calib_params = self.probe_calibration.calibrate_value(freq, *uncalibrated_x_y_z)
                calibrated_measure = uncalibrated_x_y_z + x_y_z_calib_params
                return np.append(calibrated_measure, np.linalg.norm(calibrated_measure))  # x, y, z, norm
        logger.error('Incorrect calibration!')
        return np.array([])

    def cmd_process(self, cmd: bytes) -> str | None:
        data: bytes = b''
        if self.connection_status:
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
        else:
            logger.error('Device not connected')
            return None

    def read_probe_measure(self) -> tuple[float, ...]:
        answer: str | None = self.cmd_process(b'D\r')
        if answer is not None:
            x, y, z, s = [float(x) for x in re.findall(r'\d{2}\.\d{2}', answer)]
            return x, y, z, s
        return (0, 0, 0, 0)

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



if __name__ == '__main__':
    ip = '10.6.1.95'
    devices: list[FL7000] = [
        FL7000(ip, 4005),
        FL7000(ip, 4004),
        FL7000(ip, 4003),
        FL7000(ip, 4002),
        FL7000(ip, 4001),
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
