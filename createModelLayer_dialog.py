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

#from ui_createModelLayer import Ui_CreateModelLayerDialog
import os
from PyQt4 import QtGui, uic

from freewat_utils    import getVectorLayerByName, getVectorLayerNames, getModelsInfoLists, getModelInfoByName
from mdoCreate_utils  import createModelLayer
from createGrid_utils import get_rgrid_nrow_ncol
#
#
FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_createModelLayer.ui') )
#
#class CreateModelLayerDialog(QDialog, Ui_CreateModelLayerDialog):
class CreateModelLayerDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.createMLayer)
        # self.cancelButton.clicked.connect(self.stopProcessing)
        self.manageGui()
##
##
    def manageGui(self):
        self.cmbGridLayer.clear()
        self.cmbModelName.clear()
        layerNameList = getVectorLayerNames()

        (modelNameList, pathList) =  getModelsInfoLists(layerNameList)

        self.cmbModelName.addItems(modelNameList)
        self.cmbGridLayer.addItems(layerNameList)
        self.cmbLayType.addItems(['confined','convertible'])
        self.cmbLayavg.addItems(['harmonic','logarithmic', 'arithmetic-mean'])
        self.cmbLaywet.addItems(['No','Yes'])

##
##
    def reject(self):
        QDialog.reject(self)
##
    def setProgressRange(self, maxValue):
        self.progressBar.setRange(0, maxValue)
##
    def updateProgress(self):
        self.progressBar.setValue(self.progressBar.value() + 1)
##
    def processFinished(self, statData):
        self.stopProcessing()

    def processInterrupted(self):
        self.restoreGui()

    def stopProcessing(self):
        if self.workThread is not None:
            self.workThread.stop()
            self.workThread = None
##
    def restoreGui(self):
        self.progressBar.setFormat("%p%")
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.cancelButton.clicked.disconnect(self.stopProcessing)
        self.okButton.setEnabled(True)
##
    def createMLayer(self, modeltable):

        # ------------ Load input data  ------------
        modelName = self.cmbModelName.currentText()
        #
        gridLayer = getVectorLayerByName(self.cmbGridLayer.currentText())
        # ------------ Model geometry ------------

        # Load model layer:
        layerName =  self.txtLayerName.toPlainText()
        top = self.txtTop.toPlainText()
        bottom = self.txtBottom.toPlainText()

        # Values for LPF table
        #layType     = 'convertible'
        layType     = self.cmbLayType.currentText()
        layAverage  = self.cmbLayavg.currentText()  #'harmonic'
        layWet      = self.cmbLaywet.currentText() #'off'

        # REMARK: Default value for CHANI is 1

        chani   = 1.0

        # Define values of new feature for LPF
        # --
        ft = [layerName, 1,2,3,4]
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
        if layWet == 'No':
            ft[4] = 0
        else:
            ft[4] = 1
        # --
        parameters = ft
        parameters.append(float(top))
        parameters.append(float(bottom))

       # Remark: pathfile from model table and number of stress periods (nsp) from time table
        (pathfile, nsp ) = getModelInfoByName(modelName)
        # Create a Model Layer

        createModelLayer(gridLayer, pathfile, modelName, layerName, parameters)

        # Retrieve the new layer from Map and insert correct values for BORDER.
        # BORDER =1   if cell is on a border line
        # else
        newlay = getVectorLayerByName(layerName)

        # Selection
        nrow, ncol =  get_rgrid_nrow_ncol(newlay)
        fieldIdx = newlay.dataProvider().fieldNameIndex('BORDER')

        newlay.startEditing()
        attributesDict = {}
        value = {fieldIdx : 1}

        for ft in newlay.getFeatures():
            if ft['COL'] == 1 or ft['COL'] == ncol or ft['ROW'] == 1 or ft['ROW'] == nrow :
                attributesDict[ft.id()] = value

        newlay.dataProvider().changeAttributeValues(attributesDict)
        newlay.commitChanges()

##

