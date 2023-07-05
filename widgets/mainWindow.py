import sys, os
from pathlib import Path
from copy import copy
from enum import IntFlag
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG
import pandas as pd
from lib.customWidgets.customMessageBox import QCustomMessageBox
from workers import IOWorker
from widgets.selectionViewWidget import SelectionViewWidget
from widgets.annotationConverterWidget import AnnotationConverterWidget
from widgets.annotationExtractorWidget import AnnotationExtractorWidget
from widgets.groundTruthConverterWidget import GroundTruthConverterWidget
from ui.UiConfig_MainWindow import BaseMainWindow

from PySide2.QtCore import QLibraryInfo
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)


__all__ = ['MainWindow']


class MainWindow(BaseMainWindow, QtW.QMainWindow):
    sendTextToStatusBar = QtC.Signal(str, int, int)
    sendToMessageBox = QtC.Signal(str, int)
    selectionChanged = QtC.Signal(int)
    dataFolderOpened = QtC.Signal(Path)
    repairAnnotationRequest = QtC.Signal(Path, IntFlag)
    exportFolderOpened = QtC.Signal(Path, Path, list, pd.DataFrame, int)
    convertAnnotationRequest = QtC.Signal(Path, int)
    saveRequest = QtC.Signal(Path, list, pd.DataFrame, int, bool)
    selectionViewRequest = QtC.Signal(Path, list, pd.DataFrame)

    def __init__(self, disableConsole = True):
        super(MainWindow, self).__init__()
        self.selectionViewWidget = SelectionViewWidget(self)
        self.annotationConverterWidget = AnnotationConverterWidget()
        self.annotationExtractorWidget = AnnotationExtractorWidget()
        self.groundTruthConverterWidget = GroundTruthConverterWidget()

        self.worker = IOWorker(self)
        self.workerThread = QtC.QThread()
        self.worker.moveToThread(self.workerThread)

        self.currentHomeFld = Path.home()
        self.currentExportFld = Path.home()
        self._disableConsole = disableConsole

        # --------------init procedure boilerplate---------------
        self.setupUi(self)
        self.adjustUi()
        self.connectSignalToSlot()
        self.initialize()
        # ------------------------------------------------------

        self.installEventFilter(self)
        self.workerThread.start()

        if not self._disableConsole:
            self.initConsole()

    def connectSignalToSlot(self):
        self.sendTextToStatusBar.connect(self.statusBarShowMessage)
        self.sendToMessageBox.connect(self.openBasicMessageBox)
        self.statusBar().messageChanged.connect(self.onStatusBarMessageChanged)
        self.selectionChanged.connect(self.onSelectionChanged)
        self.listWidget.currentRowChanged.connect(self.showImage)

        self.selectionViewWidget.sendAbandoned.connect(self.onImageAbandoned)

        self.dataFolderOpened.connect(self.worker.onDataFolderOpened)
        self.repairAnnotationRequest.connect(self.worker.onRepairAnnotationRequestReceived)
        self.exportFolderOpened.connect(self.worker.onExportFolderOpened)
        self.convertAnnotationRequest.connect(self.worker.onConvertAnnotationRequestReceived)
        self.saveRequest.connect(self.worker.onSaveRequestReceived)
        self.selectionViewRequest.connect(self.worker.onSelectionViewRequestReceived)

        self.worker.workerMessage.connect(self.messageDispathcer)
        self.worker.workerException.connect(self.workerExceptionHandler)
        self.worker.sendToListWidget.connect(self.listWidget.addItem)
        self.worker.sendSelected.connect(self.onImageAdopted)
        self.worker.sendToProgressBar.connect(self.progressBar.setValue)
        self.worker.sendToProgressBarRange.connect(self.progressBar.setRange)

        self.worker.imageLibLoaded.connect(self.onImageLibLoaded)
        self.worker.dataLoaded.connect(self.onDataLoaded)
        self.worker.annotationRepaired.connect(self.onAnnotationRepaired)
        self.worker.exportFinished.connect(self.onExportFinished)
        self.worker.convertFinished.connect(self.centralWidget().setEnabled)
        self.worker.convertFinished.connect(self.menuBar().setEnabled)
        self.worker.selectionSaved.connect(self.onSelectionSaved)
        self.worker.thumbnailCached.connect(self.selectionViewWidget.setSelection)

    def initialize(self):
        super(MainWindow, self).initialize()
        self.workFld = None
        self.resultFld = None
        self.origImagePaths = None
        self.imageLib = None
        self.totalImageCount = 0
        self.outputList = []
        self.outputList_Archive = []
        self.totalImagesLabel.setText('/ {imgcnt}'.format(imgcnt=self.totalImageCount))
        self.currentImageSpinBox.setMaximum(self.totalImageCount)

    def eventFilter(self, watched, event):
        if watched == self and event.type() == QtC.QEvent.Close:
            status = self.checkOutputList()
            if status == 1:
                self.on_action_Save_triggered(True, True)
                event.ignore()
            elif status == -1:
                self.annotationConverterWidget.close()
                self.annotationExtractorWidget.close()
                self.workerThread.quit()
                if not self._disableConsole:
                    self.console.close()
                event.accept()
            else:
                event.ignore()
        return super(MainWindow, self).eventFilter(watched, event)

    @property
    def numSelectedImages(self):
        return len(self.outputList)

    @QtC.Slot(bool)
    def on_action_OpenFolder_triggered(self, triggered):
        status = self.checkOutputList()
        if status == 1:
            self.on_action_Save_triggered(True)
        if status == 0:
            return None
        workFld = QtW.QFileDialog.getExistingDirectory(self, "选择数据文件夹", self.currentHomeFld.as_posix(), QtW.QFileDialog.ShowDirsOnly)
        workFld = Path(workFld)
        if not workFld.exists():
            status = QtW.QMessageBox.critical(self, '错误', '未选择正确的数据文件夹', QtW.QMessageBox.Ok)
            return None
        if not (workFld / 'result').exists():
            status = QtW.QMessageBox.critical(self, '错误', '文件夹结构错误，子文件夹"result"不存在', QtW.QMessageBox.Ok)
            return None

        self.initialize()
        self.workFld = workFld
        self.currentHomeFld = self.workFld.parent
        self.workFldLabel.setText("当前工作文件夹：{workfld}".format(workfld=workFld))
        self.resultFld = self.workFld / 'result'
        self.sendTextToStatusBar.emit('正在读取原始数据', -1, 3)
        self.centralWidget().setEnabled(False)
        self.menuBar().setEnabled(False)
        self.dataFolderOpened.emit(self.workFld)

    @QtC.Slot(int, pd.DataFrame)
    def onImageLibLoaded(self, imgCount, imageLib):
        self.totalImageCount = imgCount
        self.imageLib = imageLib
        self.totalImagesLabel.setText('/ {imgcnt}'.format(imgcnt=self.totalImageCount))
        self.currentImageSpinBox.setMaximum(self.totalImageCount)

    @QtC.Slot(int)
    def onDataLoaded(self, cur_idx):
        self.centralWidget().setEnabled(True)
        self.menuBar().setEnabled(True)
        self.listWidget.setCurrentRow(cur_idx if cur_idx < self.totalImageCount else 0)
        self.selectionChanged.emit(self.numSelectedImages)
        self.sendTextToStatusBar.emit('', 1, 3)
        self.outputList_Archive = copy(self.outputList)
        self.action_Save.setEnabled(True)
        self.action_Export.setEnabled(True)

    @QtC.Slot(bool)
    def on_action_Export_triggered(self, triggered):
        if len(self.outputList) == 0:
            status = QtW.QMessageBox.critical(self, '错误', '导出列表为空', QtW.QMessageBox.Ok)
            return None

        exportFld = QtW.QFileDialog.getExistingDirectory(self, "选择导出文件夹",
                                                         self.currentExportFld.as_posix(), QtW.QFileDialog.ShowDirsOnly)
        exportFld = Path(exportFld)
        if not exportFld.exists():
            status = QtW.QMessageBox.critical(self, '错误', '未选择正确的导出文件夹', QtW.QMessageBox.Ok)
            return None

        _emptyFld, _compatibleFld = self.worker.annotationConverter.folderCompatibilityCheck(exportFld)
        if not (_emptyFld or _compatibleFld):
            status = QtW.QMessageBox.warning(
                self, '警告', '目标文件夹包含不匹配的原始图像/边界数据，建议清理该文件夹或选择其他文件夹，是否继续？',
                QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
            if status == QtW.QMessageBox.StandardButton.Cancel:
                return None

        convertFlag = self.worker.annotationConverter.annotationCompatibilityCheck(exportFld, 'Slag')
        self.repairAnnotationRequest.emit(exportFld, convertFlag)

    @QtC.Slot(Path, IntFlag)
    def onAnnotationRepaired(self, exportFld, convertFlag):
        if convertFlag not in self.worker.annotationConverter.ConvertModeFlag:
            messageBox = QCustomMessageBox.flexible(
                QtW.QMessageBox.Question,
                '选择标注信息导出模式',
                '发现已有标注文件，请选择标注信息导出模式',
                ['新建', '合并', '覆写', '取消'],
                execute=False
            )
            messageBox.buttonTexts()['新建'].setEnabled(self.worker.annotationConverter.ConvertModeFlag.New in convertFlag)
            messageBox.buttonTexts()['合并'].setEnabled(self.worker.annotationConverter.ConvertModeFlag.Merge in convertFlag)
            messageBox.buttonTexts()['覆写'].setEnabled(self.worker.annotationConverter.ConvertModeFlag.Overwrite in convertFlag)
            messageBox.exec()
            if messageBox.clickedButton().text() == '取消':
                return None
            convertMode = [
                self.worker.annotationConverter.ConvertModeFlag.New,
                self.worker.annotationConverter.ConvertModeFlag.Merge,
                self.worker.annotationConverter.ConvertModeFlag.Overwrite,
            ][['新建', '合并', '覆写'].index(messageBox.clickedButton().text())]
        else:
            convertMode = convertFlag

        self.exportFld = Path(exportFld)
        self.currentExportFld = self.exportFld.parent
        self.centralWidget().setEnabled(False)
        self.menuBar().setEnabled(False)
        self.exportFolderOpened.emit(self.exportFld, self.workFld, self.outputList, self.imageLib, convertMode)

    @QtC.Slot(Path, int)
    def onExportFinished(self, exportFld, convertMode):
        status = QtW.QMessageBox.question(
            self, '提示', '选择集已导出，是否立即转换标注文件？',
            QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
        if status == QtW.QMessageBox.StandardButton.Ok:
            self.convertAnnotationRequest.emit(exportFld, convertMode)
        else:
            self.centralWidget().setEnabled(True)
            self.menuBar().setEnabled(True)

    @QtC.Slot(bool)
    def on_action_Save_triggered(self, triggered, exitAfterSaved=False):
        self.saveRequest.emit(self.workFld, self.outputList, self.imageLib, self.listWidget.currentRow(), exitAfterSaved)

    @QtC.Slot(bool)
    def onSelectionSaved(self, exitAfterSaved):
        self.sendTextToStatusBar.emit('选择集已保存', 2000, 2)
        self.outputList_Archive = copy(self.outputList)
        if exitAfterSaved:
            self.close()

    @QtC.Slot()
    def on_selectionViewPushButton_pressed(self):
        self.selectionViewRequest.emit(self.workFld, self.outputList, self.imageLib)
        # TODO:

    @QtC.Slot(int)
    def showImage(self, imgIdx):
        if imgIdx != -1:
            imgInfo = self.imageLib.loc[imgIdx]
            self.imageWidget.origImageBox.setImage((self.workFld / imgInfo['Orig_Image']).as_posix())
            self.imageWidget.resultImageBox.setImage((self.resultFld / imgInfo['Orig_Image']).as_posix())
            for btn in self.buttons:
                btn.setEnabled(True)
            self.currentImageSpinBox.setValue(imgIdx + 1)
        else:
            for btn in self.buttons:
                btn.setEnabled(False)

    @QtC.Slot(int)
    def onImageAdopted(self, imgIdx):
        self.outputList.append(imgIdx)
        self.listWidget.item(imgIdx).setForeground(QtG.QBrush(QtC.Qt.red))
        self.selectionChanged.emit(self.numSelectedImages)

    @QtC.Slot(int)
    def onImageAbandoned(self, imgIdx):
        if imgIdx in self.outputList:
            self.outputList.pop(self.outputList.index(imgIdx))
            self.listWidget.item(imgIdx).setForeground(QtG.QBrush(QtC.Qt.black))
            self.selectionChanged.emit(self.numSelectedImages)

    def checkOutputList(self):
        if set(self.outputList) != set(self.outputList_Archive):
            status = QtW.QMessageBox.question(
                self, '提示', '选择集已发生改变，是否保存？',
                QtW.QMessageBox.Save | QtW.QMessageBox.Discard | QtW.QMessageBox.Cancel)
            if status == QtW.QMessageBox.StandardButton.Save:
                # self.on_action_Save_triggered(True)
                return 1
            elif status == QtW.QMessageBox.StandardButton.Discard:
                return -1
            else:
                return 0
        return -1


if __name__ == '__main__':
    app = QtW.QApplication(sys.argv)
    win = MainWindow(disableConsole=False)
    win.show()
    sys.exit(app.exec_())