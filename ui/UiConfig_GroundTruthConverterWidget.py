from enum import IntEnum
import PySide2.QtCore as QtC, PySide2.QtWidgets as QtW, PySide2.QtGui as QtG
from ui.Ui_GroundTruthConverterWidget import Ui_GroundTruthConverterWidget


__all__ = ['BaseGroundTruthConverterWidget']


class BaseGroundTruthConverterWidget(Ui_GroundTruthConverterWidget):
    class BasicMessageBoxType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    def adjustUi(self):
        self.statusbar = QtW.QStatusBar(self)
        self.layout().addWidget(self.statusbar)
        self.layout().setStretch(0, 1)
        self.layout().setStretch(1, 0)
        self.progressBar = QtW.QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)

    def initialize(self):
        self._currentStatusBarPriority = 0
        self.progressBar.reset()
        self.sourceFileLineEdit.setText('')
        self.categoryComboBox.clear()
        self.categoryLabel.setEnabled(False)
        self.categoryComboBox.setEnabled(False)
        self.convertOptionGroupBox.setEnabled(False)
        self.convertPushButton.setEnabled(False)
    @QtC.Slot(str, int)
    def messageDispathcer(self, msg, msgtype):
        if msgtype == 1:
            self.sendTextToStatusBar.emit(msg, -1, 3)
        elif msgtype == 2 or msgtype == 3:
            self.sendToMessageBox.emit(msg, msgtype)

    @QtC.Slot(int)
    def on_smoothBoundaryCheckBox_stateChanged(self, state):
        self.kernelShapeComboBox.setEnabled(state == QtC.Qt.Checked)
        self.boundaryHalfWidthSpinBox.setEnabled(state == QtC.Qt.Checked)
        self.boundarySmoothCoefDoubleSpinBox.setEnabled(state == QtC.Qt.Checked)

    @QtC.Slot(int)
    def on_centralizeRegionCheckBox_stateChanged(self, state):
        self.regionProbLowerBoundDoubleSpinBox.setEnabled(state == QtC.Qt.Checked)

    @QtC.Slot(str, int, int)
    def statusBarShowMessage(self, msg, timeout, priority):
        if priority >= self._currentStatusBarPriority:
            self.statusBar().showMessage(msg, timeout)
            if msg != '':
                self._currentStatusBarPriority = priority

    @QtC.Slot(str)
    def onStatusBarMessageChanged(self, msg):
        if msg == '':
            self._currentStatusBarPriority = 0

    @QtC.Slot(str, int)
    def openBasicMessageBox(self, msg, stype):
        if stype == self.BasicMessageBoxType.Information:
            QtW.QMessageBox.information(self, '提示', msg, QtW.QMessageBox.Ok)
        elif stype == self.BasicMessageBoxType.Warning:
            QtW.QMessageBox.warning(self, '警告', msg, QtW.QMessageBox.Ok)
        elif stype == self.BasicMessageBoxType.Critical:
            QtW.QMessageBox.critical(self, '错误', msg, QtW.QMessageBox.Ok)

    def statusBar(self):
        return self.statusbar

    @QtC.Slot(Exception)
    def workerExceptionHandler(self, e):
        raise e