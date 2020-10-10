import sys

from Qt import QtWidgets

import QtColorTool as qct

#*****************************************************************************************
# START #*********************************************************************************
# Loads the tool directly in Python
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tool_sets = qct.QtColorTool()
    app.exec_()