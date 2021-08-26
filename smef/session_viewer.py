# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'session_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_session_viewer(object):
    def setupUi(self, session_viewer):
        session_viewer.setObjectName("session_viewer")
        session_viewer.resize(1190, 865)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(session_viewer)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.viewer_vertical_layout = QtWidgets.QVBoxLayout()
        self.viewer_vertical_layout.setObjectName("viewer_vertical_layout")
        self.viewer_custom_plot = CustomPlot(session_viewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewer_custom_plot.sizePolicy().hasHeightForWidth())
        self.viewer_custom_plot.setSizePolicy(sizePolicy)
        self.viewer_custom_plot.setObjectName("viewer_custom_plot")
        self.viewer_vertical_layout.addWidget(self.viewer_custom_plot)
        self.horizontalLayout_3.addLayout(self.viewer_vertical_layout)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.groupBox_6 = QtWidgets.QGroupBox(session_viewer)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.viewer_tittle_line_edit = QtWidgets.QLineEdit(self.groupBox_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewer_tittle_line_edit.sizePolicy().hasHeightForWidth())
        self.viewer_tittle_line_edit.setSizePolicy(sizePolicy)
        self.viewer_tittle_line_edit.setMaximumSize(QtCore.QSize(380, 16777215))
        self.viewer_tittle_line_edit.setObjectName("viewer_tittle_line_edit")
        self.verticalLayout_9.addWidget(self.viewer_tittle_line_edit)
        self.verticalLayout_5.addWidget(self.groupBox_6)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.groupBox = QtWidgets.QGroupBox(session_viewer)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.session_description_browser = QtWidgets.QTextBrowser(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.session_description_browser.sizePolicy().hasHeightForWidth())
        self.session_description_browser.setSizePolicy(sizePolicy)
        self.session_description_browser.setMaximumSize(QtCore.QSize(16777215, 150))
        self.session_description_browser.setObjectName("session_description_browser")
        self.verticalLayout.addWidget(self.session_description_browser)
        self.verticalLayout_6.addWidget(self.groupBox)
        self.viewer_minmax_values_table = QtWidgets.QTableWidget(session_viewer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.viewer_minmax_values_table.sizePolicy().hasHeightForWidth())
        self.viewer_minmax_values_table.setSizePolicy(sizePolicy)
        self.viewer_minmax_values_table.setMinimumSize(QtCore.QSize(350, 250))
        self.viewer_minmax_values_table.setMaximumSize(QtCore.QSize(350, 230))
        self.viewer_minmax_values_table.setObjectName("viewer_minmax_values_table")
        self.viewer_minmax_values_table.setColumnCount(3)
        self.viewer_minmax_values_table.setRowCount(5)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setVerticalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setVerticalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setVerticalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.viewer_minmax_values_table.setHorizontalHeaderItem(2, item)
        self.viewer_minmax_values_table.horizontalHeader().setDefaultSectionSize(80)
        self.viewer_minmax_values_table.horizontalHeader().setMinimumSectionSize(30)
        self.viewer_minmax_values_table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_6.addWidget(self.viewer_minmax_values_table)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem2)
        self.groupBox_3 = QtWidgets.QGroupBox(session_viewer)
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.s1_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.s1_legend_checkbox.setObjectName("s1_legend_checkbox")
        self.horizontalLayout.addWidget(self.s1_legend_checkbox)
        self.checkBos2_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBos2_legend_checkbox.setObjectName("checkBos2_legend_checkbox")
        self.horizontalLayout.addWidget(self.checkBos2_legend_checkbox)
        self.s3_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.s3_legend_checkbox.setObjectName("s3_legend_checkbox")
        self.horizontalLayout.addWidget(self.s3_legend_checkbox)
        self.s4_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.s4_legend_checkbox.setObjectName("s4_legend_checkbox")
        self.horizontalLayout.addWidget(self.s4_legend_checkbox)
        self.s5_legend_checkbox = QtWidgets.QCheckBox(self.groupBox_3)
        self.s5_legend_checkbox.setObjectName("s5_legend_checkbox")
        self.horizontalLayout.addWidget(self.s5_legend_checkbox)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout_6.addWidget(self.groupBox_3)
        self.groupBox_2 = QtWidgets.QGroupBox(session_viewer)
        self.groupBox_2.setMaximumSize(QtCore.QSize(380, 16777215))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.units_rbutton1 = QtWidgets.QRadioButton(self.groupBox_2)
        self.units_rbutton1.setChecked(True)
        self.units_rbutton1.setObjectName("units_rbutton1")
        self.verticalLayout_3.addWidget(self.units_rbutton1)
        self.units_rbutton2 = QtWidgets.QRadioButton(self.groupBox_2)
        self.units_rbutton2.setChecked(False)
        self.units_rbutton2.setObjectName("units_rbutton2")
        self.verticalLayout_3.addWidget(self.units_rbutton2)
        self.units_rbutton3 = QtWidgets.QRadioButton(self.groupBox_2)
        self.units_rbutton3.setObjectName("units_rbutton3")
        self.verticalLayout_3.addWidget(self.units_rbutton3)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        self.groupBox_5 = QtWidgets.QGroupBox(session_viewer)
        self.groupBox_5.setObjectName("groupBox_5")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.viewer_norma_checkbox = QtWidgets.QCheckBox(self.groupBox_5)
        self.viewer_norma_checkbox.setObjectName("viewer_norma_checkbox")
        self.horizontalLayout_9.addWidget(self.viewer_norma_checkbox)
        self.viewer_norma_val_spinbox = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.viewer_norma_val_spinbox.setDecimals(4)
        self.viewer_norma_val_spinbox.setMinimum(-1000.0)
        self.viewer_norma_val_spinbox.setMaximum(1000.0)
        self.viewer_norma_val_spinbox.setObjectName("viewer_norma_val_spinbox")
        self.horizontalLayout_9.addWidget(self.viewer_norma_val_spinbox)
        self.viewer_norma_unit_label = QtWidgets.QLabel(self.groupBox_5)
        self.viewer_norma_unit_label.setObjectName("viewer_norma_unit_label")
        self.horizontalLayout_9.addWidget(self.viewer_norma_unit_label)
        self.label_4 = QtWidgets.QLabel(self.groupBox_5)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_9.addWidget(self.label_4)
        self.marker_checkbox = QtWidgets.QCheckBox(self.groupBox_5)
        self.marker_checkbox.setChecked(True)
        self.marker_checkbox.setObjectName("marker_checkbox")
        self.horizontalLayout_9.addWidget(self.marker_checkbox)
        self.verticalLayout_6.addWidget(self.groupBox_5)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem3)
        self.groupBox_4 = QtWidgets.QGroupBox(session_viewer)
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.viewer_copy_graph_button = QtWidgets.QPushButton(self.groupBox_4)
        self.viewer_copy_graph_button.setObjectName("viewer_copy_graph_button")
        self.horizontalLayout_8.addWidget(self.viewer_copy_graph_button)
        self.viewer_copy_data_button = QtWidgets.QPushButton(self.groupBox_4)
        self.viewer_copy_data_button.setObjectName("viewer_copy_data_button")
        self.horizontalLayout_8.addWidget(self.viewer_copy_data_button)
        self.verticalLayout_6.addWidget(self.groupBox_4)
        self.horizontalLayout_3.addLayout(self.verticalLayout_6)

        self.retranslateUi(session_viewer)
        QtCore.QMetaObject.connectSlotsByName(session_viewer)

    def retranslateUi(self, session_viewer):
        _translate = QtCore.QCoreApplication.translate
        session_viewer.setWindowTitle(_translate("session_viewer", "Просмотр сеанса"))
        self.groupBox_6.setTitle(_translate("session_viewer", "Заголовок графика"))
        self.groupBox.setTitle(_translate("session_viewer", "Описание сессии"))
        item = self.viewer_minmax_values_table.verticalHeaderItem(0)
        item.setText(_translate("session_viewer", "Датчик 1"))
        item = self.viewer_minmax_values_table.verticalHeaderItem(1)
        item.setText(_translate("session_viewer", "Датчик 2"))
        item = self.viewer_minmax_values_table.verticalHeaderItem(2)
        item.setText(_translate("session_viewer", "Датчик 3"))
        item = self.viewer_minmax_values_table.verticalHeaderItem(3)
        item.setText(_translate("session_viewer", "Датчик 4"))
        item = self.viewer_minmax_values_table.verticalHeaderItem(4)
        item.setText(_translate("session_viewer", "Датчик 5"))
        item = self.viewer_minmax_values_table.horizontalHeaderItem(0)
        item.setText(_translate("session_viewer", "Мин."))
        item = self.viewer_minmax_values_table.horizontalHeaderItem(1)
        item.setText(_translate("session_viewer", "Средн."))
        item = self.viewer_minmax_values_table.horizontalHeaderItem(2)
        item.setText(_translate("session_viewer", "Макс."))
        self.groupBox_3.setTitle(_translate("session_viewer", "Отображение графиков"))
        self.s1_legend_checkbox.setText(_translate("session_viewer", "Д1"))
        self.checkBos2_legend_checkbox.setText(_translate("session_viewer", "Д2"))
        self.s3_legend_checkbox.setText(_translate("session_viewer", "Д3"))
        self.s4_legend_checkbox.setText(_translate("session_viewer", "Д4"))
        self.s5_legend_checkbox.setText(_translate("session_viewer", "Д5"))
        self.groupBox_2.setTitle(_translate("session_viewer", "Единицы измерения"))
        self.units_rbutton1.setText(_translate("session_viewer", "В/м"))
        self.units_rbutton2.setText(_translate("session_viewer", "дБмкВ/м"))
        self.units_rbutton3.setText(_translate("session_viewer", "Вт/м2"))
        self.groupBox_5.setTitle(_translate("session_viewer", "Параметры нормы и маркеров"))
        self.viewer_norma_checkbox.setText(_translate("session_viewer", "Норма"))
        self.viewer_norma_unit_label.setText(_translate("session_viewer", "В/м"))
        self.label_4.setText(_translate("session_viewer", "            "))
        self.marker_checkbox.setText(_translate("session_viewer", "Маркеры данных"))
        self.groupBox_4.setTitle(_translate("session_viewer", "Копирование данных"))
        self.viewer_copy_graph_button.setText(_translate("session_viewer", "Копировать график"))
        self.viewer_copy_data_button.setText(_translate("session_viewer", "Копировать данные"))
from .CustomPlot import CustomPlot
