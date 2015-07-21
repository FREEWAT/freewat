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

import os, sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from pyspatialite import *




#aggiunte la classe getRasternames e getRasterByName
from freewat_utils import getVectorLayerByName, getVectorLayerNames, getFieldNames, getRasterNames, copyVectorFields, getRasterByName, copyRasterToField

#

FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_copyRasterToFields.ui') )


#
class copyRasterToFields(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

		#buttonBox è il pulsante OK - Cancel
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.copyFunction)
        self.cmbLayerTo.currentIndexChanged.connect(self.reloadFieldsTo)

        self.manageGui()

##
##
    def manageGui(self):
        self.cmbLayerFrom.clear()
        self.cmbLayerTo.clear()

        layerNameListRaster = getRasterNames()
        layerNameListVector = getVectorLayerNames()

        self.cmbLayerFrom.addItems(layerNameListRaster)
        self.cmbLayerTo.addItems(layerNameListVector)
        fromLay = getRasterByName(self.cmbLayerFrom.currentText())
        toLay = getVectorLayerByName(self.cmbLayerTo.currentText())

		#non serve più, è un raster e non ha elenco attributi
        #self.cmbFieldFrom_1.addItems(getFieldNames(fromLay))
		#per il vettore invece serve
        self.cmbFieldTo.addItems(getFieldNames(toLay))

##non serve più la lista dei campi del layer di partenza, è un raster
    #def reloadFieldsFrom(self):
        #fromLay = getVectorLayerByName(self.cmbLayerFrom.currentText())
        #self.cmbFieldFrom_1.clear()
        #self.cmbFieldFrom_1.addItems(getFieldNames(fromLay))
        #self.cmbFieldFrom_2.clear()
        #self.cmbFieldFrom_2.addItem(' ')
        #self.cmbFieldFrom_2.addItems(getFieldNames(fromLay))
        #self.cmbFieldFrom_3.clear()
        #self.cmbFieldFrom_3.addItem(' ')
        #self.cmbFieldFrom_3.addItems(getFieldNames(fromLay))
        #self.cmbFieldFrom_4.clear()
        #self.cmbFieldFrom_4.addItem(' ')
        #self.cmbFieldFrom_4.addItems(getFieldNames(fromLay))
        #self.cmbFieldFrom_5.clear()
        #self.cmbFieldFrom_5.addItem(' ')
        #self.cmbFieldFrom_5.addItems(getFieldNames(fromLay))

##unico campo in uscita per il vettore
    def reloadFieldsTo(self):
        toLay = getVectorLayerByName(self.cmbLayerTo.currentText())
        self.cmbFieldTo.clear()
        self.cmbFieldTo.addItems(getFieldNames(toLay))

##
    def copyFunction(self):
        # ------------ Load input data  ------------
        # Layer names
        progressBar = QProgressDialog("Copying fields...", " ",0,100)
        progressBar.setRange(0,100)
        progressBar.setValue(0)
        progressBar.show()


        #fromLay = getRasterByName(self.cmbLayerFrom.currentText())
        #toLay = getVectorLayerByName(self.cmbLayerTo.currentText())

        #fieldList = [ (self.cmbFieldFrom.currentText(), self.cmbFieldTo.currentText() ) ]


		#anche in questo caso non serve, il valore da copiare è solo uno
        # Check if other fields have to be copied, and add them to the list, just in case.
		#if  self.cmbFieldFrom_2.currentText() != ' ':
			#fieldList.append( (self.cmbFieldFrom_2.currentText(), self.cmbFieldTo_2.currentText()) )
		#if  self.cmbFieldFrom_3.currentText() != ' ':
			#fieldList.append( (self.cmbFieldFrom_3.currentText(), self.cmbFieldTo_3.currentText()) )
		#if  self.cmbFieldFrom_4.currentText() != ' ':
			#fieldList.append( (self.cmbFieldFrom_4.currentText(), self.cmbFieldTo_4.currentText()) )
		#if  self.cmbFieldFrom_5.currentText() != ' ':
			#fieldList.append( (self.cmbFieldFrom_5.currentText(), self.cmbFieldTo_5.currentText()) )

        # Execute
        copyRasterToField(self.cmbLayerTo.currentText(), self.cmbLayerFrom.currentText(),  self.cmbFieldTo.currentText())

        progressBar.setValue(100)


##

