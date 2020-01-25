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

import sys
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import Qt, QUrl


if __name__ == '__main__':
    app = QApplication([])
    view = QQuickView()
    view.setResizeMode(QQuickView.SizeRootObjectToView)
    view.setSource(QUrl('./qml/main.qml'))
    view.show()
    sys.exit(app.exec_())
