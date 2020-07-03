#  Copyright (C) 2020 Tzu-Yu Lee, National Taiwan University
#
#  This file (trace_plotter.py) is part of SM_fluorescence_trace_plotter.
#
#  SM_fluorescence_trace_plotter is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SM_fluorescence_trace_plotter is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SM_fluorescence_trace_plotter.  If not, see <https://www.gnu.org/licenses/>.

"""This module is a GUI plotting tool for CoSMoS intensity data visualization.

This module reads """

import typing
import sys
from collections import namedtuple
from pathlib import Path
import numpy as np
import xarray as xr
import pandas as pd
import pyqtgraph as pg
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
from PySide2.QtQuickWidgets import QQuickWidget
from PySide2.QtWidgets import QApplication, QWidget, QGridLayout
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import (Qt, QUrl, QAbstractListModel, QAbstractTableModel,
                            QStringListModel, QModelIndex, Signal, Slot,
                            Property, QObject)
from sm_fluorescence_trace_plotter.python_for_imscroll.python_for_imscroll import (imscrollIO,
                                                                                   binding_kinetics,
                                                                                   visualization)


class TraceInfoModel(QAbstractListModel):
    """Stores information about the current trace and interacts with view.

    """
    def __init__(self, parameter_file_path):
        super(TraceInfoModel, self).__init__()
        self.parameter_file_path = parameter_file_path
        parameter_file = pd.ExcelFile(parameter_file_path)
        sheet_names = parameter_file.sheet_names
        self.sheet_model = QStringListModel(sheet_names[:-1])
        self.current_sheet = sheet_names[0]
        self.fov_model = QStringListModel()
        self.set_fov_list(parameter_file)
        self.current_molecule = 1
        self.max_molecule = 1
        self.set_data_list_storage()
        self.property_name_role = Qt.UserRole + 1
        self.value_role = Qt.UserRole + 2
        self.choose_delegate_role = Qt.UserRole + 3
        self.dataChanged.connect(self.update_current_molecule, Qt.UniqueConnection)

    def rowCount(self, parent: QModelIndex = None) -> int:
        """See base class."""
        return len(self.data_list)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """See base class."""
        if role == Qt.DisplayRole:
            return self.data_list[index.row()].value
        elif role == Qt.EditRole:
            return self.data_list[index.row()].value
        elif role == self.choose_delegate_role:
            return self.data_list[index.row()].chooseDelegate
        elif role == self.property_name_role:
            return self.data_list[index.row()].key
        elif role == self.value_role:
            return self.data_list[index.row()].value
        return None

    def roleNames(self):
        """See base class."""
        role_names = super(TraceInfoModel, self).roleNames()
        role_names[self.choose_delegate_role] = b'chooseDelegate'
        role_names[self.property_name_role] = b'propertyName'
        role_names[self.value_role] = b'value'
        return role_names

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """See base class."""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def setData(self, index: QModelIndex, value: typing.Any,
                role: int = None) -> bool:
        """See base class."""
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            if row == 2:  # molecule number
                value = int(value)
                if value == self.current_molecule:
                    return True
                if 1 <= value <= self.max_molecule:
                    self.data_list[row] = self.data_list[row]._replace(value=value)
                    self.dataChanged.emit(index, index)
            else:
                self.data_list[row] = self.data_list[row]._replace(value=value)
                self.dataChanged.emit(index, index)
            return True
        return False

    def set_category(self, value: str):
        """Set the molecule category entry in view to the input string value."""
        self.data_list[3] = self.data_list[3]._replace(value=value)
        index = self.createIndex(3, 0)
        self.dataChanged.emit(index, index)

    def set_max_molecule_number(self, number: int):
        """Set the maximum molecule number to the input int. Used by TraceModel"""
        self.max_molecule = number

    def update_current_molecule(self, topleft: QModelIndex, bottomright: QModelIndex,
                                role: list = None):
        """Connected to self.dataChanged signal. Update the current molecule
        number if it is changed."""
        if topleft == bottomright:  # Single element changed
            if topleft.row() == 2:  # Molecule number entry
                self.current_molecule = self.data_list[2].value
                self.molecule_changed.emit()

    def set_data_list_storage(self, molecule: int = None):
        """Setup the data storage for this list model."""
        if molecule is None:
            molecule = self.current_molecule
        # choose delegate enumeration is defined in main.qml
        entry = namedtuple('data_entry', ['key', 'value', 'chooseDelegate'])
        self.data_list = [entry('Sheet name', self.current_sheet, 2),
                          entry('Field of view', self.current_fov, 3),
                          entry('Molecule', molecule, 1),
                          entry('Category', '', 0)]

    def set_fov_list(self, parameter_file: pd.ExcelFile = None):
        """Set the FOV string list model from the given parameter file. An
        already opened ExcelFile can be passed as an argument."""
        if parameter_file is None:
            parameter_file = pd.ExcelFile(self.parameter_file_path)
        dfs = parameter_file.parse(sheet_name=self.current_sheet)
        fov_list = dfs['filename'].tolist()
        parameter_file.close()
        self.fov_model.setStringList(fov_list)
        self.current_fov = fov_list[0]

    @Slot()
    def onNextMoleculeButtonClicked(self):
        """Set molecule number entry to (current value + 1)"""
        molecule_index = self.createIndex(2, 0)
        self.setData(molecule_index, self.current_molecule + 1, Qt.EditRole)

    @Slot()
    def onPreviousMoleculeButtonClicked(self):
        """Set molecule number entry to (current value - 1)"""
        molecule_index = self.createIndex(2, 0)
        self.setData(molecule_index, self.current_molecule - 1, Qt.EditRole)

    @Slot(int)
    def onSheetComboActivated(self, index: int):
        """Changes current sheet to the selected value in view and reinitialize
        self. Notify the TraceModel to change its data.

        index: The index of the selected item in the ComboBox component."""
        activated_sheet = self.sheet_model.data(self.sheet_model.createIndex(index, 0))
        if activated_sheet != self.current_sheet:
            self.current_sheet = activated_sheet
            self.set_fov_list()
            self.current_molecule = 1
            self.set_data_list_storage()
            self.dataChanged.emit(self.createIndex(2, 0),
                                  self.createIndex(3, 0))
            self.trace_model_should_change_file.emit()

    @Slot(int)
    def onFovComboActivated(self, index: int):
        """Changes current FOV to the selected value in view and reinitialize
        self. Notify the TraceModel to change its data.

        index: The index of the selected item in the ComboBox component."""
        activated_fov = self.fov_model.data(self.fov_model.createIndex(index, 0))
        if activated_fov != self.current_fov:
            self.current_fov = activated_fov
            self.current_molecule = 1
            self.set_data_list_storage()
            self.dataChanged.emit(self.createIndex(2, 0),
                                  self.createIndex(3, 0))
            self.trace_model_should_change_file.emit()

    @Slot()
    def debug(self):
        breakpoint()

    def _read_sheet_model(self):
        return self.sheet_model

    def _read_fov_model(self):
        return self.fov_model

    @Signal
    def sheet_model_changed(self):
        pass

    @Signal
    def fov_model_changed(self):
        pass

    @Signal
    def molecule_changed(self):
        pass

    @Signal
    def trace_model_should_change_file(self):
        pass

    sheetModel = Property(QObject, _read_sheet_model, notify=sheet_model_changed)
    fovModel = Property(QObject, _read_fov_model, notify=fov_model_changed)


