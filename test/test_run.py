# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMenu
# Initialize Qt resources from file resources.py
import sys, os
sys.path.append("C:\Users\iacopo.borsi\Sviluppo_QGIS\Freewat")
import resources
# Import the code for the dialog

import createModelLayer_dialog as mlDialog
from mdoCreate_utils import createModelTable
# Create Model Table
filePath = 'C:\Users\iacopo.borsi\Desktop'
workingDir = 'C:\Users\iacopo.borsi\Desktop'
modelname = 'tigro'
modeltype = 'modflow' # 'sewat'
lengthString = 'ft'
timeString = 'day'

createModelTable(modelname, modeltype, workingDir, lengthString, timeString)

# --
#
qd = QDialog()
dlgML = mlDialog.CreateModelLayerDialog(iface)


# show the dialog
dlgML.show()
# Run the dialog event loop
dlgML.exec_()
