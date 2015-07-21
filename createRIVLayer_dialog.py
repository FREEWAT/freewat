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
import os
from PyQt4 import QtGui, uic
from freewat_utils    import getVectorLayerByName, getVectorLayerNames, fileDialog, getModelsInfoLists, getModelInfoByName
from mdoCreate_utils  import createRivLayer, createModelLayer

FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_createRIVLayer.ui') )

class CreateRIVLayerDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.createRiver)

        #csv browse button
        self.toolBrowseButton.clicked.connect(self.outFilecsv)

        self.manageGui()
##
##
    def manageGui(self):
        self.cmbGridLayer.clear()
        self.cmbModelName.clear()
        self.cmbRiverLayer.clear()
        layerNameList = getVectorLayerNames()

        (modelNameList, pathList) =  getModelsInfoLists(layerNameList)

        self.cmbModelName.addItems(modelNameList)
        self.cmbGridLayer.addItems(layerNameList)
        self.cmbRiverLayer.addItems(layerNameList)
##
##
	# function for the choose of the csv table
    def outFilecsv(self):
        (self.OutFilePath) = fileDialog(self)
        # if self.OutFilePath is None or self.encoding is None:
            # return

    def reject(self):
        QDialog.reject(self)

##
    def createRiver(self):

        # ------------ Load input data  ------------

        newName = self.lineNewLayerEdit.toPlainText()
        gridLayer = getVectorLayerByName(self.cmbGridLayer.currentText())
        riverLayer = getVectorLayerByName(self.cmbRiverLayer.currentText())
        modelName = self.cmbModelName.currentText()

        xyz = self.lineRiverSegment.toPlainText()
        width = self.lineWidth.toPlainText()
        layer = self.lineLayerNumber.toPlainText()

        width = float(width)


        # Remark: pathfile from model table and number of stress periods (nsp) from time table
        (pathfile, nsp ) = getModelInfoByName(modelName)

        # CSV table loader
        csvlayer = self.OutFilePath
        uri = QUrl.fromLocalFile(csvlayer)
        uri.addQueryItem("type","csv")
        uri.addQueryItem("geomType","none")
        # uri.addQueryItem("delimiter",",")
        # uri.addQueryItem("skipLines","0")
        # uri.addQueryItem("xField","field_1")
        # uri.addQueryItem("yField","field_2")
        csvl = QgsVectorLayer(uri.toString(), "River_params_" + modelName, "delimitedtext")
        if csvl.isValid():
			QgsMapLayerRegistry.instance().addMapLayer(csvl)


        # dbName
        dbName = pathfile + '/' + modelName + '.sqlite'

        # Create a River Layer, call the main funcion imported at the beginning of the file
        createRivLayer(newName, dbName, gridLayer, riverLayer, csvl, width, layer, xyz, nsp)

##