class TraceModel(QAbstractTableModel):
    """Trace Model"""

    def __init__(self, trace_info_model: TraceInfoModel):
        super(TraceModel, self).__init__()
        self.trace_info_model = trace_info_model
        self.trace_info_model.molecule_changed.connect(self.change_molecule, Qt.UniqueConnection)
        self.trace_info_model.trace_model_should_change_file.connect(self.change_file,
                                                                     Qt.UniqueConnection)
        self.datapath = imscrollIO.def_data_path()
        self.set_data_storage()

    def rowCount(self, parent: QModelIndex = None) -> int:
        """See base class."""
        return self.data_array.shape[0]

    def columnCount(self, parent: QModelIndex = None) -> int:
        """See base class."""
        return self.data_array.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """See base class."""
        aoi_data_array = self.data_array[:, :, self.trace_info_model.current_molecule-1]
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            return aoi_data_array[row, column].item()
        elif role == Qt.EditRole:
            return aoi_data_array[row, column].item()
        return None

    def get_category(self) -> typing.Union[str, None]:
        """Searches the current molecule in the AOI_catories dict and return the
        category (key). If the molecule is not found return None."""
        molecule = self.trace_info_model.current_molecule
        found = False
        for key, value in self.AOI_categories.items():
            if found is True:
                break
            if key == 'analyzable':
                for key2, value2 in self.AOI_categories['analyzable'].items():
                    if molecule in value2:
                        category = key2
                        found = True
                        break
            else:
                if molecule in value:
                    category = key
                    found = True
                    break
        if found:
            return category
        return None

    def map_data_to_model_storage(self):
        """Map the xarray dataset to np 2D array which can be read by this model.

        Reorganize the time, intensity, and viterbi path in the data xarray
        to np array with columns correspond to times and row indices corresponds
        to the repetition of [time, intensity, viterbi path]. The order of
        channels is specified in the dict row_color."""
        outlist = []
        self.row_color = dict()
        i = 0
        for channel in self.channels:
            channel_data = self.data_xr.sel(channel=channel)
            out = xr.concat((channel_data.time,
                             channel_data.intensity,
                             channel_data.viterbi_path.sel(state='position')),
                            dim='').values
            outlist.append(out)
            self.row_color[i] = channel
            i += 3
        self.data_array = np.concatenate(outlist)

    def change_molecule(self):
        """Notifies the data model that the current molecule is changed.

        Connected to the TraceInfoModel.molecule_changed signal. Also updates
        the category entry."""
        category = self.get_category()
        self.trace_info_model.set_category(category)
        self.notify_whole_table_changed()

    def set_data_storage(self):
        """Reads trace data from _all.json file and store as attributes. Updates
        the model to the loaded data."""
        try:
            all_data, self.AOI_categories = binding_kinetics.load_all_data(
                self.datapath / (self.trace_info_model.current_fov + '_all.json'))
        except FileNotFoundError:
            print('file not found')
        category = self.get_category()
        self.trace_info_model.set_category(category)
        self.data_xr = all_data['data']
        self.channels = [self.data_xr.target_channel] + self.data_xr.binder_channel
        self.map_data_to_model_storage()
        self.trace_info_model.set_max_molecule_number(len(self.data_xr.AOI))

    def change_file(self):
        """Updates the data model when switching to another data file.

        Connected to the TraceInfoModel.trace_model_should_change_file signal."""
        self.set_data_storage()
        self.notify_whole_table_changed()

    def notify_whole_table_changed(self):
        """Emits dataChanged signal on the whole table to update the view """
        topleft = self.createIndex(0, 0)
        bottomright = self.createIndex(self.rowCount(), self.columnCount())
        self.dataChanged.emit(topleft, bottomright)

    @Slot(int, result=str)
    def get_row_color(self, row: int = 0) -> str:
        """Returns the corresponding channel name (color) to the input row
        number of the table model."""
        return self.row_color[row]

    @Slot()
    def save_fig(self):
        """Save matplotlib traces plot of the current molecule as SVG file."""
        current_molecule = self.trace_info_model.current_molecule
        category = self.get_category()
        current_molecule_data = self.data_xr.sel(AOI=current_molecule)
        fov_dir = self.datapath / self.trace_info_model.current_fov
        if not fov_dir.exists():
            fov_dir.mkdir()
        visualization.plot_one_trace_and_save(current_molecule_data, category,
                                              fov_dir, save_format='svg')


