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
#from ui_viewOutput import Ui_viewOutput
from freewat_utils    import getVectorLayerByName, getVectorLayerNames, getModelsInfoLists, getModelInfoByName
#
# load flopy and createGrid
from flopy.modflow import *
from flopy.utils import *
import createGrid_utils
#
FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_viewOutput.ui') )
#
class viewOutputDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.viewOutput)

        self.cmbModelName.currentIndexChanged.connect(self.reloadTime)
        # self.cmbStressPeriod.currentIndexChanged.connect(self.reloadSteps)
        # self.cancelButton.clicked.connect(self.stopProcessing)
        self.manageGui()

##
##
    def manageGui(self):
        self.cmbModelName.clear()
        layerNameList = getVectorLayerNames()

        (modelNameList, pathList) =  getModelsInfoLists(layerNameList)


        self.cmbModelName.addItems(modelNameList)



    def reloadTime(self):
        layerNameList = getVectorLayerNames()
        # Retrieve the model table
        isok = 0
        for mName in layerNameList:
            if mName == 'timetable_' + self.cmbModelName.currentText():
                timelayer = getVectorLayerByName(mName)
                ## TO DO:
                # The faster method is the following but it seems
                # that it counts only geom features, no one in time_table:
                # nsp = int(timelayer.featureCount())
                ftit = timelayer.getFeatures()
                nsp = 0
                #tslist = []
                for f in ftit:
                    nsp = nsp + 1
                    #tslist.append(f['time_steps'])

        SPitems = ['%s' % (i + 1) for i in range(nsp)]

        #self.listStressPeriod.addItems(SPitems)
        self.cmbStressPeriod.addItems(SPitems)
        #self.cmbStressPeriod.currentIndexChanged.connect(self.reloadSteps)
        self.txtTimeStep.setText('1')

##
    def viewOutput(self):

        # ------------ Load input data  ------------
        modelName = self.cmbModelName.currentText()
        kper = int(self.cmbStressPeriod.currentText())
        kstp = int(self.txtTimeStep.toPlainText())
        #

        # Remark: pathfile from modelltable
        layerNameList = getVectorLayerNames()

        for mName in layerNameList:
            if mName == 'modeltable_'+ modelName:
                modelNameTable = getVectorLayerByName(mName)
                for f in modelNameTable.getFeatures():
                    pathfile = f['working_dir']
                    print pathfile
        # Retrieve LPF table, and from there model layers and data needed for LPF
            if mName ==  "lpf_"+ modelName:
                lpftable = getVectorLayerByName(mName)
                # Number of layers
                nlay = 0
                # Get layers name from LPF table
                dpLPF = lpftable.dataProvider()

                # Create lists of layers properties
                layNameList = []
                layTypeList = []
                layAvgList = []
                layChaniList =[]
                layWetList = []

                for ft in lpftable.getFeatures():
                    attrs = ft.attributes()
                    layNameList.append(attrs[0])
                    layTypeList.append(attrs[1])
                    layAvgList.append(attrs[2])
                    layChaniList.append(attrs[3])
                    layWetList.append(attrs[4])
                    nlay = nlay + 1

                layersList = [layNameList, layTypeList, layAvgList, layChaniList, layWetList]

        # Spatial discretization:
        # Number of rows (along width)
        nrow, ncol = createGrid_utils.get_rgrid_nrow_ncol(getVectorLayerByName(layNameList[0]))
        # delc, delrow
        delr, delc = createGrid_utils.get_rgrid_delr_delc(getVectorLayerByName(layNameList[0]))

        # --- Post processing
        # Note you may have to set compiler type.
        # 'l' suits for OS X
        # mread = ModflowHdsRead(ml,compiler='l')
        #
        # USINg HeadFile object
        hdobj = HeadFile(pathfile+'/'+modelName+'.hds', text = 'head', precision='single')

        htot = hdobj.get_data(kstpkper = (kstp, kper))

        for ilay in range(0,nlay):
            fileName = pathfile+'/'+'rst_'+ 'lay_' + str(ilay +1) + '_' + modelName + '_' + str(kper)+ '_' + str(kstp) + '.asc'
            rstfile = open(fileName, 'w')
            # Data for this layer
            h11 = htot[ilay]
            # Header
            extent = getVectorLayerByName(layNameList[0]).extent()
            rstfile.write('NCOLS  %i \n'%ncol)
            rstfile.write('NROWS  %i \n'%nrow)
            rstfile.write('XLLCORNER  %f \n'%extent.xMinimum())
            rstfile.write('YLLCORNER  %f \n'%extent.yMinimum())
            rstfile.write('CELLSIZE   %f  \n'%delc)
            rstfile.write('NODATA_VALUE   -9999.0 \n')

            # Array of selected Head (kper, kstp)
            rstfile.write('NODATA_VALUE   -9999.0 \n')

            for j in range(0, len(h11)):
                for k in range(0, len(h11[j])):
                    rstfile.write(str(h11[j][k])+'  ')
                rstfile.write('\n')

            rstfile.close()


            fileInfo = QFileInfo(fileName)
            baseName = fileInfo.baseName()
            rlayer = QgsRasterLayer(fileName, baseName)
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)



##

