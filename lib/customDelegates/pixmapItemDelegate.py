import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG


class QPixmapItemDelegate(QtW.QStyledItemDelegate):
    # def __init__(self, parent=None):
    #     super(QPixmapItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        pix = index.data(QtC.Qt.DisplayRole)
        if isinstance(pix, QtG.QPixmap):
            painter.drawPixmap(option.rect, pix)
        super(QPixmapItemDelegate, self).paint(painter, option, index)