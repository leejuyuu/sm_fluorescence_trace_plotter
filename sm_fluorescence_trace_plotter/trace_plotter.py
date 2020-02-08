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
#

"""main function"""

import typing
import sys
import os
from pathlib import Path
import numpy as np
import xarray as xr
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import (Qt, QUrl, QAbstractListModel, QAbstractTableModel,
                            QStringListModel, QModelIndex, Signal, Slot,
                            Property, QObject)
from sm_fluorescence_trace_plotter.python_for_imscroll import (imscrollIO,
                                                               binding_kinetics,
                                                               visualization)
from collections import namedtuple
import pandas as pd


# noinspection PyProtectedMember,PyProtectedMember
class TraceInfoModel(QAbstractListModel):

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
        return len(self.data_list)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
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
        else:
            return None

    def roleNames(self):
        role_names = super(TraceInfoModel, self).roleNames()
        role_names[self.choose_delegate_role] = b'chooseDelegate'
        role_names[self.property_name_role] = b'propertyName'
        role_names[self.value_role] = b'value'
        return role_names

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def setData(self, index: QModelIndex, value: typing.Any, role: int = None) -> bool:
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            if row == 2: #molecule number
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

    def set_category(self, value: str) -> bool:
        self.data_list[3] = self.data_list[3]._replace(value=value)
        index = self.createIndex(3, 0)
        self.dataChanged.emit(index, index)
        return False

    def set_max_molecule_number(self, number: int):
        self.max_molecule = number
        return None

    def refresh(self, topleft: QModelIndex, bottomright: QModelIndex,
                role: list = None):
        if role is None:
            role = list()
        if topleft == bottomright:
            if topleft.row() == 2:  # Molecule number
                self.current_molecule = self.data_list[2].value
                self.molecule_changed.emit()
        return None

    def set_data_list_storage(self, molecule: int = None):
        if molecule is None:
            molecule = self.current_molecule
        # choose delegate enumeration is defined in main.qml
        entry = namedtuple('data_entry', ['key', 'value', 'chooseDelegate'])
        self.data_list = [entry('Sheet name', self.current_sheet, 2),
                          entry('Field of view', self.current_fov, 3),
                          entry('Molecule', molecule, 1),
                          entry('Category', '', 0)]
        return None

    def set_fov_list(self, parameter_file: pd.ExcelFile = None):
        if parameter_file is None:
            parameter_file = pd.ExcelFile(self.parameter_file_path)
        dfs = parameter_file.parse(sheet_name=self.current_sheet)
        fov_list = dfs['filename'].tolist()
        parameter_file.close()
        self.fov_model.setStringList(fov_list)
        self.current_fov = fov_list[0]

    @Slot()
    def onNextMoleculeButtonClicked(self):
        molecule_index = self.createIndex(2, 0)
        self.setData(molecule_index, self.current_molecule + 1, Qt.EditRole)
        return None

    @Slot()
    def onPreviousMoleculeButtonClicked(self):
        molecule_index = self.createIndex(2, 0)
        self.setData(molecule_index, self.current_molecule - 1, Qt.EditRole)
        return None

    @Slot(int)
    def onSheetComboActivated(self, index: int):
        activated_sheet = self.sheet_model.data(self.sheet_model.createIndex(index, 0))
        if activated_sheet != self.current_sheet:
            self.current_sheet = activated_sheet
            self.set_fov_list()
            self.current_molecule = 1
            self.set_data_list_storage()
            self.dataChanged.emit(self.createIndex(2, 0),
                                  self.createIndex(3, 0))
            self.trace_model_should_change_file.emit()
        return None

    @Slot(int)
    def onFovComboActivated(self, index: int):
        activated_fov = self.fov_model.data(self.fov_model.createIndex(index, 0))
        if activated_fov != self.current_fov:
            self.current_fov = activated_fov
            self.current_molecule = 1
            self.set_data_list_storage()
            self.dataChanged.emit(self.createIndex(2, 0),
                                  self.createIndex(3, 0))
            self.trace_model_should_change_file.emit()
        return None

    @Slot()
    def debug(self):
        pass

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

    sheetModel = Property(QObject, read_sheet_model, notify=sheet_model_changed)
    fovModel = Property(QObject, read_fov_model, notify=fov_model_changed)


class TraceModel(QAbstractTableModel):

    def __init__(self, trace_info_model: TraceInfoModel):
        super(TraceModel, self).__init__()
        self.trace_info_model = trace_info_model
        self.trace_info_model.molecule_changed.connect(self.change_molecule, Qt.UniqueConnection)
        self.trace_info_model.trace_model_should_change_file.connect(self.change_file,
                                                                     Qt.UniqueConnection)
        self.datapath = imscrollIO.def_data_path()
        self.set_data_storage()

    def rowCount(self, parent: QModelIndex = None) -> int:
        return self.data_array.shape[0]

    def columnCount(self, parent: QModelIndex = None) -> int:
        return self.data_array.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        aoi_data_array = self.data_array[:, :, self.trace_info_model.current_molecule-1]
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            return aoi_data_array[row, column].item()
        elif role == Qt.EditRole:
            return aoi_data_array[row, column].item()
        else:
            return None

    def get_category(self) -> str:
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
        if not found:
            return None
        else:
            return category

    def map_data_to_model_storage(self):
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
        # noinspection PyAttributeOutsideInit
        self.data_array = np.concatenate(outlist)
        return True

    def change_molecule(self):
        category = self.get_category()
        self.trace_info_model.set_category(category)
        self.notify_whole_table_changed()
        return None

    def set_data_storage(self):
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
        self.set_data_storage()
        self.notify_whole_table_changed()
        return None

    def notify_whole_table_changed(self):
        topleft = self.createIndex(0, 0)
        bottomright = self.createIndex(self.rowCount(), self.columnCount())
        self.dataChanged.emit(topleft, bottomright)

    @Slot(int, result=str)
    def get_row_color(self, row: int = 0):
        return self.row_color[row]

    @Slot()
    def save_fig(self):
        current_molecule = self.trace_info_model.current_molecule
        category = self.get_category()
        current_molecule_data = self.data_xr.sel(AOI=current_molecule)
        fov_dir = self.datapath / self.trace_info_model.current_fov
        if not fov_dir.exists():
            fov_dir.mkdir()
        visualization.plot_one_trace_and_save(current_molecule_data, category,
                                              fov_dir, save_format='svg')
        return None


def main():
    """Starts the GUI window after asking for the parameter file."""
    parameter_file_path = imscrollIO.get_xlsx_parameter_file_path()
    trace_info_model = TraceInfoModel(parameter_file_path)
    trace_model = TraceModel(trace_info_model)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    rc = view.rootContext()
    rc.setContextProperty('traceInfoModel', trace_model.trace_info_model)
    rc.setContextProperty('traceModel', trace_model)
    rc.setContextProperty('aac', trace_info_model.sheet_model)
    qml_path = Path(__file__).parent / 'qml/main.qml'
    view.setSource(QUrl(str(qml_path)))
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
