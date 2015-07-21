# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Freewat
                                 A QGIS plugin
 Build and Run MODFLOW models
                              -------------------
        begin                : 2015-01-06
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Iacopo Borsi TEA Sistemi
        email                : iac
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QMenu
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
import createModelLayer_dialog as mlDialog
import createModel_dialog as mdDialog
import createCHDLayer_dialog as chdDialog
import createWELLayer_dialog as welDialog
import createRCHLayer_dialog as rchDialog
import createRIVLayer_dialog as rivDialog
import createModelBuilder_dialog as mbDialog
import viewOutput_dialog as outDialog
import addStressPeriod_dialog as spDialog
import copyFromVector_dialog as copyVectorDialog
import copyRasterToFields_dialog as copyRasterDialog
import createGrid_dialog as grDialog

import os.path


class Freewat:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Freewat_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)



        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'Freewat')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Freewat')
        self.toolbar.setObjectName(u'Freewat')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Freewat', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        self.menu = QMenu(self.iface.mainWindow())
        self.menu.setTitle("&FREEWAT")

        # Create Model
        self.actionCreateModel = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create New &Model", self.iface.mainWindow())
        self.actionCreateModel.setWhatsThis("Configuration for test plugin")
        self.actionCreateModel.setStatusTip("This is status tip")
        self.actionCreateModel.triggered.connect(self.runCreateModel)

        # Create Grid
        self.actionCreateGrid = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create A Model &Grid", self.iface.mainWindow())
        self.actionCreateGrid.setWhatsThis("Configuration for test plugin")
        self.actionCreateGrid.setStatusTip("This is status tip")
        self.actionCreateGrid.triggered.connect(self.runCreateGrid)

        # Create Model Layer
        self.actionCreateModelLayer = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create a &Model Layer", self.iface.mainWindow())
        self.actionCreateModelLayer.setWhatsThis("Configuration for test plugin")
        self.actionCreateModelLayer.setStatusTip("This is status tip")
        self.actionCreateModelLayer.triggered.connect(self.runCreateModelLayer)

        # Create CHD Layer
        self.actionCreateCHDLayer = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create a &CHD Layer", self.iface.mainWindow())
        self.actionCreateCHDLayer.setWhatsThis("Configuration for test plugin")
        self.actionCreateCHDLayer.setStatusTip("This is status tip")
        self.actionCreateCHDLayer.triggered.connect(self.runCreateCHD)

        # Create WEL Layer
        self.actionCreateWELlayer = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create a &WEL Layer", self.iface.mainWindow())
        self.actionCreateWELlayer.setWhatsThis("Configuration for test plugin")
        self.actionCreateWELlayer.setStatusTip("This is status tip")
        self.actionCreateWELlayer.triggered.connect(self.runCreateWEL)

        # Create RCH Layer
        self.actionCreateRCHLayer= QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create a &RCH Layer", self.iface.mainWindow())
        self.actionCreateRCHLayer.setWhatsThis("Configuration for test plugin")
        self.actionCreateRCHLayer.setStatusTip("This is status tip")
        self.actionCreateRCHLayer.triggered.connect(self.runCreateRCH)

        # Create RIV Layer
        self.actionCreateRIVLayer= QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Create a &RIV Layer", self.iface.mainWindow())
        self.actionCreateRIVLayer.setWhatsThis("Configuration for test plugin")
        self.actionCreateRIVLayer.setStatusTip("This is status tip")
        self.actionCreateRIVLayer.triggered.connect(self.runCreateRIV)

        # Copy from vector to vector
        self.actionCopyFromVec = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Copy from &Vector layer", self.iface.mainWindow())
        self.actionCopyFromVec.setWhatsThis("Configuration for test plugin")
        self.actionCopyFromVec.setStatusTip("This is status tip")
        self.actionCopyFromVec.triggered.connect(self.runCopyfromVecToVec)

        # Copy from raster to vector
        self.actionCopyFromRaster = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Copy from &Raster layer", self.iface.mainWindow())
        self.actionCopyFromRaster.setWhatsThis("Configuration for test plugin")
        self.actionCopyFromRaster.setStatusTip("This is status tip")
        self.actionCopyFromRaster.triggered.connect(self.runCopyfromRasterToVec)

        # Add a stress period
        self.actionStressPeriod = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "Add a &Stress Period", self.iface.mainWindow())
        self.actionStressPeriod.setWhatsThis("Configuration for test plugin")
        self.actionStressPeriod.setStatusTip("This is status tip")
        self.actionStressPeriod.triggered.connect(self.runAddStressPeriod)

        # Model Builder
        self.actionModelBuilder = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&Build and &Run a Model", self.iface.mainWindow())
        self.actionModelBuilder.setWhatsThis("Configuration for test plugin")
        self.actionModelBuilder.setStatusTip("This is status tip")
        self.actionModelBuilder.triggered.connect(self.runModelBuilder)

        # Model Output
        self.actionModelOutput = QAction(QIcon(":/plugins/Freewat/icons/icon.png"), "&View Model Output", self.iface.mainWindow())
        self.actionModelOutput.setWhatsThis("Configuration for test plugin")
        self.actionModelOutput.setStatusTip("This is status tip")
        self.actionModelOutput.triggered.connect(self.runOutputView)

        # Add Actions to Main Menu
        self.menu.addAction(self.actionCreateModel)

        # Add Actions to Main Menu
        self.menu.addAction(self.actionCreateGrid)

        # Add Sub-menu MDO to main Menu, and relatives Actions
        self.menu.createMDO_menu = QMenu(QCoreApplication.translate("FREEWAT", "Create a MDO"))
        self.menu.addMenu(self.menu.createMDO_menu)

        self.menu.createMDO_menu.addAction(self.actionCreateModelLayer)
        self.menu.createMDO_menu.addAction(self.actionCreateCHDLayer)
        self.menu.createMDO_menu.addAction(self.actionCreateWELlayer)
        self.menu.createMDO_menu.addAction(self.actionCreateRCHLayer)
        self.menu.createMDO_menu.addAction(self.actionCreateRIVLayer)

        # Add Actions to Main Menu
        self.menu.addAction(self.actionStressPeriod)

        # Add Sub-menu TOOLS to main Menu, and relatives Actions
        self.menu.tools = QMenu(QCoreApplication.translate("FREEWAT", "Tools"))
        self.menu.addMenu(self.menu.tools)
        self.menu.tools.addAction(self.actionCopyFromVec)
        self.menu.tools.addAction(self.actionCopyFromRaster)

        # Add Actions to Main Menu
        self.menu.addAction(self.actionModelBuilder)

        # Add Actions to Main Menu
        self.menu.addAction(self.actionModelOutput)

        menuBar = self.iface.mainWindow().menuBar()
        menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menu)




    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&Freewat'),action)
            self.iface.removeToolBarIcon(action)

    def runCreateModel(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgMD = mdDialog.CreateModelDialog(self.iface)
        # show the dialog
        self.dlgMD.show()
        # Run the dialog event loop
        self.dlgMD.exec_()

    def runCreateGrid(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgGR = grDialog.QGridderDialog(self.iface)
        # show the dialog
        self.dlgGR.show()
        # Run the dialog event loop
        self.dlgGR.exec_()

    def runCreateModelLayer(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgML = mlDialog.CreateModelLayerDialog(self.iface)
        # show the dialog
        self.dlgML.show()
        # Run the dialog event loop
        self.dlgML.exec_()

    def runCreateCHD(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgCHD = chdDialog.CreateCHDLayerDialog(self.iface)
        # show the dialog
        self.dlgCHD.show()
        # Run the dialog event loop
        self.dlgCHD.exec_()

    def runCreateWEL(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgWEL = welDialog.CreateWELayerDialog(self.iface)
        # show the dialog
        self.dlgWEL.show()
        # Run the dialog event loop
        self.dlgWEL.exec_()

    def runCreateRCH(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgRCH = rchDialog.CreateRCHLayerDialog(self.iface)
        # show the dialog
        self.dlgRCH.show()
        # Run the dialog event loop
        self.dlgRCH.exec_()

    def runCreateRIV(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgRIV = rivDialog.CreateRIVLayerDialog(self.iface)
        # show the dialog
        self.dlgRIV.show()
        # Run the dialog event loop
        self.dlgRIV.exec_()

    def runAddStressPeriod(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgSP = spDialog.CreateAddSPDialog(self.iface)
        # show the dialog
        self.dlgSP.show()
        # Run the dialog event loop
        self.dlgSP.exec_()

    def runCopyfromVecToVec(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgVector = copyVectorDialog.CopyFromVector(self.iface)
        # show the dialog
        self.dlgVector.show()
        # Run the dialog event loop
        self.dlgVector.exec_()

    def runCopyfromRasterToVec(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgRaster = copyRasterDialog.copyRasterToFields(self.iface)
        # show the dialog
        self.dlgRaster.show()
        # Run the dialog event loop
        self.dlgRaster.exec_()



    def runModelBuilder(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgMB = mbDialog.ModelBuilderDialog(self.iface)
        # show the dialog
        self.dlgMB.show()
        # Run the dialog event loop
        self.dlgMB.exec_()

    def runOutputView(self):
        """Run method that performs all the real work"""
        # Create the dialog (after translation) and keep reference
        self.dlgOUT = outDialog.viewOutputDialog(self.iface)
        # show the dialog
        self.dlgOUT.show()
        # Run the dialog event loop
        self.dlgOUT.exec_()
