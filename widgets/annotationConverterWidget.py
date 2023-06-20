from pathlib import Path
from enum import IntFlag
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG
from workers import IOWorker
from ui.UiConfig_AnnotationConverterWidget import BaseAnnotationConverterWidget


__all__ = ['AnnotationConverterWidget']


class AnnotationConverterWidget(BaseAnnotationConverterWidget, QtW.QWidget):
    sendTextToStatusBar = QtC.Signal(str, int, int)
    sendToMessageBox = QtC.Signal(str, int)
    repairAnnotationRequest = QtC.Signal(Path, IntFlag)
    convertAnnotationRequest = QtC.Signal(Path, int)
    convertSingleImageAnnotationRequest = QtC.Signal(list)

    def __init__(self, parent=None):
        super(AnnotationConverterWidget, self).__init__(parent)
        self.worker = IOWorker(self)
        self.workerThread = QtC.QThread()
        self.worker.moveToThread(self.workerThread)

        self.currentTargetFld = Path.home()

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
        self.tabWidget.tabBarClicked.connect(self.onTabBarClicked)

        self.repairAnnotationRequest.connect(self.worker.onRepairAnnotationRequestReceived)
        self.convertAnnotationRequest.connect(self.worker.onConvertAnnotationRequestReceived)
        self.convertSingleImageAnnotationRequest.connect(self.worker.onConvertSingleImageAnnotationRequestReceived)

        self.worker.workerMessage.connect(self.messageDispathcer)
        self.worker.workerException.connect(self.workerExceptionHandler)
        self.worker.sendToProgressBar.connect(self.progressBar.setValue)
        self.worker.sendToProgressBarRange.connect(self.progressBar.setRange)

        self.worker.annotationRepaired.connect(self.onAnnotationRepaired)
        self.worker.convertFinished.connect(self.tabWidget.setEnabled)

    def initialize(self):
        super(AnnotationConverterWidget, self).initialize()
        self.targetFld = None
        self.imagePaths = []

    def showEvent(self, event):
        self.initialize()
        self.workerThread.start()

    def closeEvent(self, event):
        self.workerThread.quit()

    @QtC.Slot()
    def on_browseFolderPushButton_pressed(self):
        targetFld = QtW.QFileDialog.getExistingDirectory(self, "选择目标文件夹", self.currentTargetFld.as_posix(),
                                                         QtW.QFileDialog.ShowDirsOnly)
        targetFld = Path(targetFld)
        if not targetFld.exists():
            status = QtW.QMessageBox.critical(self, '错误', '未选择正确的目标文件夹', QtW.QMessageBox.Ok)
            self.initialize()
            return None

        _emptyFld, _compatibleFld = self.worker.annotationConverter.folderCompatibilityCheck(targetFld)
        if _emptyFld:
            status = QtW.QMessageBox.critical(
                self, '错误', '目标文件夹不包含可转换的原始图像/边界数据', QtW.QMessageBox.Ok)
            self.initialize()
            return None
        if not _compatibleFld:
            status = QtW.QMessageBox.warning(
                self, '警告', '目标文件夹包含不匹配的原始图像/边界数据，建议清理该文件夹或选择其他文件夹，是否继续？',
                QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
            if status == QtW.QMessageBox.StandardButton.Cancel:
                self.initialize()
                return None

        convertFlag = self.worker.annotationConverter.annotationCompatibilityCheck(targetFld, 'Slag')
        self.repairAnnotationRequest.emit(targetFld, convertFlag)

    @QtC.Slot(Path, IntFlag)
    def onAnnotationRepaired(self, targetFld, convertFlag):
        self.targetFolderLineEdit.setText(str(targetFld))
        self.targetFld = targetFld
        self.currentTargetFld = self.targetFld.parent
        self.imagePaths = []
        self.newPushButton.setEnabled(self.worker.annotationConverter.ConvertModeFlag.New in convertFlag)
        self.mergePushButton.setEnabled(self.worker.annotationConverter.ConvertModeFlag.Merge in convertFlag)
        self.overwritePushButton.setEnabled(self.worker.annotationConverter.ConvertModeFlag.Overwrite in convertFlag)
        self.singleConvertTab.setEnabled(self.worker.annotationConverter.ConvertModeFlag.Merge in convertFlag)

    @QtC.Slot()
    def on_browseFilePushButton_pressed(self):
        images, _ = QtW.QFileDialog.getOpenFileNames(self, '选择要进行转换的文件', self.targetFld.as_posix(), 'Images (*.jpg)')
        imagePaths = []
        for img in images:
            imgPath = Path(img)
            if imgPath.parent != self.targetFld:
                status = QtW.QMessageBox.critical(
                    self, '错误', '{选择的文件不在当前目标文件夹内', QtW.QMessageBox.Ok)
                break
            if not ((imgPath.parent / 'result') / (imgPath.stem + '.border.tif')).exists():
                status = QtW.QMessageBox.critical(
                    self, '错误', '{fname}缺失对应的边界数据, 已从选择集中排除'.format(fname=imgPath.name), QtW.QMessageBox.Ok)
                continue
            imagePaths.append(imgPath)
        totalImageCount = len(imagePaths)
        if totalImageCount > 0:
            self.imagePaths = imagePaths
            self.targetFileLineEdit.setText('{file1}{file2}{file3}{other}'.format(
                file1=self.imagePaths[0].name,
                file2=(', ' + self.imagePaths[1].name) if totalImageCount >= 2 else '',
                file3=(', ' + self.imagePaths[2].name) if totalImageCount >= 3 else '',
                other=', 等多个文件...' if totalImageCount > 3 else '',
            ))
            self.convertFilePushButton.setEnabled(True)

    @QtC.Slot()
    def on_newPushButton_pressed(self):
        self.convertAnnotationRequest.emit(self.targetFld, self.worker.annotationConverter.ConvertModeFlag.New)
        self.tabWidget.setEnabled(False)

    @QtC.Slot()
    def on_mergePushButton_pressed(self):
        self.convertAnnotationRequest.emit(self.targetFld, self.worker.annotationConverter.ConvertModeFlag.Merge)
        self.tabWidget.setEnabled(False)

    @QtC.Slot()
    def on_overwritePushButton_pressed(self):
        self.convertAnnotationRequest.emit(self.targetFld, self.worker.annotationConverter.ConvertModeFlag.Overwrite)
        self.tabWidget.setEnabled(False)

    @QtC.Slot()
    def on_convertFilePushButton_pressed(self):
        status = QtW.QMessageBox.warning(
            self, '警告',
            '单文件转换将在已有标注上添加新的标注, 可能产生多个重合的标注, 建议用于新图像的标注添加或恢复意外丢失的标注, 请谨慎选择要转换的文件\n是否继续？',
            QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
        if status == QtW.QMessageBox.StandardButton.Ok:
            self.convertSingleImageAnnotationRequest.emit(self.imagePaths)
            self.tabWidget.setEnabled(False)