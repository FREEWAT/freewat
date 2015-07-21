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

import numpy as np

#from ui_modelBuilder import Ui_ModelBuilderDialog
from freewat_utils    import getVectorLayerByName, getVectorLayerNames
from freewat_utils import fileDialog

import sys
import subprocess as sub

# load flopy and grid utils
from flopy.modflow import *
from flopy.utils import *
import createGrid_utils


#
#
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/ui_modelBuilder.ui'))


class ModelBuilderDialog(QtGui.QDialog, FORM_CLASS):
#class ModelBuilderDialog(QDialog, Ui_ModelBuilderDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.buildModel)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("Run")

        self.btnBrowse.clicked.connect(self.outFileDir)


        # self.cancelButton.clicked.connect(self.stopProcessing)
        self.manageGui()
##
##
    def manageGui(self):
        self.cmbModelName.clear()
        layerNameList = getVectorLayerNames()

        # Remark: here we assume the name of models table starts with "modeltable"
        modelNameList = []
        pathList = []
        for mName in layerNameList:
            if mName[0:10] == 'modeltable':
                modelNameTable = getVectorLayerByName(mName)
                for f in modelNameTable.getFeatures():
                    nameTemp = f['name']
                    pathTemp = f['working_dir']
                    modelNameList.append(nameTemp)
                    pathList.append(pathTemp)
# TO DO: inserire qui un messaggio di errore in caso di eccezione
##            else:
##                QMessageBox.warning(self, self.tr('No model'),
##                                self.tr('There is no model table in TOC '
##                                        'You have to create a MODEL before '
##                                        'running Model Layer Creation ' ))

        self.cmbModelName.addItems(modelNameList)
        self.cmbCHD.addItems(layerNameList)
        self.cmbWEL.addItems(layerNameList)
        self.cmbRCH.addItems(layerNameList)
        #
        self.rchopt_list = ['Recharge to top grid', 'Recharge layer defined in irch', 'Recharge to highest active cell']
        self.cmbRchOp.addItems(self.rchopt_list)
        #
        self.cmbRIV.addItems(layerNameList)
        #self.cmbGHB.addItems(layerNameList)


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
    def outFileDir(self):
        #(self.OutFilePath, self.encoding) = fileDialog(self)
        #if self.OutFilePath is None or self.encoding is None:
        #    return
        self.OutFilePath = fileDialog(self)
        self.txtDirectory.setText(self.OutFilePath)

##
    def restoreGui(self):
        self.progressBar.setFormat("%p%")
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.cancelButton.clicked.disconnect(self.stopProcessing)
        self.okButton.setEnabled(True)
##
    def buildModel(self, modeltable):

        # ------------ Load input MDO  ------------
        modelName = self.cmbModelName.currentText()
        #
        # -------- Load MODFLOW Directory
        modlflowdir = unicode(  self.OutFilePath )


        #
        # Load MDOs of selected Packages
        #
        if self.ckChd.isChecked():
            chdlayer = getVectorLayerByName(self.cmbCHD.currentText())
        #
        if self.ckWel.isChecked():
            wellayer = getVectorLayerByName(self.cmbWEL.currentText())
        #
        if self.ckRch.isChecked():
            rchlayer = getVectorLayerByName(self.cmbRCH.currentText())
        #
                #
        if self.ckRiv.isChecked():
            rivlayer = getVectorLayerByName(self.cmbRIV.currentText())
        #
##        if self.ckGHB.isChecked():
##            ghblayer = getVectorLayerByName(self.cmbGHB.currentTex())

        # ----------
        #
        layerNameList = getVectorLayerNames()

        # ------------ Build a Model ------------
        isok = 0
        for mName in layerNameList:
            # Retrieve the model table
            if mName == 'modeltable_'+modelName:
                isok = 1
                modelNameTable = getVectorLayerByName(mName)
                for f in modelNameTable.getFeatures():
                    pathFile =  f['working_dir']
                    modelType = f['type']
                    lenuni   = f['length_unit']
                    itmuni = f["time_unit"]

        ## Message Error if no model is found
