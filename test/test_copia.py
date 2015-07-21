# -*- coding: utf-8 -*-
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMenu


# Initialize Qt resources from file resources.py
import sys, os
# add path
sys.path.append('C:\Users\iacopo.borsi\.qgis2\python\plugins\Freewat')
# import QspatiaLite classes and methods
#from Database import Database



# Import the code for the dialog
import copyFromVector_dialog as cDialog


# Input parameters
#qd = QDialog()
dlg = cDialog.CopyFromVector(iface)


# show the dialog
dlg.show()
# Run the dialog event loop
dlg.exec_()


