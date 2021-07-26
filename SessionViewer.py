from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidgetItem
import session_viewer
import app_logger
import double_range_slider

logger = app_logger.get_logger(__name__)


class SessionViewer(QWidget, session_viewer.Ui_session_viewer):
    def __init__(self, **kwargs):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Просмотр сеанса')

        self.viewer_tittle_line_edit.textChanged.connect(self.set_title)

        self.slider = double_range_slider.RangeSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimumHeight(30)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.setLow(0)
        self.slider.setHigh(100)
        # self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.slider.sliderMoved.connect(self.update_plot)
        # QtCore.QObject.connect(slider, QtCore.SIGNAL('sliderMoved(int)'), echo)
        # self.slider.show()
        # self.slider.raise_()
        self.viewer_vertical_layout.addWidget(self.slider)

        self.data = kwargs.get('data', None)
        self.np_data = self.data.T.to_numpy()
        self.viewer_norma_checkbox.setChecked(True)
        self.viewer_norma_val_spinbox.setValue(kwargs.get('norma_val', 0))
        self.connected_sensors = [False, False, False, False, False]
        # print(self.data)
        self.get_connected_sensors()
        self.indices = [i for i, x in enumerate(self.connected_sensors) if x]
        self.viewer_custom_plot.pgcustom.legend.clear()
        self.data_len = len(self.np_data[0])
        print('len:', self.data_len)
        if self.data is not None:
            for i in range(len(self.np_data) - 1):
                if self.np_data[i+1] is not None:
                    # boolean mask for self.viewer_custom_plot.pgcustom.data_line array
                    [b for a, b in zip(self.connected_sensors, self.viewer_custom_plot.pgcustom.data_line) if a][i].setData(self.np_data[0], self.np_data[i+1])
                    self.viewer_custom_plot.pgcustom.legend.addItem(self.viewer_custom_plot.pgcustom.data_line[self.indices[i]], "Датчик " + str(self.indices[i] + 1))
                    # self.viewer_custom_plot.pgcustom.data_line[i].setData(np_data[0], np_data[i+1])
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='y', enable=True)
            self.viewer_custom_plot.pgcustom.enableAutoRange(axis='x', enable=True)
        else:
            print('empty data')

        # for i, row in self.table.iterrows():
        #     for j in range(self.viewer_minmax_values_table.columnCount()):
        #         self.viewer_minmax_values_table.setItem(i, j, QTableWidgetItem('{:.2f}'.format(row[j])))
                # self.minmax = np.row_stack((np.amin(self.data[1:], axis=1), np.mean(self.data[1:], axis=1),
                #                             np.amax(self.data[1:], axis=1)))

    def update_plot(self, low_range, high_range):
        for i in range(len(self.np_data) - 1):
            if self.np_data[i+1] is not None:
                # boolean mask for self.viewer_custom_plot.pgcustom.data_line array
                [b for a, b in zip(self.connected_sensors, self.viewer_custom_plot.pgcustom.data_line)
                 if a][i].setData(self.np_data[0][low_range*self.data_len//100:high_range*self.data_len//100],
                                  self.np_data[i+1][low_range*self.data_len//100:high_range*self.data_len//100])

    def get_connected_sensors(self):
        header = list(self.data)
        if 'Sensor1' in header:
            self.connected_sensors[0] = True
        if 'Sensor2' in header:
            self.connected_sensors[1] = True
        if 'Sensor3' in header:
            self.connected_sensors[2] = True
        if 'Sensor4' in header:
            self.connected_sensors[3] = True
        if 'Sensor5' in header:
            self.connected_sensors[4] = True


    def set_title(self):
        new_tittle = self.viewer_tittle_line_edit.text()
        item = self.viewer_custom_plot.pgcustom.getPlotItem()
        item.setTitle("<span style=\"color:black;font-size:30px\">" + new_tittle + "</span>")
