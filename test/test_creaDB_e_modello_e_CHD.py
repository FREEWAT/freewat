# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMenu

from pyspatialite import dbapi2 as sqlite3

# Initialize Qt resources from file resources.py
import sys, os
# Add to python path the directory where the script resides.
#print __file__
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append("C:\Users\iacopo.borsi\Sviluppo_QGIS\Freewat")

# Import the function
from mdoCreate_utils import createModel
from sqlite_utils import uploadQgisVectorLayer

# Import the code for the dialog
import createModel_dialog as mdDialog
import createCHDLayer_dialog as chdDialog
import addStressPeriod_dialog as tmDialog


# Input parameters
workingDir = 'C:\Users\iacopo.borsi\Desktop\ '
modelname = 'bacinoSerchio'
modeltype = 'modflow' # 'sewat'
lengthString = 'm'
timeString = 'day'
isChild = 0

createModel(modelname, workingDir, modeltype, isChild, lengthString, timeString)

##
#
#qd0 = QDialog()
#dlgMD = mdDialog.CreateModelDialog(iface)

# show the dialog
#dlgMD.show()
# Run the dialog event loop
#dlgMD.exec_()

##
#
qd = QDialog()
dlgCHD = chdDialog.CreateCHDLayerDialog(iface)


# show the dialog
dlgCHD.show()
# Run the dialog event loop
dlgCHD.exec_()


qd = QDialog()
dlgTM = tmDialog.CreateAddSPDialog(iface)


# show the dialog
dlgTM.show()
# Run the dialog event loop
dlgTM.exec_()


