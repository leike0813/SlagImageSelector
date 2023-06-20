import PySide2.QtCore as QtC, PySide2.QtGui as QtG
from lib.customDelegates import QPixmapItemDelegate
from ui.Ui_SelectionViewWidget import Ui_SelectionViewWidget
import qtawesome as qta


__all__ = ['BaseSelectionViewWidget']


class BaseSelectionViewWidget(Ui_SelectionViewWidget):
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
            self.abandonPushButton_1,
            self.abandonPushButton_2,
        ]

        self.nextPushButton.setIcon(
            qta.icon('mdi6.arrow-right-circle', color='deepskyblue', scale_factor=iconScale))
        self.nextPushButton.setIconSize(iconSize)
        self.nextPushButton.setMinimumSize(iconSize)

        self.previousPushButton.setIcon(
            qta.icon('mdi6.arrow-left-circle', color='deepskyblue', scale_factor=iconScale))
        self.previousPushButton.setIconSize(iconSize)
        self.previousPushButton.setMinimumSize(iconSize)

        self.abandonPushButton_1.setIcon(
            qta.icon('mdi6.close-circle', color='red', scale_factor=iconScale))
        self.abandonPushButton_1.setFont(font)
        self.abandonPushButton_1.setIconSize(iconSize)
        self.abandonPushButton_1.setMinimumHeight(iconSize.height())

        self.abandonPushButton_2.setIcon(
            qta.icon('mdi6.close-circle', color='red', scale_factor=iconScale))
        self.abandonPushButton_2.setFont(font)
        self.abandonPushButton_2.setIconSize(iconSize)
        self.abandonPushButton_2.setMinimumHeight(iconSize.height())

        self.switchPushButton_1.setIcon(
            qta.icon('mdi6.toggle-switch-off', color='darkred', scale_factor=iconScale))
        self.switchPushButton_1.setFont(font)
        self.switchPushButton_1.setIconSize(iconSize)
        self.switchPushButton_1.setMinimumHeight(iconSize.height())

        self.switchPushButton_2.setIcon(
            qta.icon('mdi6.toggle-switch', color='darkgreen', scale_factor=iconScale))
        self.switchPushButton_2.setFont(font)
        self.switchPushButton_2.setIconSize(iconSize)
        self.switchPushButton_2.setMinimumHeight(iconSize.height())

        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setVerticalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOn)
        self.tableWidget.setItemDelegate(QPixmapItemDelegate())

    @property
    def totalImageCount(self):
        return len(self.selection)

    def thumbnailIndex(self, row, column):
        if row == -1 or column == -1:
            return -1
        columnCount = self.tableWidget.columnCount()
        return row * self.tableWidget.columnCount() + column

    def currentThumbnailIndex(self):
        return self.thumbnailIndex(self.tableWidget.currentRow(), self.tableWidget.currentColumn())

    def thumbnailPosition(self, index):
        if index == -1:
            return -1, -1
        columnCount = self.tableWidget.columnCount()
        row = index // columnCount if columnCount > 0 else -1
        column = index % columnCount if columnCount > 0 else -1
        return row, column

    def onSelectionChanged(self):
        self.totalImagesLabel_1.setText(str(self.totalImageCount))
        self.totalImagesLabel_2.setText(str(self.totalImageCount))
        self.currentImageSpinBox_1.setMaximum(self.totalImageCount)
        self.currentImageSpinBox_2.setMaximum(self.totalImageCount)
        if self.totalImageCount > 0:
            for btn in self.buttons:
                btn.setEnabled(True)
        else:
            for btn in self.buttons:
                btn.setEnabled(False)

    @QtC.Slot(int)
    def on_currentImageSpinBox_2_valueChanged(self, value):
        if self.totalImageCount == 0 or self.totalImageCount == 1:
            self.previousPushButton.setEnabled(False)
            self.nextPushButton.setEnabled(False)
        else:
            if value == 1:
                self.previousPushButton.setEnabled(False)
                self.nextPushButton.setEnabled(True)
            elif value == self.totalImageCount:
                self.previousPushButton.setEnabled(True)
                self.nextPushButton.setEnabled(False)
            else:
                self.previousPushButton.setEnabled(True)
                self.nextPushButton.setEnabled(True)

    @QtC.Slot()
    def on_nextPushButton_pressed(self):
        self.currentImageSpinBox_2.setValue(self.currentImageSpinBox_2.value() + 1)

    @QtC.Slot()
    def on_previousPushButton_pressed(self):
        self.currentImageSpinBox_2.setValue(self.currentImageSpinBox_2.value() - 1)

    @QtC.Slot()
    def on_abandonPushButton_1_pressed(self):
        curNum = self.currentImageSpinBox_1.value()
        self.sendAbandoned.emit(
            list(self.mainWindow.imageLib['Orig_Image']).index(self.selection.pop(curNum - 1)))
        self.thumbnails.pop(curNum - 1)
        self.onSelectionChanged()
        self.drawThumbnails(self.tableWidget.size())
        self.currentImageSpinBox_2.setValue(curNum if curNum < self.totalImageCount + 1 else curNum - 1)
        self.on_currentImageSpinBox_2_valueChanged(curNum if curNum < self.totalImageCount + 1 else curNum - 1) # manually call the slot because the value may not be changed
        self.showImage(self.currentImageSpinBox_2.value(), directCall=True)

    @QtC.Slot()
    def on_abandonPushButton_2_pressed(self):
        self.on_abandonPushButton_1_pressed()

    @QtC.Slot()
    def on_switchPushButton_1_pressed(self):
        self.tabWidget.setCurrentIndex(1)

    @QtC.Slot()
    def on_switchPushButton_2_pressed(self):
        self.tabWidget.setCurrentIndex(0)

    @QtC.Slot(int)
    def onTabWidgetCurrentChanged(self, index):
        self.switchPushButton_1.setEnabled(not index)
        self.switchPushButton_2.setEnabled(index)

    @QtC.Slot(int, int, int, int)
    def onTableWidgetCellChanged(self, currentRow, currentColumn, previousRow, previousColumn):
        if currentRow >= 0 and currentColumn >= 0:
            self.currentImageSpinBox_1.setValue(self.thumbnailIndex(currentRow, currentColumn) + 1)