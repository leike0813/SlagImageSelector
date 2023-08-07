from pathlib import Path
from enum import IntFlag
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG
from workers import IOWorker
from ui.UiConfig_GroundTruthConverterWidget import BaseGroundTruthConverterWidget


__all__ = ['GroundTruthConverterWidget']


class GroundTruthConverterWidget(BaseGroundTruthConverterWidget, QtW.QWidget):
    sendTextToStatusBar = QtC.Signal(str, int, int)
    sendToMessageBox = QtC.Signal(str, int)
    convertGroundTruthRequest = QtC.Signal(Path, str, str, int, float, float, list)

    def __init__(self, parent=None):
        super(GroundTruthConverterWidget, self).__init__(parent)
        self.worker = IOWorker(self)
        self.workerThread = QtC.QThread()
        self.worker.moveToThread(self.workerThread)

        self.currentSourceFld = Path.home()

        # --------------init procedure boilerplate---------------
        self.setupUi(self)
        self.adjustUi()
        self.connectSignalToSlot()
        self.initialize()
        # ------------------------------------------------------

    def connectSignalToSlot(self):
        self.sendTextToStatusBar.connect(self.statusBarShowMessage)
        self.sendToMessageBox.connect(self.openBasicMessageBox)
        self.statusBar().messageChanged.connect(self.onStatusBarMessageChanged)

        self.convertGroundTruthRequest.connect(self.worker.onConvertGroundTruthRequestReceived)

        self.worker.workerMessage.connect(self.messageDispathcer)
        self.worker.workerException.connect(self.workerExceptionHandler)
        self.worker.sendToProgressBar.connect(self.progressBar.setValue)
        self.worker.sendToProgressBarRange.connect(self.progressBar.setRange)

        self.worker.convertFinished.connect(self.centralWidget.setEnabled)

    def initialize(self):
        super(GroundTruthConverterWidget, self).initialize()
        self.sourceFile = None

    def showEvent(self, event):
        self.initialize()
        self.workerThread.start()

    def closeEvent(self, event):
        self.workerThread.quit()

    @QtC.Slot()
    def on_browsePushButton_pressed(self):
        sourceFile, _ = QtW.QFileDialog.getOpenFileName(self, "选择要进行转换的标注文件",
                                                        self.currentSourceFld.as_posix(), 'Annotations (*.json)')
        sourceFile = Path(sourceFile)
        if not sourceFile.is_file():
            status = QtW.QMessageBox.critical(self, '错误', '未选择文件', QtW.QMessageBox.Ok)
            if sourceFile.is_dir():
                self.currentSourceFld = sourceFile
            self.initialize()
            return None
        else:
            self.currentSourceFld = sourceFile.parent

        categories = self.worker.groundTruthConverter.annotationCompatibilityCheck(sourceFile)
        if not categories:
            self.initialize()
            return None

        self.sourceFile = sourceFile
        self.sourceFileLineEdit.setText(str(sourceFile))
        self.categoryLabel.setEnabled(True)
        self.categoryComboBox.setEnabled(True)
        self.convertOptionGroupBox.setEnabled(True)
        self.convertPushButton.setEnabled(True)
        for cat in categories:
            cat_icon = QtG.QPixmap(10, 10)
            cat_icon.fill(fillColor=QtG.QColor(*cat['color']))
            self.categoryComboBox.addItem(QtG.QIcon(cat_icon), cat['name'])

    @QtC.Slot()
    def on_convertPushButton_pressed(self):
        self.convertGroundTruthRequest.emit(
            self.sourceFile,
            self.categoryComboBox.currentText(),
            self.kernelShapeComboBox.currentText(),
            self.boundaryHalfWidthSpinBox.value(),
            self.boundarySmoothCoefDoubleSpinBox.value(),
            self.regionProbLowerBoundDoubleSpinBox.value(),
            [
                self.smoothBoundaryCheckBox.isChecked(),
                self.simpleBoundaryCheckBox.isChecked(),
                self.centralizeRegionCheckBox.isChecked(),
                self.simpleRegionCheckBox.isChecked()
            ]
        )
        self.centralWidget.setEnabled(False)