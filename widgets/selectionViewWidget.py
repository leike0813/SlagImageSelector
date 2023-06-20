from pathlib import Path
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG
from ui.UiConfig_SelectionViewWidget import BaseSelectionViewWidget


all = ['SelectionViewWidget']


class SelectionViewWidget(BaseSelectionViewWidget, QtW.QWidget):
    sendAbandoned = QtC.Signal(int)

    def __init__(self, mainWindow, parent=None):
        super(SelectionViewWidget, self).__init__(parent)
        self.mainWindow = mainWindow
        self.setupUi(self)
        self.adjustUi()
        self.connectSignalToSlot()
        self.initialize()
        self.installEventFilter(self)

        # self.setWindowModality(QtC.Qt.NonModal) # for debugging

    def connectSignalToSlot(self):
        self.currentImageSpinBox_1.valueChanged.connect(self.showImage)
        self.currentImageSpinBox_2.valueChanged.connect(self.showImage)
        self.tableWidget.currentCellChanged.connect(self.onTableWidgetCellChanged)
        self.tabWidget.currentChanged.connect(self.onTabWidgetCurrentChanged)

    def initialize(self):
        self.workFld = None
        self.selection = []
        self.thumbnailScale = 0.1
        self.tableWidget.clear()
        self.imageWidget.clear()
        self.currentImageSpinBox_1.setMaximum(0)
        self.currentImageSpinBox_2.setMaximum(0)
        self.totalImagesLabel_1.setText(str(0))
        self.totalImagesLabel_2.setText(str(0))
        self.currentImageLineEdit_1.clear()
        self.currentImageLineEdit_2.clear()

    def eventFilter(self, watched, event):
        if watched == self and event.type() == QtC.QEvent.Resize:
            event.accept()
            self.drawThumbnails(self.tableWidget.size())
        return super(SelectionViewWidget, self).eventFilter(watched, event)

    @QtC.Slot(Path, list, set, float)
    def setSelection(self, workFld, imageNames, invalidImages, thumbnailScale):
        self.initialize()
        self.workFld = workFld
        self.selection = imageNames
        self.thumbnailScale = thumbnailScale
        self.thumbnails = [
            QtG.QPixmap(((workFld / '.thumbnail') / name).as_posix())
            if (workFld / name) not in invalidImages
            else QtG.QPixmap(w=int(2048 * self.thumbnailScale), h=int(4096 * self.thumbnailScale))
            for name in imageNames
        ]
        self.onSelectionChanged()
        self.show()
        self.resize(self.mainWindow.size())
        self.drawThumbnails(self.tableWidget.size())
        if self.totalImageCount > 0:
            self.currentImageSpinBox_1.setValue(1)

    @QtC.Slot(int)
    def showImage(self, imgNum, directCall=False):
        if imgNum > 0:
            if not directCall:
                if self.sender() == self.currentImageSpinBox_1:
                    self.currentImageSpinBox_2.valueChanged.disconnect(self.showImage)
                    self.tableWidget.currentCellChanged.disconnect(self.onTableWidgetCellChanged)
                    self.tableWidget.setCurrentCell(*self.thumbnailPosition(imgNum - 1))
                    self.currentImageSpinBox_2.setValue(imgNum)
                    self.currentImageSpinBox_2.valueChanged.connect(self.showImage)
                    self.tableWidget.currentCellChanged.connect(self.onTableWidgetCellChanged)
                elif self.sender() == self.currentImageSpinBox_2:
                    self.currentImageSpinBox_1.valueChanged.disconnect(self.showImage)
                    self.tableWidget.currentCellChanged.disconnect(self.onTableWidgetCellChanged)
                    self.tableWidget.setCurrentCell(*self.thumbnailPosition(imgNum - 1))
                    self.currentImageSpinBox_1.setValue(imgNum)
                    self.currentImageSpinBox_1.valueChanged.connect(self.showImage)
                    self.tableWidget.currentCellChanged.connect(self.onTableWidgetCellChanged)

            imageName = self.selection[imgNum - 1]
            self.imageWidget.origImageBox.setImage((self.workFld / imageName).as_posix())
            self.imageWidget.resultImageBox.setImage(((self.workFld / 'result') / imageName).as_posix())
            self.currentImageLineEdit_1.setText(str(imageName))
            self.currentImageLineEdit_2.setText(str(imageName))
        else:
            self.imageWidget.clear()
            self.currentImageLineEdit_1.clear()
            self.currentImageLineEdit_2.clear()

    @QtC.Slot(QtC.QSize)
    def drawThumbnails(self, size):
        curIdx = self.currentThumbnailIndex()
        self.tableWidget.clear()
        numColumns = max((size.width() - 20) // int(2048 * self.thumbnailScale), 1)
        columnWidth = (size.width() - 20) / numColumns
        numRows = (self.totalImageCount - 1) // numColumns + 1
        self.tableWidget.setColumnCount(numColumns)
        self.tableWidget.setRowCount(numRows)
        for i in range(numColumns):
            self.tableWidget.setColumnWidth(i, columnWidth)
        for j in range(numRows):
            self.tableWidget.setRowHeight(j, columnWidth * 2)
        for thumbIdx, thumb in enumerate(self.thumbnails):
            thumbItem = QtW.QTableWidgetItem()
            thumbItem.setFlags(QtC.Qt.ItemIsUserCheckable | QtC.Qt.ItemIsEnabled)
            thumbItem.setData(QtC.Qt.DisplayRole, thumb)
            self.tableWidget.setItem(thumbIdx // numColumns, thumbIdx % numColumns, thumbItem)
        self.tableWidget.setCurrentCell(curIdx // numColumns, curIdx % numColumns)
        self.tableWidget.update()