from PyQt4.QtCore import *
from PyQt4.QtGui import *

#from ui_createModel import Ui_CreateModelDialog
import os
from PyQt4 import QtGui, uic
from freewat_utils import *
from mdoCreate_utils import createModel

#
FORM_CLASS, _ = uic.loadUiType(os.path.join( os.path.dirname(__file__), 'ui/ui_createModel.ui') )

#class CreateModelDialog(QDialog, Ui_CreateModelDialog):
class CreateModelDialog(QDialog, FORM_CLASS):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.createModel)

        self.tlBttnWorkingDir.clicked.connect(self.outFileDir)

        self.manageGui()

    def manageGui(self):
        self.cmbBxModelType.clear()

        # self.bxDBname.addItems(modelNameList)
        self.cmbBxModelType.addItems(['modflow', 'seewat'])
        self.cmbBxLengthUnit.addItems(['m', 'cm', 'ft', 'undefined'])
        self.cmbBxTimeUnit.addItems(['sec', 'min', 'hour', 'day', 'month', 'year', 'undefined'])


    def outFileDir(self):
        (self.OutFilePath, self.encoding) = dirDialog(self)
        if self.OutFilePath is None or self.encoding is None:
            return

    def restoreGui(self):
        self.progressBar.setFormat("%p%")
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(0)
        self.cancelButton.clicked.disconnect(self.stopProcessing)
        self.okButton.setEnabled(True)

    def createModel(self):
        modelName = self.bxDBname.toPlainText()
        modelType = self.cmbBxModelType.currentText()
        lengthString = self.cmbBxLengthUnit.currentText()
        timeString = self.cmbBxTimeUnit.currentText()
        workingDir = self.OutFilePath
        print 'Direttori recuperata ..... ' , workingDir
        isChild = 1.0
        messaggio = 'DB Model is saved in' + workingDir
        QtGui.QMessageBox.information(None, 'Information', '%s' % (messaggio))
        print 'DB is saved in' + workingDir
        createModel(modelName, workingDir, modelType, isChild, lengthString, timeString)

