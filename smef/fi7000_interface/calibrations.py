from __future__ import annotations

import os
from os import listdir
from os.path import isfile
from pathlib import Path
# import matplotlib.pyplot as plt
import numpy as np
from numpy import ndarray
np.set_printoptions(edgeitems=30, linewidth=300)


def load_freq_calibrations(path: str | Path) -> list[tuple[str, ndarray]]:
    calib_files: list[str] = [f for f in listdir(path) if isfile(os.path.join(path, f)) and f.endswith(".ar")]
    calibrations: list[tuple[str, ndarray]] = []
    for file in calib_files:
        with open(os.path.join(path, file)) as calib_file:
            file_lines: list[str] = calib_file.read().replace('\t\t', '\t').replace('\t\n', '\n').split('\n')
            sensor_id: str = file_lines[0].lstrip("0")
            field_lists: ndarray = np.array([np.array(line.split('\t')) for line in file_lines[1:] if line != ''])
            freq: ndarray = field_lists[:, 0].astype(float)
            x_freq_points: ndarray = field_lists[:, 1].astype(float)
            y_freq_points: ndarray = field_lists[:, 2].astype(float)
            z_freq_points: ndarray = field_lists[:, 3].astype(float)
            calibrations.append((sensor_id, np.vstack((freq, x_freq_points, y_freq_points, z_freq_points))))
    return calibrations


def load_amplitude_calibrations(path: str | Path) -> list[tuple[str, ndarray]]:
    calib_files: list[str] = [f for f in listdir(path) if isfile(os.path.join(path, f)) and f.endswith(".txt")]
    calibrations: list[tuple[str, ndarray]] = []
    for file in calib_files:
        with open(os.path.join(path, file)) as calib_file:
            file_lines: list[str] = calib_file.read().replace('\t\n', '\n').split('\n')
            sensor_id: str = file_lines[5].split(':')[1].strip().lstrip("0")
            data_lines: ndarray = np.array([val.split('\t') for val in file_lines[-7:-2]])
            amplitude_list: ndarray = data_lines[:, 1].astype(int)
            x_correction: ndarray = amplitude_list / data_lines[:, 2].astype(float)
            y_correction: ndarray = amplitude_list / data_lines[:, 3].astype(float)
            z_correction: ndarray = amplitude_list / data_lines[:, 4].astype(float)
            calibrations.append((sensor_id, np.vstack((amplitude_list, x_correction, y_correction, z_correction))))
    return calibrations


class Calibration:
    def __init__(self, freq_calibration: tuple[str, ndarray], amplitude_calibration: tuple[str, ndarray]) -> None:
        self.sensor_id = freq_calibration[0]
        self.freq_list = freq_calibration[1][0]
        self.x_freq_points = freq_calibration[1][1]
        self.y_freq_points = freq_calibration[1][2]
        self.z_freq_points = freq_calibration[1][3]

        self.amplitude_list = amplitude_calibration[1][0]
        self.x_amplitude_points = amplitude_calibration[1][1]
        self.y_amplitude_points = amplitude_calibration[1][2]
        self.z_amplitude_points = amplitude_calibration[1][3]

    def calibrate_value(self, freq: float, x: float | ndarray, y: float | ndarray, z: float | ndarray) -> ndarray:
        x_freq_param = np.interp(freq, self.freq_list, self.x_freq_points)
        y_freq_param = np.interp(freq, self.freq_list, self.y_freq_points)
        z_freq_param = np.interp(freq, self.freq_list, self.z_freq_points)
        x_amp_param = np.interp(x, self.amplitude_list, self.x_amplitude_points)
        y_amp_param = np.interp(y, self.amplitude_list, self.y_amplitude_points)
        z_amp_param = np.interp(z, self.amplitude_list, self.z_amplitude_points)
        return np.array([x_freq_param * x_amp_param, y_freq_param * y_amp_param, z_freq_param * z_amp_param])

    def __str__(self) -> str:
        return f'Probe ID: {self.sensor_id}\nFreq list: {self.freq_list}\nX param: {self.x_freq_points}\n' \
               f'Y param: {self.y_freq_points}\nZ param: {self.z_freq_points}'


