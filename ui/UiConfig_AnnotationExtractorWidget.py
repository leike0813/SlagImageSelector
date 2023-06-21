from enum import IntEnum
import PySide2.QtCore as QtC, PySide2.QtWidgets as QtW, PySide2.QtGui as QtG
from lib.customDelegates import QPixmapItemDelegate
from ui.Ui_AnnotationExtractorWidget import Ui_AnnotationExtractorWidget
import qtawesome as qta


__all__ = ['BaseAnnotationExtractorWidget']


class BaseAnnotationExtractorWidget(Ui_AnnotationExtractorWidget):
    class BasicMessageBoxType(IntEnum):
        Information = 1
        Warning = 2
        Critical = 3

    def adjustUi(self):
        iconSize = QtC.QSize(32, 32)
        iconScale = 1.0

        font = QtG.QFont()
        font.setFamily(u"\u5e7c\u5706")
        font.setPointSize(12)
        font.setWeight(75)

        self.buttons = [
            self.extractPushButton,
        ]

        self.statusbar = QtW.QStatusBar(self)
        self.layout().addWidget(self.statusbar)
        self.layout().setStretch(2, 0)
        self.progressBar = QtW.QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)

        self.openPushButton.setIcon(
            qta.icon('mdi6.file-search', color='deepskyblue', scale_factor=iconScale))
        self.openPushButton.setFont(font)
        self.openPushButton.setIconSize(iconSize)
        self.openPushButton.setMinimumHeight(iconSize.height())

        self.extractPushButton.setIcon(
            qta.icon('mdi6.file-move', color='deepskyblue', scale_factor=iconScale))
        self.extractPushButton.setFont(font)
        self.extractPushButton.setIconSize(iconSize)
        self.extractPushButton.setMinimumHeight(iconSize.height())

        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(1)

        imgIDItem = QtW.QTableWidgetItem()
        imgIDItem.setData(QtC.Qt.DisplayRole, 'ID')
        imgIDItem.setData(QtC.Qt.TextAlignmentRole, QtC.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(0, imgIDItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QtW.QHeaderView.ResizeToContents)

        imgNameItem = QtW.QTableWidgetItem()
        imgNameItem.setData(QtC.Qt.DisplayRole, '文件名')
        imgNameItem.setData(QtC.Qt.TextAlignmentRole, QtC.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(1, imgNameItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtW.QHeaderView.ResizeToContents)

        thumbItem = QtW.QTableWidgetItem()
        thumbItem.setData(QtC.Qt.DisplayRole, '原始图像')
        thumbItem.setData(QtC.Qt.TextAlignmentRole, QtC.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(2, thumbItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(2, QtW.QHeaderView.Fixed)
        self.tableWidget.horizontalHeader().resizeSection(2, 200)

        numSlagOrigItem = QtW.QTableWidgetItem()
        numSlagOrigItem.setData(QtC.Qt.DisplayRole, '原始标注数量')
        numSlagOrigItem.setData(QtC.Qt.TextAlignmentRole, QtC.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(3, numSlagOrigItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QtW.QHeaderView.Stretch)

        numSlagAnnoItem = QtW.QTableWidgetItem()
        numSlagAnnoItem.setData(QtC.Qt.DisplayRole, '发现标注数量')
        numSlagAnnoItem.setData(QtC.Qt.TextAlignmentRole, QtC.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(4, numSlagAnnoItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(4, QtW.QHeaderView.Stretch)

        checkboxItem = QtW.QTableWidgetItem()
        checkboxItem.setData(QtC.Qt.DisplayRole, '选择')
        checkboxItem.setData(QtC.Qt.TextAlignmentRole, QtC.Qt.AlignCenter)
        self.tableWidget.setHorizontalHeaderItem(5, checkboxItem)
        self.tableWidget.horizontalHeader().setSectionResizeMode(5, QtW.QHeaderView.Fixed)
        self.tableWidget.horizontalHeader().resizeSection(5, 10)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setItemDelegateForColumn(2, QPixmapItemDelegate())

    def initialize(self):
        self._currentStatusBarPriority = 0
        self.progressBar.reset()
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        self.numSelectedSpinBox.setValue(0)
        self.totalImageLabel.setText('/ {avail} (共{total})'.format(avail=0, total=0))
        self.extractPushButton.setEnabled(False)

        for btn in self.buttons:
            btn.setEnabled(False)

    def setTableWidgetItem(self, row, column, data, role=QtC.Qt.DisplayRole,
                           flags=QtC.Qt.ItemIsEnabled,
                           foreground=QtG.QColor('black'),
                           textAliengment=QtC.Qt.AlignCenter):
        item = QtW.QTableWidgetItem()
        item.setData(role, data)
        item.setFlags(flags)
        if role != QtC.Qt.ForegroundRole:
            item.setData(QtC.Qt.ForegroundRole, foreground)
        if role != QtC.Qt.TextAlignmentRole:
            item.setData(QtC.Qt.TextAlignmentRole, textAliengment)
        self.tableWidget.setItem(row, column, item)

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