import os
import sys
from enum import IntEnum
from copy import copy
import numpy as np
import pandas as pd
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG
import qtawesome as qta
from ui.Ui_MainWindow import Ui_MainWindow
from lib.customWidgets import QIPythonConsoleWidget



__all__ = ['BaseMainWindow']


class BaseMainWindow(Ui_MainWindow):
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
            self.nextPushButton,
            self.previousPushButton,
            self.adoptPushButton,
            self.abandonPushButton,
            self.skipPushButton
        ]

        self.nextPushButton.setIcon(
            qta.icon('mdi6.arrow-right-circle', color='deepskyblue', scale_factor=iconScale))
        self.nextPushButton.setIconSize(iconSize)
        self.nextPushButton.setMinimumSize(iconSize)

        self.previousPushButton.setIcon(
            qta.icon('mdi6.arrow-left-circle', color='deepskyblue', scale_factor=iconScale))
        self.previousPushButton.setIconSize(iconSize)
        self.previousPushButton.setMinimumSize(iconSize)

        self.adoptPushButton.setIcon(
            qta.icon('mdi6.check-circle', color='green', scale_factor=iconScale))
        self.adoptPushButton.setFont(font)
        self.adoptPushButton.setIconSize(iconSize)
        self.adoptPushButton.setMinimumHeight(iconSize.height())

        self.abandonPushButton.setIcon(
            qta.icon('mdi6.close-circle', color='red', scale_factor=iconScale))
        self.abandonPushButton.setFont(font)
        self.abandonPushButton.setIconSize(iconSize)
        self.abandonPushButton.setMinimumHeight(iconSize.height())

        self.skipPushButton.setIcon(
            qta.icon('mdi6.skip-next-circle', color='blue', scale_factor=iconScale))
        self.skipPushButton.setFont(font)
        self.skipPushButton.setIconSize(iconSize)
        self.skipPushButton.setMinimumHeight(iconSize.height())

        self.clearPushButton.setIcon(
            qta.icon('mdi6.layers-off', color='deepskyblue', scale_factor=iconScale)
        )
        self.clearPushButton.setFont(font)
        self.clearPushButton.setIconSize(iconSize)
        self.clearPushButton.setMinimumHeight(iconSize.height())

        self.selectionViewPushButton.setIcon(
            qta.icon('mdi6.view-gallery', color='deepskyblue', scale_factor=iconScale)
        )
        self.selectionViewPushButton.setFont(font)
        self.selectionViewPushButton.setIconSize(iconSize)
        self.selectionViewPushButton.setMinimumHeight(iconSize.height())

        self.additiveModeCheckBox.setFont(font)

        self.workFldLabel = QtW.QLabel(self)
        self.statusBar().addPermanentWidget(self.workFldLabel)
        self.progressBar = QtW.QProgressBar()
        self.statusBar().addPermanentWidget(self.progressBar)

        self.action_OpenFolder.setIcon(
            qta.icon('mdi6.folder-open', color='deepskyblue')
        )
        self.action_Save.setIcon(
            qta.icon('mdi6.content-save', color='deepskyblue')
        )
        self.action_Export.setIcon(
            qta.icon('mdi6.file-export', color='deepskyblue')
        )
        self.action_AnnotationConverter.setIcon(
            qta.icon('mdi6.file-marker', color='deepskyblue')
        )
        self.action_AnnotationExtractor.setIcon(
            qta.icon('mdi6.file-move', color='deepskyblue')
        )
        self.action_GroundTruthConverter.setIcon(
            qta.icon('mdi6.file-image', color='deepskyblue')
        )
        self.action_Console.setIcon(
            qta.icon('mdi6.console', color='deepskyblue')
        )
        self.action_Exit.setIcon(
            qta.icon('mdi6.exit-run', color='red')
        )

    def initialize(self):
        self._currentStatusBarPriority = 0
        self.listWidget.clear()
        self.numSelectedSpinBox.setValue(0)
        self.progressBar.reset()
        self.action_Save.setEnabled(False)
        self.action_Export.setEnabled(False)

    @QtC.Slot(str, int)
    def messageDispathcer(self, msg, msgtype):
        if msgtype == 1:
            self.sendTextToStatusBar.emit(msg, -1, 3)
        elif msgtype == 2 or msgtype == 3:
            self.sendToMessageBox.emit(msg, msgtype)

    @QtC.Slot(int)
    def on_currentImageSpinBox_valueChanged(self, value):
        self.listWidget.setCurrentRow(value - 1)
        if value == 1:
            self.previousPushButton.setEnabled(False)
            self.nextPushButton.setEnabled(self.totalImageCount > 1)
        elif value == self.totalImageCount:
            self.previousPushButton.setEnabled(True)
            self.nextPushButton.setEnabled(False)
        else:
            self.previousPushButton.setEnabled(True)
            self.nextPushButton.setEnabled(True)

    @QtC.Slot(int)
    def onSelectionChanged(self, numSel):
        self.numSelectedSpinBox.setValue(numSel)
        self.clearPushButton.setEnabled(numSel)
        self.selectionViewPushButton.setEnabled(numSel)

    @QtC.Slot()
    def on_nextPushButton_pressed(self):
        self.currentImageSpinBox.setValue(self.currentImageSpinBox.value() + 1)

    @QtC.Slot()
    def on_previousPushButton_pressed(self):
        self.currentImageSpinBox.setValue(self.currentImageSpinBox.value() - 1)

    def onMainButtonPressed(self):
        imgIdx = self.listWidget.currentRow()
        if imgIdx < self.totalImageCount - 1:
            if self.additiveModeCheckBox.isChecked():
                _unselectedFound = imgIdx
                for idx in range(imgIdx + 1, self.totalImageCount):
                    if idx not in self.outputList:
                        _unselectedFound = idx
                        break
                if _unselectedFound == imgIdx:
                    self.sendTextToStatusBar.emit("后续所有图片已在选择集中", 3000, 2)
                else:
                    self.currentImageSpinBox.setValue(_unselectedFound + 1)
            else:
                self.nextPushButton.pressed.emit()
        else:
            self.sendTextToStatusBar.emit("已是最后一张图片", 3000, 2)
        return imgIdx

    @QtC.Slot()
    def on_adoptPushButton_pressed(self):
        imgIdx = self.onMainButtonPressed()
        self.onImageAdopted(imgIdx)

    @QtC.Slot()
    def on_abandonPushButton_pressed(self):
        imgIdx = self.onMainButtonPressed()
        self.onImageAbandoned(imgIdx)

    @QtC.Slot()
    def on_skipPushButton_pressed(self):
        self.onMainButtonPressed()

    @QtC.Slot()
    def on_clearPushButton_pressed(self):
        status = QtW.QMessageBox.question(
            self, '确认', '确认清空当前选择集？',
            QtW.QMessageBox.Ok | QtW.QMessageBox.Cancel)
        if status == QtW.QMessageBox.StandardButton.Cancel:
            return None
        clearList = copy(self.outputList)
        for imgIdx in clearList:
            self.onImageAbandoned(imgIdx)

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

    @QtC.Slot(bool)
    def on_action_Exit_triggered(self, triggered):
        self.close()

    @QtC.Slot(bool)
    def on_action_AnnotationConverter_triggered(self, triggered):
        self.annotationConverterWidget.show()

    @QtC.Slot(bool)
    def on_action_AnnotationExtractor_triggered(self, triggered):
        self.annotationExtractorWidget.show()

    @QtC.Slot(bool)
    def on_action_Console_triggered(self, triggered):
        if self._disableConsole:
            status = QtW.QMessageBox.critical(self, '错误', '控制台已被禁用。', QtW.QMessageBox.Ok)
        else:
            self.console.show()

    def initConsole(self):
        """
        初始化调试控制台。
        """
        self.console = QIPythonConsoleWidget(self, self)
        self.console.push({"sys": sys, "os": os, "QtC": QtC, "QtW": QtW, "QtG": QtG, "np": np, "pd": pd})

    @QtC.Slot(Exception)
    def workerExceptionHandler(self, e):
        raise e