def load_calibration_by_id(path: str | Path, id: str) -> Calibration:
    probe_id: str = id.lstrip('0')
    freq_calibrations: list[tuple[str, ndarray]] = load_freq_calibrations(path)
    amplitude_calibrations: list[tuple[str, ndarray]] = load_amplitude_calibrations(path)
    freq: tuple[str, ndarray] | None = None
    ampl: tuple[str, ndarray] | None = None
    for calib in freq_calibrations:
        if calib[0] == probe_id:
            freq = calib
    for calib in amplitude_calibrations:
        if calib[0] == probe_id:
            ampl = calib
    if freq is None or ampl is None:
        raise ValueError(f'Calibration loading error for {probe_id=}:\n{freq=};\n{ampl=}')
    return Calibration(freq, ampl)


def find_calibration_pairs(freq_calibrations: list[tuple[str, ndarray]],
                           amplitude_calibrations: list[tuple[str, ndarray]]) -> list[Calibration]:
    calibrations = []
    for freq_calib in freq_calibrations:
        for amplitude_calib in amplitude_calibrations:
            if freq_calib[0] == amplitude_calib[0]:
                calibrations.append(Calibration(freq_calib, amplitude_calib))
    if len(calibrations) != len(freq_calibrations) or len(calibrations) != len(amplitude_calibrations):
        raise Exception("Some calibrations are missing")
    return calibrations


if __name__ == '__main__':
    print(load_calibration_by_id('X:\\NextCloudStorage\\ImportantData\\PyQt_projects\\SMEF\\sensor_calibrations', '0357218'))
    # calibrations = find_calibration_pairs(load_freq_calibrations(), load_amplitude_calibrations())
    # freq_grid = np.linspace(0, 40000000000, 10000)
    # amp_grid = np.linspace(5, 300, 1000)
    # print(calibrations[0].calibrate_value(10000000, np.array([15.44, 15.44]), np.array([15.03, 15.44]), np.array([12.02, 15.44])))
    # for i, calib in enumerate(calibrations):
    #     plt.subplot(4, 5, i + 1)
    #     plt.plot(calib.freq_list, calib.x_freq_points, '-o', label=f'x')
    #     plt.plot(calib.freq_list, calib.y_freq_points, '-o', label=f'y')
    #     plt.plot(calib.freq_list, calib.z_freq_points, '-o', label=f'z')
    #     plt.title(f"Frequency calibration data for {calib.sensor_id} sensor")
    #     plt.xlabel("frequency")
    #
    #     plt.subplot(4, 5, i + 6)
    #     plt.plot(freq_grid, np.interp(freq_grid, calib.freq_list, calib.x_freq_points), '-o', label=f'x')
    #     plt.plot(freq_grid, np.interp(freq_grid, calib.freq_list, calib.y_freq_points), '-o', label=f'y')
    #     plt.plot(freq_grid, np.interp(freq_grid, calib.freq_list, calib.z_freq_points), '-o', label=f'z')
    #     plt.title(f"Linear interpolation for {calib.sensor_id} sensor")
    #     plt.xlabel("frequency")
    #
    #     plt.subplot(4, 5, i + 11)
    #     plt.plot(calib.amplitude_list, calib.x_amplitude_points, '-o', label=f'x')
    #     plt.plot(calib.amplitude_list, calib.y_amplitude_points, '-o', label=f'y')
    #     plt.plot(calib.amplitude_list, calib.z_amplitude_points, '-o', label=f'z')
    #     plt.title(f"Amplitude calibration data for {calib.sensor_id} sensor")
    #     plt.xlabel("amplitude")
    #
    #     plt.subplot(4, 5, i + 16)
    #     plt.plot(amp_grid, np.interp(amp_grid, calib.amplitude_list, calib.x_amplitude_points), '-o', label=f'x')
    #     plt.plot(amp_grid, np.interp(amp_grid, calib.amplitude_list, calib.y_amplitude_points), '-o', label=f'y')
    #     plt.plot(amp_grid, np.interp(amp_grid, calib.amplitude_list, calib.z_amplitude_points), '-o', label=f'z')
    #     plt.title(f"Linear interpolation for {calib.sensor_id} sensor")
    #
    #     plt.legend()
    #     plt.xlabel("amplitude")
    #     plt.ylabel("factor")
    #
    # plt.show()
