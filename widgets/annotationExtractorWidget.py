from pathlib import Path
from enum import IntFlag
import PySide2.QtCore as QtC, PySide2.QtWidgets as QtW, PySide2.QtGui as QtG
from workers import IOWorker
from lib.customWidgets import QCustomMessageBox
from ui.UiConfig_AnnotationExtractorWidget import BaseAnnotationExtractorWidget


__all__ = ['AnnotationExtractorWidget']


class AnnotationExtractorWidget(BaseAnnotationExtractorWidget, QtW.QWidget):
    sendTextToStatusBar = QtC.Signal(str, int, int)
    sendToMessageBox = QtC.Signal(str, int)
    repairAnnotationRequest = QtC.Signal(Path, IntFlag)
    openAnnotationRequest = QtC.Signal(Path)
    extractAnnotationRequest = QtC.Signal(dict, Path, set)

    rotateMatrix = QtG.QMatrix().rotate(-90)

    def __init__(self, parent=None):
        super(AnnotationExtractorWidget, self).__init__(parent)
        self.mutex = QtC.QMutex()
        self.waitConditions = {'AskForOverwrite': QtC.QWaitCondition()}

        self.worker = IOWorker(self, mutex=self.mutex, waitConditions=self.waitConditions)
        self.workerThread = QtC.QThread()
        self.worker.moveToThread(self.workerThread)

        self.currentSourceFld = Path.home()
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

        self.repairAnnotationRequest.connect(self.worker.onRepairAnnotationRequestReceived)
        self.openAnnotationRequest.connect(self.worker.onOpenAnnotationRequestReceived)
        self.extractAnnotationRequest.connect(self.worker.onExtractAnnotationRequestReceived)

        self.worker.workerMessage.connect(self.messageDispathcer)
        self.worker.workerException.connect(self.workerExceptionHandler)
        self.worker.sendToProgressBar.connect(self.progressBar.setValue)
        self.worker.sendToProgressBarRange.connect(self.progressBar.setRange)

        self.worker.annotationRepaired.connect(self.onAnnotationRepaired)
        self.worker.annotationOpened.connect(self.onAnnotationOpened)
        self.worker.annotationExtracted.connect(self.tableWidget.setEnabled)
        self.worker.annotationExtracted.connect(self.openPushButton.setEnabled)
        self.worker.annotationExtracted.connect(self.extractPushButton.setEnabled)
        self.worker.askForOverwrite.connect(self.onAskedForOverwrite)

    def initialize(self):
        super(AnnotationExtractorWidget, self).initialize()
        self.sourceFile = None
        self.targetFld = None
        self.annoDataDict = {}
        self.checkBoxes = []
        self.selection = set()
        self._overwriteFlag = False
        self._applyForAllFlag = False

    def showEvent(self, event):
        self.initialize()
        self.workerThread.start()

    def closeEvent(self, event):
        self.workerThread.quit()

    @QtC.Slot()
    def on_openPushButton_pressed(self):
        sourceFile, _ = QtW.QFileDialog.getOpenFileName(self, "选择要进行提取的标注文件", self.currentSourceFld.as_posix(), 'Annotations (*.json)')
        sourceFile = Path(sourceFile)
        if not sourceFile.is_file():
            status = QtW.QMessageBox.critical(self, '错误', '未选择文件', QtW.QMessageBox.Ok)
            if sourceFile.is_dir():
                self.currentSourceFld = sourceFile
            return None
        else:
            self.currentSourceFld = sourceFile.parent

        convertFlag = self.worker.annotationConverter.annotationCompatibilityCheck(sourceFile, 'Slag', send_message=False)
        self.repairAnnotationRequest.emit(sourceFile, convertFlag)

    @QtC.Slot(Path, IntFlag)
    def onAnnotationRepaired(self, sourceFile, convertFlag):
        if self.worker.annotationConverter.ConvertModeFlag.Extractable not in convertFlag:
            status = QtW.QMessageBox.critical(self, '错误', '非法标注文件, 无法进行提取', QtW.QMessageBox.Ok)
            return None

        self.initialize()
        self.sourceFile = sourceFile
        self.openAnnotationRequest.emit(self.sourceFile)

    @QtC.Slot(dict)
    def onAnnotationOpened(self, annoDataDict):
        self.annoDataDict = annoDataDict
        numRows = len(self.annoDataDict['images'])
        self.tableWidget.setRowCount(numRows)
        rowCount = 0
        invalid = 0
        for i in range(numRows):
            imgInfo = self.annoDataDict['images'].iloc[i]
            origImgExist = imgInfo['Path'].exists()
            boundaryExist = imgInfo['BoundaryPath'].exists()
            if imgInfo['ThumbnailPath']:
                thumbExist = imgInfo['ThumbnailPath'].exists()
            else:
                thumbExist = False

            self.setTableWidgetItem(rowCount, 0, int(imgInfo['id']))
            self.setTableWidgetItem(rowCount, 1, imgInfo['file_name'])
            if origImgExist:
                if thumbExist:
                    thumbnail = QtG.QPixmap(str(imgInfo['ThumbnailPath'])).transformed(self.rotateMatrix)
                else:
                    thumbnail = '未能生成缩略图'
            else:
                thumbnail = '缺失'
            self.setTableWidgetItem(rowCount, 2, thumbnail)
            self.setTableWidgetItem(
                rowCount, 3,
                int(imgInfo['NumSlagInOrigBoundary']) if boundaryExist else '缺失'
            )
            if len(imgInfo['AnnotationMap']) > imgInfo['NumSlagInOrigBoundary']:
                foregroundColor = QtG.QColor('red')
            elif len(imgInfo['AnnotationMap']) < imgInfo['NumSlagInOrigBoundary']:
                foregroundColor = QtG.QColor('blue')
            else:
                foregroundColor = QtG.QColor('black')
            self.setTableWidgetItem(rowCount, 4, len(imgInfo['AnnotationMap']),
                                    foreground=foregroundColor)

            checkboxWidget = QtW.QWidget()
            checkboxLayout = QtW.QHBoxLayout()
            checkboxItem = QtW.QCheckBox()
            if not origImgExist or not boundaryExist:
                checkboxItem.setEnabled(False)
                invalid += 1
            checkboxItem.setStyleSheet('QCheckBox::indicator {width: 24; height:24;}')
            checkboxLayout.addWidget(checkboxItem, 0, QtC.Qt.AlignCenter)
            checkboxLayout.setMargin(0)
            checkboxWidget.setLayout(checkboxLayout)
            self.tableWidget.setCellWidget(rowCount, 5, checkboxWidget)
            self.checkBoxes.append(checkboxItem)
            checkboxItem.stateChanged.connect(self.onImageSelected)

            self.tableWidget.setRowHeight(rowCount, 100)
            rowCount += 1
        self.totalImageLabel.setText('/ {avail} (共{total})'.format(avail=rowCount - invalid, total=rowCount))
        self.tableWidget.update()

    @QtC.Slot()
    def on_extractPushButton_pressed(self):
        targetFld = QtW.QFileDialog.getExistingDirectory(self, "选择转存提取标注信息的文件夹",
                                                             self.currentTargetFld.as_posix(), QtW.QFileDialog.ShowDirsOnly)
        targetFld = Path(targetFld)
        if not targetFld.exists():
            status = QtW.QMessageBox.critical(self, '错误', '未选择正确的转存文件夹', QtW.QMessageBox.Ok)
            return None

        # _emptyFld, _compatibleFld = self.worker.annotationConverter.folderCompatibilityCheck(targetFld)
        # if not (_emptyFld or _compatibleFld):
        #     status = QtW.QMessageBox.warning(
        #         self, '警告', '目标文件夹包含不匹配的原始图像/边界数据，建议清理该文件夹或选择其他文件夹，是否继续？',
        #         QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
        #     if status == QtW.QMessageBox.StandardButton.Cancel:
        #         return None

        convertFlag = self.worker.annotationConverter.annotationCompatibilityCheck(targetFld, 'Slag')
        self.worker.annotationRepaired.disconnect(self.onAnnotationRepaired)
        self.worker.annotationRepaired.connect(self.onAnnotationRepaired_Target)
        self.repairAnnotationRequest.emit(targetFld, convertFlag)

    @QtC.Slot(Path, IntFlag)
    def onAnnotationRepaired_Target(self, targetFld, convertFlag):
        self.worker.annotationRepaired.disconnect(self.onAnnotationRepaired_Target)
        self.worker.annotationRepaired.connect(self.onAnnotationRepaired)
        if self.worker.annotationConverter.ConvertModeFlag.Overwrite in convertFlag:
            if self.worker.annotationConverter.ConvertModeFlag.Merge not in convertFlag:
                status = QtW.QMessageBox.critical(self, '错误', '发现现有标注文件，但文件存在错误, 无法进行合并，建议清理目标文件夹', QtW.QMessageBox.Ok)
                return None
        if self.worker.annotationConverter.ConvertModeFlag.Merge in convertFlag:
            status = QtW.QMessageBox.information(self, '提示', '发现现有标注文件，是否进行合并？', QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
            if status == QtW.QMessageBox.Cancel:
                return None

        self.targetFld = targetFld
        self.extractAnnotationRequest.emit(self.annoDataDict, self.targetFld, self.selection)
        self.tableWidget.setEnabled(False)
        self.openPushButton.setEnabled(False)
        self.extractPushButton.setEnabled(False)

    @QtC.Slot(str)
    def onAskedForOverwrite(self, imgName):
        self.mutex.lock()
        messageBox = QCustomMessageBox.flexible(
            QtW.QMessageBox.Question,
            '选择标注写入模式',
            '{imgName}提取的的标注信息与目标文件夹内的已有标注不一致，请选择标注信息写入模式'.format(
                imgName=imgName
            ),
            ['覆写', '全部覆写', '跳过', '全部跳过'],
            roles=[
                QtW.QMessageBox.YesRole,
                QtW.QMessageBox.YesRole,
                QtW.QMessageBox.NoRole,
                QtW.QMessageBox.DestructiveRole,
            ],
        )
        if messageBox.clickedButton().text() == '覆写':
            self._overwriteFlag = True
        elif messageBox.clickedButton().text() == '全部覆写':
            self._overwriteFlag = True
            self._applyForAllFlag = True
        elif messageBox.clickedButton().text() == '跳过':
            self._overwriteFlag = False
        elif messageBox.clickedButton().text() == '全部跳过':
            self._overwriteFlag = False
            self._applyForAllFlag = True
        else:
            raise NotImplementedError
        self.waitConditions['AskForOverwrite'].wakeAll()
        self.mutex.unlock()

    @QtC.Slot(int)
    def onImageSelected(self, state):
        if state == QtC.Qt.Checked:
            self.selection.add(self.checkBoxes.index(self.sender()))
        elif state == QtC.Qt.Unchecked:
            self.selection.discard(self.checkBoxes.index(self.sender()))
        else:
            raise NotImplementedError
        self.numSelectedSpinBox.setValue(len(self.selection))
        self.extractPushButton.setEnabled(len(self.selection) > 0)