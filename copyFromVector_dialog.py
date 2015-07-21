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

import os
from PyQt4 import QtGui, uic

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *

#from ui_copyFromVector import Ui_CopyFromVectorDialog

from freewat_utils  import getVectorLayerByName, getVectorLayerNames, copyVectorFields, getFieldNames

#
#
FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_copyFromVector.ui') )

#
class CopyFromVector(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.copyFunction)

        self.cmbLayerFrom.currentIndexChanged.connect(self.reloadFieldsFrom)
        self.cmbLayerTo.currentIndexChanged.connect(self.reloadFieldsTo)

        self.manageGui()

##
##
    def manageGui(self):
        self.cmbLayerFrom.clear()
        self.cmbLayerTo.clear()

        layerNameList = getVectorLayerNames()

        self.cmbLayerFrom.addItems(layerNameList)
        self.cmbLayerTo.addItems(layerNameList)
        fromLay = getVectorLayerByName(self.cmbLayerFrom.currentText())
        toLay = getVectorLayerByName(self.cmbLayerTo.currentText())

        self.cmbFieldFrom_1.addItems(getFieldNames(fromLay))
        self.cmbFieldTo_1.addItems(getFieldNames(toLay))

##
    def reloadFieldsFrom(self):
        fromLay = getVectorLayerByName(self.cmbLayerFrom.currentText())
        self.cmbFieldFrom_1.clear()
        self.cmbFieldFrom_1.addItems(getFieldNames(fromLay))
        self.cmbFieldFrom_2.clear()
        self.cmbFieldFrom_2.addItem(' ')
        self.cmbFieldFrom_2.addItems(getFieldNames(fromLay))
        self.cmbFieldFrom_3.clear()
        self.cmbFieldFrom_3.addItem(' ')
        self.cmbFieldFrom_3.addItems(getFieldNames(fromLay))
        self.cmbFieldFrom_4.clear()
        self.cmbFieldFrom_4.addItem(' ')
        self.cmbFieldFrom_4.addItems(getFieldNames(fromLay))
        self.cmbFieldFrom_5.clear()
        self.cmbFieldFrom_5.addItem(' ')
        self.cmbFieldFrom_5.addItems(getFieldNames(fromLay))
##
    def reloadFieldsTo(self):
        toLay = getVectorLayerByName(self.cmbLayerTo.currentText())
        self.cmbFieldTo_1.clear()
        self.cmbFieldTo_1.addItems(getFieldNames(toLay))
        self.cmbFieldTo_2.clear()
        self.cmbFieldTo_2.addItem(' ')
        self.cmbFieldTo_2.addItems(getFieldNames(toLay))
        self.cmbFieldTo_3.clear()
        self.cmbFieldTo_3.addItem(' ')
        self.cmbFieldTo_3.addItems(getFieldNames(toLay))
        self.cmbFieldTo_4.clear()
        self.cmbFieldTo_4.addItem(' ')
        self.cmbFieldTo_4.addItems(getFieldNames(toLay))
        self.cmbFieldTo_5.clear()
        self.cmbFieldTo_5.addItem(' ')
        self.cmbFieldTo_5.addItems(getFieldNames(toLay))


##
    def copyFunction(self):
        # ------------ Load input data  ------------
        # Layer names
        progressBar = QProgressDialog("Copying fields...", " ",0,100)
        progressBar.setRange(0,100)
        progressBar.setValue(0)
        progressBar.show()
        progressBar.setValue(1)

        fromLay = getVectorLayerByName(self.cmbLayerFrom.currentText())
        toLay = getVectorLayerByName(self.cmbLayerTo.currentText())

        fieldList = [ (self.cmbFieldFrom_1.currentText(), self.cmbFieldTo_1.currentText() )  ]

        # Check if other fields have to be copied, and add them to the list, just in case.
        if  self.cmbFieldFrom_2.currentText() != ' ':
            fieldList.append( (self.cmbFieldFrom_2.currentText(), self.cmbFieldTo_2.currentText()) )
        if  self.cmbFieldFrom_3.currentText() != ' ':
            fieldList.append( (self.cmbFieldFrom_3.currentText(), self.cmbFieldTo_3.currentText()) )
        if  self.cmbFieldFrom_4.currentText() != ' ':
            fieldList.append( (self.cmbFieldFrom_4.currentText(), self.cmbFieldTo_4.currentText()) )
        if  self.cmbFieldFrom_5.currentText() != ' ':
            fieldList.append( (self.cmbFieldFrom_5.currentText(), self.cmbFieldTo_5.currentText()) )

        # Execute
        copyVectorFields(self.cmbLayerFrom.currentText(), self.cmbLayerTo.currentText(), fieldList)

        progressBar.setValue(100)


##

