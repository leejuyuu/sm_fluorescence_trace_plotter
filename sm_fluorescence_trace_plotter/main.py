#  Copyright (C) 2020 Tzu-Yu Lee, National Taiwan University
#
#  This file (main.py) is part of SM_fluorescence_trace_plotter.
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
import numpy as np
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import (Qt, QUrl, QAbstractListModel, QAbstractTableModel,
                            QModelIndex, Slot)
import sm_fluorescence_trace_plotter.python_for_imscroll.imscrollIO
from collections import namedtuple


class TraceInfoModel(QAbstractListModel):

    def __init__(self):
        super(TraceInfoModel, self).__init__()
        entry = namedtuple('data_entry', ['key', 'value', 'is_editable'])
        self.data_list = [entry('key1', 'value1', False),
                          entry('key2', 'value2', True)]
        self.property_name_role = Qt.UserRole + 1
        self.value_role = Qt.UserRole + 2
        self.is_editable_role = Qt.UserRole + 3

    def rowCount(self, parent: QModelIndex=None) -> int:
        return len(self.data_list)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int=Qt.DisplayRole):
        if orientation == Qt.Vertical:
            return self.data_list[section].key
        else:
            return None

    def data(self, index:QModelIndex, role:int=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.data_list[index.row()].value
        elif role == Qt.EditRole:
            return self.data_list[index.row()].value
        elif role == Qt.BackgroundRole:
            # not finished
            return 0
        elif role == self.is_editable_role:
            return self.data_list[index.row()].is_editable
        elif role == self.property_name_role:
            return self.data_list[index.row()].key
        elif role == self.value_role:
            return self.data_list[index.row()].value
        else:
            return None

    def roleNames(self):
        role_names = super(TraceInfoModel, self).roleNames()
        role_names[self.is_editable_role] = b'isEditable'
        role_names[self.property_name_role] = b'propertyName'
        role_names[self.value_role] = b'value'
        return role_names

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEditable | Qt.ItemIsEnabled

    def setData(self, index: QModelIndex, value: typing.Any, role:int=None) -> bool:
        if index.isValid() and role == Qt.EditRole:
            row = index.row()
            self.data_list[row] = self.data_list[row]._replace(value=value)
            self.dataChanged.emit(index, index)
            return True
        return False

    @Slot()
    def debug(self):
        pass




class TraceModel(QAbstractTableModel):

    def __init__(self):
        super(TraceModel, self).__init__()
        xvalue = np.arange(0, 1000).reshape((1000, 1))
        data = np.random.standard_normal((1000, 3))
        data[500:, 0] += 5
        data[700:, 1] += 5
        data[800:, 2] += 5
        self.data_array = np.concatenate((xvalue, data), axis=1)

    def rowCount(self, parent: QModelIndex=None) -> int:
        return self.data_array.shape[0]

    def columnCount(self, parent: QModelIndex=None) -> int:
        return self.data_array.shape[1]

    def data(self, index: QModelIndex, role: int=Qt.DisplayRole):
        row = index.row()
        column = index.column()
        if role == Qt.DisplayRole:
            return self.data_array[row, column].item()
        elif role == Qt.EditRole:
            return self.data_array[row, column].item()
        else:
            return None



if __name__ == '__main__':
    trace_info_model = TraceInfoModel()
    trace_model = TraceModel()
    app = QApplication([])
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    rc = view.rootContext()
    rc.setContextProperty('traceInfoModel', trace_info_model)
    rc.setContextProperty('traceModel', trace_model)
    view.setSource(QUrl('./qml/main.qml'))
    view.show()
    sys.exit(app.exec_())
