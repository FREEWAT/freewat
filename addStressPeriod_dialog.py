# -*- coding: utf-8 -*-

#******************************************************************************
#
# Freewat
# ---------------------------------------------------------
#
#
# Copyright (C) 2014 - 2015 Iacopo Borsi (iacopo.borsi@tea-group.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

#from ui_addStressPeriod import Ui_addStressPeriodDialog
import os
from PyQt4 import QtGui, uic
from freewat_utils    import getVectorLayerByName, getVectorLayerNames, getModelsInfoLists, getModelInfoByName
from pyspatialite import dbapi2 as sqlite3
#
FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_addStressPeriod.ui') )
#
#class CreateAddSPDialog  (QDialog, Ui_addStressPeriodDialog):
class CreateAddSPDialog  (QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.addSP)
        self.manageGui()
##
##
    def manageGui(self):
        self.cmbModelName.clear()
        layerNameList = getVectorLayerNames()
        self.cmbModelName.addItems(layerNameList)
        self.cmbState.addItems(['Steady State', 'Transient'])
##
    def restoreGui(self):
        self.progressBar.setFormat("%p%")
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.cancelButton.clicked.disconnect(self.stopProcessing)
        self.okButton.setEnabled(True)
##
    def addSP(self):

        # ------------ Load input data  ------------
        timetable = self.cmbModelName.currentText()
        # Retrieve the model name from timetable, formatted as 'modelname_timetable'
        modelname = timetable[10:]

        # Retrieve the modeltable layer and the working directory:
        layerNameList = getVectorLayerNames()

        # Remark: pathfile from model table and number of stress periods (nsp) from time table
        (pathfile, nsp ) = getModelInfoByName(modelName)


        dbname = pathfile + '/' + modelname + ".sqlite"
        # creating/connecting SQL database object
        con = sqlite3.connect(dbname)
        # con = sqlite3.connect(":memory:") if you want write it in RAM
        con.enable_load_extension(True)
        cur = con.cursor()

        # Retrieve data from GUI:
        length = float(self.txtLength.toPlainText())
        time_steps = int(self.txtTimeSteps.toPlainText())
        multiplier = float(self.txtMultiplier.toPlainText())
        state = self.cmbState.currentText()
        if state == 'Steady State':
            state = 'SS'
        else:
            state = 'TR'

        parameters = [length, time_steps, multiplier, state]
        sql4 = 'INSERT INTO %s'%timetable
        sql44 = sql4 + '   (length, ts, multiplier, state) VALUES (?, ?, ?, ?, ?, ?);'

        cur.execute(sql44, (parameters[0], parameters[1], parameters[2], parameters[3] ))

        # Close SpatiaLiteDB
        cur.close()
        # Save the changes
        con.commit()
        # Close connection
        con.close()

##

