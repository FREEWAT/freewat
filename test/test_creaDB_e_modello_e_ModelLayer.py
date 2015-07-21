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
from mdoCreate_utils import createModel, createModelLayer
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





# Load model layers:
nomelayer1 =  'aquifer1'
##
top = 20.0
bottom = 0.0

# Values for LPF table
layType     = 'convertible'
layAverage  = 'harmonic'
chani   = 1.0
layWet  = 'off'

# Define values of new feature for LPF
# --
ft = [nomelayer1, 1,2,3,4]
# --
if layType == 'convertible':
    ft[1] = 1
else:
    ft[1] = 0
# --
if layAverage == 'harmonic':
    ft[2] = 0
elif layAverage == 'logarithmic':
    ft[2] = 1
else:
    ft[2] = 2
# --
ft[3] = chani
# --
if layWet == 'off':
    ft[4] = 0
else:
    ft[4] = 1
# --
parameters = ft
##parameters2 = []
##parameters2.append(nomelayer2)
##for j in range(1,len(ft)):
##    parameters2.append(ft[j])

# Create a Model Layer
# BE SELECTED IN THE QGIS LAYER LIST PANEL
gridLayer = qgis.utils.iface.activeLayer()

dbName = workingDir

createModelLayer(gridLayer, dbName, modelname, nomelayer1, parameters)

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
#