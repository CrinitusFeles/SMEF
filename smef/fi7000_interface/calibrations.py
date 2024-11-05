from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal, TypeVar
import numpy as np
import numpy.typing as npt
from numpy import ndarray
import pandas as pd
from pandas import DataFrame
from loguru import logger

from smef.utils import get_label
np.set_printoptions(edgeitems=30, linewidth=300)

DType = TypeVar("DType", bound=np.generic)

Array3 = Annotated[npt.NDArray[DType], Literal[3]]
Array3x3 = Annotated[npt.NDArray[DType], Literal[3, 3]]
ArrayNx3 = Annotated[npt.NDArray[DType], Literal['N', 3]]
ArrayNx1 = Annotated[npt.NDArray[DType], Literal['N', 1]]
ArrayNxNx3 = Annotated[npt.NDArray[DType], Literal["N", "N", 3]]


def get_files_with_ext(path: Path, ext: str) -> list[Path]:
    return [f for f in path.iterdir()
            if path.joinpath(f).is_file() and f.suffix == ext]


def parse_freq_response_file(data: str) -> list[str]:
    return data.replace('\t\t', '\t').replace('\t\n', '\n').split('\n')


def parse_linearity_file(data: str) -> list[str]:
    return data.replace('\t\n', '\n').split('\n')


def freq_response_calib(path: Path) -> list[tuple[str, ndarray]]:
    calib_files: list[Path] = get_files_with_ext(path, ".ar")
    calibrations: list[tuple[str, ndarray]] = []
    for file in calib_files:
        with open(path.joinpath(file), 'r') as calib_file:
            file_lines: list[str] = parse_freq_response_file(calib_file.read())
            sensor_id: str = file_lines[0].lstrip("0")
            field_lists: ndarray = np.array([np.array(line.split('\t'))
                                             for line in file_lines[1:]
                                             if line != ''])
            freq: ndarray = field_lists[:, 0].astype(float)
            x_freq_points: ndarray = field_lists[:, 1].astype(float)
            y_freq_points: ndarray = field_lists[:, 2].astype(float)
            z_freq_points: ndarray = field_lists[:, 3].astype(float)
            calibrations.append((sensor_id, np.vstack((freq,
                                                       x_freq_points,
                                                       y_freq_points,
                                                       z_freq_points))))
    return calibrations


def linear_calib(path: Path) -> list[tuple[str, ndarray]]:
    calib_files: list[Path] = get_files_with_ext(path, ".txt")
    calibrations: list[tuple[str, ndarray]] = []
    for file in calib_files:
        with open(path.joinpath(file), 'r') as calib_file:
            file_lines: list[str] = parse_linearity_file(calib_file.read())
            sensor_id: str = file_lines[5].split(':')[1].strip().lstrip("0")
            data_lines: ndarray = np.array([val.split('\t')
                                            for val in file_lines[-7:-2]])
            linear: ndarray = data_lines[:, 1].astype(int)
            x_correction: ndarray = linear / data_lines[:, 2].astype(float)
            y_correction: ndarray = linear / data_lines[:, 3].astype(float)
            z_correction: ndarray = linear / data_lines[:, 4].astype(float)
            calibrations.append((sensor_id, np.vstack((linear,
                                                       x_correction,
                                                       y_correction,
                                                       z_correction))))
    return calibrations

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ProbeCalibrator:
    def __init__(self, freq_calibration: tuple[str, ndarray],
                 amplitude_calibration: tuple[str, ndarray]) -> None:
        self.sensor_id = freq_calibration[0]
        self.freq_list = freq_calibration[1][0]
        self.x_freq_points = freq_calibration[1][1]
        self.y_freq_points = freq_calibration[1][2]
        self.z_freq_points = freq_calibration[1][3]

        self.liear = amplitude_calibration[1][0]
        self.x_linear_points = amplitude_calibration[1][1]
        self.y_linear_points = amplitude_calibration[1][2]
        self.z_linear_points = amplitude_calibration[1][3]

    def calibrate_value(self, xyz: Array3, freq: float) -> ndarray:
        x_freq_param = np.interp(freq, self.freq_list, self.x_freq_points)
        y_freq_param = np.interp(freq, self.freq_list, self.y_freq_points)
        z_freq_param = np.interp(freq, self.freq_list, self.z_freq_points)
        x_amp_param = np.interp(xyz[0], self.liear, self.x_linear_points)
        y_amp_param = np.interp(xyz[1], self.liear, self.y_linear_points)
        z_amp_param = np.interp(xyz[2], self.liear, self.z_linear_points)
        return np.array([x_freq_param * x_amp_param, y_freq_param * y_amp_param,
                         z_freq_param * z_amp_param])

    def calibrate_dataframe(self, freq: float, df: DataFrame) -> DataFrame:
        freq_mhz: float = freq / 1e6
        xyz: ArrayNx3 = df.iloc[:, 1:4].to_numpy()
        calib_xyz: ArrayNx3 = np.apply_along_axis(self.calibrate_value, 1, xyz,
                                                  freq=freq)
        v_m: ArrayNx1 = np.apply_along_axis(np.linalg.norm, 1, xyz * calib_xyz)
        w_m2: ArrayNx1 = np.apply_along_axis(lambda x: x / 377, 0, v_m)
        dBuV_m: ArrayNx1 = np.apply_along_axis(lambda x: 20 * np.log10(x * 10**6, where=x > 0), 0, v_m)

        label: str = f'{get_label(self.sensor_id)}({self.sensor_id})'
        dataframe = DataFrame({f'{label} x\n{freq_mhz:.2f} МГц': calib_xyz.T[0],
                               f'{label} y\n{freq_mhz:.2f} МГц': calib_xyz.T[1],
                               f'{label} z\n{freq_mhz:.2f} МГц': calib_xyz.T[2],
                               f'{label} В/м\n{freq_mhz:.2f} МГц': v_m.T,
                               f'{label} дБмкВ/м\n{freq_mhz:.2f} МГц': dBuV_m.T,
                               f'{label} Вт/м²\n{freq_mhz:.2f} МГц': w_m2.T})
        timestamps = DataFrame(df.iloc[:, 0])
        return pd.concat([timestamps, dataframe], axis=1)

    def __str__(self) -> str:
        return f'Probe ID: {self.sensor_id}\n'\
               f'Freq list: {self.freq_list}\n'\
               f'X param: {self.x_freq_points}\n' \
               f'Y param: {self.y_freq_points}\n' \
               f'Z param: {self.z_freq_points}'