##            if isok == 0:
##               QMessageBox.warning(self, self.tr('No model found!!'),
##                                self.tr('There is no model table in TOC '
##                                        'You have to create a MODEL before '
##                                        'running Model Layer Creation ' ))
##            # --
            # Retrieve the model time table and data for temporal discretization
            if mName == 'timetable_'+modelName:
                timetable = getVectorLayerByName(mName)

                # number of stress periods
                nper = 0 #timetable.featureCount()

                # Create lists of layers properties
                perlenList = []
                nstpList = []
                tsmultList =[]
                steadyList = []

                for ft in timetable.getFeatures():
                    nper = nper + 1
                    perlenList.append(ft['length'])
                    nstpList.append(ft['ts'])
                    tsmultList.append(ft['multiplier'])
                    state = ft['state']
                    if state == 'SS':
                        steadyList.append(True)
                    else:
                        steadyList.append(False)

                # --
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
        nrow, ncol =  createGrid_utils.get_rgrid_nrow_ncol(getVectorLayerByName(layNameList[0]))


        # delc, delrow
        delr, delc = createGrid_utils.get_rgrid_delr_delc(getVectorLayerByName(layNameList[0]))

        # Set TOP and Bottom(s), IBOUND, STRT, KX, KY, KZ
        modeltop  = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[0]), fieldName = 'TOP')
        # --
        botm = np.zeros(shape = (nlay, nrow, ncol))
        ibound = np.zeros(shape = (nlay, nrow, ncol))
        hstart = np.zeros(shape = (nlay, nrow, ncol))
        kx = np.zeros(shape = (nlay, nrow, ncol))
        ky = kx;
        kz = kx;

        for i in range(0,nlay):
            btemp = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[i]), fieldName = 'BOTTOM')
            botm[i, : ,: ] = btemp
            ibtemp = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[i]), fieldName = 'ACTIVE')
            ibound[i, : ,: ] = ibtemp
            hstemp = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[i]), fieldName = 'STRT')
            hstart[i, :, :] = hstemp
            kxtemp = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[i]), fieldName = 'KX')
            kytemp = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[i]), fieldName = 'KY')
            kztemp = createGrid_utils.get_param_array(getVectorLayerByName(layNameList[i]), fieldName = 'KZ')
            kx[i, :, : ] = kxtemp
            ky[i, :, : ] = kytemp
            kz[i, :, : ] = kztemp

        # Transfor list in array, if necessary
        laytyp = np.zeros(nlay)
        layavg = np.zeros(nlay)
        chani = np.zeros(nlay)
        laywet = np.zeros(nlay)
        layvka = np.zeros(nlay)

        for i in range (0,nlay):
            laytyp[i] = layTypeList[i]
            layavg[i] = layAvgList[i]
            chani[i] = layChaniList[i]
            laywet[i] = layWetList[i]
        #
        # ----
        # Retrieve data for CHD: a dictionary
        #
        if self.ckChd.isChecked():
            # Retrieve data for CHD: a triple list
            layer_row_column_data = {}

            for i in range(1,nper+1):
                bn = []
                for f in chdlayer.getFeatures():
                    fromlay =  f['from_lay']
                    tolay = f['to_lay']

                    shead = f[str(i) + '_shead']
                    ehead = f[str(i) + '_ehead']
                    nr = f['row'] - 1
                    nc = f['col'] - 1

                    for k in range(fromlay-1, tolay):
                        bcn = [k, nr, nc, shead, ehead]
                        bn.append(bcn)

            layer_row_column_data[i-1] = bn
            #layer_row_column_data = {0 : [ [1, 1, 1, 10, 10 ], [1, 2, 1, 10, 10 ], [1, 3, 1, 10, 10 ] ] }


        # ----
        # Retrieve data for WEL: a triple list
        #
        if self.ckWel.isChecked():
            layer_row_column_Q = {}
            for i in range(1,nper+1):
                wl = []
                for f in wellayer.getFeatures():
                    fromlay =  f['from_lay'] -1
                    tolay = f['to_lay'] - 1
                    # layer(s) where wel is applied

                    qwel = f['sp_' + str(i) ]
                    nr = f['row'] - 1
                    nc = f['col'] - 1

                    for k in range(fromlay, tolay + 1 ):
                        wlcn = [k, nr, nc, qwel]
                        wl.append(wlcn)

            layer_row_column_Q[i-1] = wl

        # ----
        # Retrieve data for RCH: a triple list
        #
        if self.ckRch.isChecked():
            rech_dict = {}
            irch_dict = {}
            for i in range(1,nper+1):
                rc = np.zeros(shape = (nrow,ncol))
                irc = np.zeros(shape = (nrow,ncol))
                for f in rchlayer.getFeatures():
                    nr = f['row'] - 1
                    nc = f['col'] - 1
                    rc[nr,nc] = f['sp_' + str(i) + '_rech']
                    irc[nr,nc] = f['sp_' + str(i) + '_irch']

                rech_dict[i-1] = rc
                irch_dict[i-1] = irc
        # Retrieve rch_option from GUI:

        optiontext = self.cmbRchOp.currentText()
        if optiontext == self.rchopt_list[0] :
            rch_option = 1
        if optiontext == self.rchopt_list[1] :
            rch_option = 2
        if optiontext == self.rchopt_list[2]:
            rch_option = 3

        # ----
        # Retrieve data for RIV:
        #
        if self.ckRiv.isChecked():
            riv_dict = {}
            for i in range(1,nper+1):
                rv = []
                for f in rivlayer.getFeatures():
                    layrv =  f['layer'] - 1
                    stg = f['stage_' + str(i) ]
                    rb = f['rbot_' + str(i) ]
                    cnd = f['cond_' + str(i) ]
                    nr = f['row'] - 1
                    nc = f['col'] - 1

                    rvlst = [layrv, nr, nc, stg, cnd, rb]
                    rv.append(rvlst)

            riv_dict[i-1] = rv


        # -------- New model
        exename = modlflowdir
        QtGui.QMessageBox.information(None, 'Information', exename )
        # TO DO: recuperare la versione a seconda del tipo di eseguibile!!!

        QtGui.QMessageBox.information(None, 'Stress period n.', str(nper))

        ml = Modflow(modelName, exe_name= modlflowdir, version='mf2005',silent=0 , model_ws = pathFile)
        #ml = Modflow(modelName, exe_name= 'mf2005', version='mf2005',silent=0 , model_ws = pathFile)


        # DIS (Discretization) package
        laycbd = 0

        discret = ModflowDis(ml,nlay=nlay, nrow=nrow, ncol=ncol, nper=nper, delr=delr, delc=delc, laycbd = laycbd, perlen=perlenList, top= modeltop, botm= botm, nstp=nstpList, tsmult=tsmultList, steady=steadyList, itmuni= itmuni , lenuni=lenuni)

        # BAS package
        bas = ModflowBas(ml,ibound=ibound,strt=hstart)

        # LPF (Layer-property Flow) package
        # Remark: by default, layvka = 0.0, so that VKA = KZ, a 3D array od vertical hydraulic conductivity, so vka = kz
        lpf = ModflowLpf(ml, laytyp = laytyp, layavg = layavg, chani=1.0, layvka = layvka, laywet= laywet, ilpfcb=53, hdry=-1e+30, iwdflg=0, wetfct=0.1, iwetit=1, ihdwet=0, hk=kx, hani= ky, vka=kz, ss=1e-05, sy=0.15, vkcb=0.0, wetdry=-0.01, storagecoefficient=False, constantcv=False, thickstrt=False, nocvcorrection=False, novfc=False, extension='lpf', unitnumber=15)

        # CHD (Fixed head boundary condition)
        if self.ckChd.isChecked():
            QtGui.QMessageBox.information(None, 'Information', str(layer_row_column_data ))

            chd = ModflowChd(ml, stress_period_data = layer_row_column_data, cosines=None, extension='chd', unitnumber=24)
            #chd = ModflowChd(ml, stress_period_data = {  0:[[2, 3, 4, 10., 10.1]] } , cosines=None, extension='chd', unitnumber=24)

        # WEL (WELL package)
        if self.ckWel.isChecked():
            #
            wel = ModflowWel(ml, stress_period_data = layer_row_column_Q )
            #wel = ModflowWel(ml, stress_period_data = {   0:[[2, 3, 4, -21.6]]   } )

        # RCH (RCH package)

        if self.ckRch.isChecked():
            rch = ModflowRch(ml, nrchop=rch_option, ipakcb=0, rech = rech_dict, irch = irch_dict, extension='rch', unitnumber=19)
            #rch = ModflowRch(ml, nrchop=rch_option, ipakcb=0, rech = 0.01, irch = irch_array, extension='rch', unitnumber=19)

        # RIV (RIVER package)
        if self.ckRiv.isChecked():
            #
            riv = ModflowRiv(ml, stress_period_data = riv_dict )

        # Output control package
        oc = ModflowOc(ml)

        # PCG package
        pcg = ModflowPcg(ml)

        # Write input files
        ml.write_input()

        # Run model
        # Remark: here the subprocess library is used directly, overpassing
        # the flopy method: ml.run_model(), which seems to fail.
        namefile = modelName + '.nam'
        sub.Popen([exename, namefile], cwd=pathFile)

        while True:
          line = proc.stdout.readline()
          if line != '':
            if 'normal termination of simulation' in line.lower():
                success = True
            #c = line.split('\r')
            c = line.rstrip('\r\n')
            if not silent:
                print c
            if report == True:
                buff.append(c)
          else:
            break
        if pause == True:
            raw_input('Press Enter to continue...')
        return ([success, buff])

##

