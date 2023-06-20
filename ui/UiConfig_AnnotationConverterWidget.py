from enum import IntEnum
import PySide2.QtCore as QtC, PySide2.QtWidgets as QtW, PySide2.QtGui as QtG
from ui.Ui_AnnotationConverterWidget import Ui_AnnotationConverterWidget


__all__ = ['BaseAnnotationConverterWidget']


class BaseAnnotationConverterWidget(Ui_AnnotationConverterWidget):
    class BasicMessageBoxType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    def adjustUi(self):
        self.buttons = [
            self.newPushButton,
            self.mergePushButton,
            self.overwritePushButton,
            self.convertFilePushButton,
        ]

        self.statusbar = QtW.QStatusBar(self)
        self.layout().addWidget(self.statusbar)
        self.layout().setStretch(0, 1)
        self.layout().setStretch(1, 0)
        self.progressBar = QtW.QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)

    def initialize(self):
        self._currentStatusBarPriority = 0
        self.progressBar.reset()
        self.targetFolderLineEdit.setText('')
        self.targetFileLineEdit.setText('')
        self.singleConvertTab.setEnabled(False)

        for btn in self.buttons:
            btn.setEnabled(False)

    @QtC.Slot(int)
    def onTabBarClicked(self, index):
        if index == 1 and not self.singleConvertTab.isEnabled():
            status = QtW.QMessageBox.critical(self, '错误', '需要先选择包含已有合法标注文件的目标文件夹, 才可使用单文件转换功能', QtW.QMessageBox.Ok)

    @QtC.Slot(str, int)
    def messageDispathcer(self, msg, msgtype):
        if msgtype == 1:
            self.sendTextToStatusBar.emit(msg, -1, 3)
        elif msgtype == 2 or msgtype == 3:
            self.sendToMessageBox.emit(msg, msgtype)

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