class Calibrator(metaclass=Singleton):
    def __init__(self, path: Path | None = None) -> None:
        self.probes: dict[str, ProbeCalibrator] = {}
        logger.debug('create calibrator')
        if not path:
            logger.warning('Calibrator path undefined!')
            return None
        self.update(path)

    def __call__(self, probe_id: str) -> ProbeCalibrator:
        return self.probes[probe_id.lstrip('0')]

    def update(self, path: Path) -> None:
        freq_response: list[tuple[str, ndarray]] = freq_response_calib(path)
        linear: list[tuple[str, ndarray]] = linear_calib(path)
        for freq_calib in freq_response:
            for amplitude_calib in linear:
                if freq_calib[0] == amplitude_calib[0]:
                    calib = ProbeCalibrator(freq_calib, amplitude_calib)
                    self.probes.update({freq_calib[0]: calib})


def load_calibration_by_id(path: Path, id: str) -> ProbeCalibrator | None:
    probe_id: str = id.lstrip('0')
    freq_calibrations: list[tuple[str, ndarray]] = freq_response_calib(path)
    amplitude_calibrations: list[tuple[str, ndarray]] = linear_calib(path)
    freq: tuple[str, ndarray] | None = None
    ampl: tuple[str, ndarray] | None = None
    for calib in freq_calibrations:
        if calib[0] == probe_id:
            freq = calib
    for calib in amplitude_calibrations:
        if calib[0] == probe_id:
            ampl = calib
    if freq is None or ampl is None:
        msg: str = 'Calibration loading error for'
        raise ValueError(f'{msg} {probe_id=}:\n{freq=};\n{ampl=}')
    return ProbeCalibrator(freq, ampl)



# if __name__ == '__main__':
    # from matplotlib import pyplot as plt
    # calib = Calibrator(Path('X:\\NextCloudStorage\\ImportantData\\VSCode_projects\\SMEF\\smef\\sensor_calibrations'))
    # print(calib('357218'))

    # # calibrations = find_calibration_pairs(load_freq_calibrations(), load_amplitude_calibrations())
    # freq_grid = np.linspace(0, 40e9, 10000)
    # amp_grid = np.linspace(5, 300, 1000)
    # print(calib.probes['357218'].calibrate_value(np.array([15.44, 5.44, 12.23]), 10000000))
    # for i, calib in enumerate(calib.probes.values()):
    #     plt.subplot(4, 5, i + 1)
    #     plt.subplots_adjust(wspace=0.6, top=0.9, bottom=0.1, hspace=0.6, left=0.1, right=0.9)
    #     plt.plot(calib.freq_list, calib.x_freq_points, '-o', label='x')
    #     plt.plot(calib.freq_list, calib.y_freq_points, '-o', label='y')
    #     plt.plot(calib.freq_list, calib.z_freq_points, '-o', label='z')
    #     plt.title(f"Frequency calibration data for {calib.sensor_id} sensor")
    #     plt.xlabel("frequency")

    #     plt.subplot(4, 5, i + 6)
    #     plt.plot(freq_grid, np.interp(freq_grid, calib.freq_list, calib.x_freq_points), '-o', label='x')
    #     plt.plot(freq_grid, np.interp(freq_grid, calib.freq_list, calib.y_freq_points), '-o', label='y')
    #     plt.plot(freq_grid, np.interp(freq_grid, calib.freq_list, calib.z_freq_points), '-o', label='z')
    #     plt.title(f"Linear interpolation for {calib.sensor_id} sensor")
    #     plt.xlabel("frequency")

    #     plt.subplot(4, 5, i + 11)
    #     plt.plot(calib.liear, calib.x_linear_points, '-o', label='x')
    #     plt.plot(calib.liear, calib.y_linear_points, '-o', label='y')
    #     plt.plot(calib.liear, calib.z_linear_points, '-o', label='z')
    #     plt.title(f"Amplitude calibration data for {calib.sensor_id} sensor")
    #     plt.xlabel("amplitude")

    #     plt.subplot(4, 5, i + 16)
    #     plt.plot(amp_grid, np.interp(amp_grid, calib.liear, calib.x_linear_points), '-o', label='x')
    #     plt.plot(amp_grid, np.interp(amp_grid, calib.liear, calib.y_linear_points), '-o', label='y')
    #     plt.plot(amp_grid, np.interp(amp_grid, calib.liear, calib.z_linear_points), '-o', label='z')
    #     plt.title(f"Linear interpolation for {calib.sensor_id} sensor")

    #     plt.legend()
    #     plt.xlabel("amplitude")
    #     plt.ylabel("factor")

    # plt.show()