class TracePlot(pg.GraphicsLayoutWidget):
    def __init__(self, model: TraceModel):
        super().__init__()
        self.data_model = model
        self.data_model.dataChanged.connect(self.update)
        # xkcd purple blue,[tried green]
        pens = {'blue': pg.mkPen(color='#632de9', width=2),
                'green': pg.mkPen(color='#14C823', width=2),
                'red': pg.mkPen(color='#e50000', width=2)}
        self.plots = {channel: self.addPlot(row=row, col=0)
                      for row, channel in enumerate(self.data_model.channels)}
        self.int_curves = {channel: plot.plot(pen=pens[channel])
                           for channel, plot in self.plots.items()}
        self.state_curves = {channel: plot.plot(pen=pg.mkPen(color='k', width=3))
                             for channel, plot in self.plots.items()}
        self.update()


    def update(self):
        molecule = self.data_model.trace_info_model.current_molecule
        for channel in self.data_model.channels:
            data = self.data_model.data_xr.sel(channel=channel, AOI=molecule)
            self.int_curves[channel].setData(data.time, data.intensity)
            self.state_curves[channel].setData(data.time, data.viterbi_path.sel(state='position'))



def main():
    """Starts the GUI window after asking for the parameter file."""
    parameter_file_path = imscrollIO.get_xlsx_parameter_file_path()
    trace_info_model = TraceInfoModel(parameter_file_path)
    trace_model = TraceModel(trace_info_model)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    window = QWidget()
    view = QQuickWidget()
    view.setResizeMode(QQuickWidget.SizeRootObjectToView)
    root_context = view.rootContext()
    root_context.setContextProperty('traceInfoModel',
                                    trace_model.trace_info_model)
    root_context.setContextProperty('traceModel', trace_model)
    qml_path = Path(__file__).parent / 'qml/main.qml'
    view.setSource(QUrl(str(qml_path)))

    layout = QGridLayout()
    plot = TracePlot(model=trace_model)
    layout.addWidget(plot, 0, 0)
    layout.addWidget(view, 0, 1)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
