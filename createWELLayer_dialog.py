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

#from ui_createWELLayer import Ui_CreateWELLayerDialog
import os
from PyQt4 import QtGui, uic
from freewat_utils    import getVectorLayerByName, getVectorLayerNames, getModelsInfoLists, getModelInfoByName
from mdoCreate_utils  import createWellLayer, createModelLayer
#
#
FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_createWELLayer.ui') )
#
#class CreateWELayerDialog(QDialog, Ui_CreateWELLayerDialog):
class CreateWELayerDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.createWEL)
        self.manageGui()
##
##
    def manageGui(self):
        self.cmbGridLayer.clear()
        self.cmbModelName.clear()
        layerNameList = getVectorLayerNames()

        # Retrieve modelname and pathfile List

        (modelNameList, pathList) =  getModelsInfoLists(layerNameList)


        self.cmbModelName.addItems(modelNameList)
        self.cmbGridLayer.addItems(layerNameList)
##
##
    def reject(self):
        QDialog.reject(self)
##
    def restoreGui(self):
        self.progressBar.setFormat("%p%")
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.cancelButton.clicked.disconnect(self.stopProcessing)
        self.okButton.setEnabled(True)
##
    def createWEL(self):

        # ------------ Load input data  ------------
        modelName = self.cmbModelName.currentText()
        #
        gridLayer = getVectorLayerByName(self.cmbGridLayer.currentText())

        # Remark: pathfile from model table and number of stress periods (nsp) from time table
        (pathfile, nsp ) = getModelInfoByName(modelName)


        # Retrieve the name of the new layer from Text Box
        name = self.textEdit.toPlainText()

        # Create a CHD Layer
        createWellLayer(gridLayer, name, pathfile, modelName, nsp)

##

