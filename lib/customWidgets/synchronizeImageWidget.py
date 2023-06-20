# -*- coding: utf-8 -*-
import PySide2.QtWidgets as QtW, PySide2.QtCore as QtC, PySide2.QtGui as QtG


__all__ = ['SynchronizeImageWidget']


class SynchronizeImageWidget(QtW.QWidget):
    def __init__(self, parent=None):
        super(SynchronizeImageWidget, self).__init__(parent)
        self.setupUi(self)
        self.installEventFilter(self)
        self.origImageBox.installEventFilter(self)
        self.resultImageBox.installEventFilter(self)

    def setupUi(self, widget):
        widget.horizontalLayout = QtW.QHBoxLayout(widget)
        widget.horizontalLayout.setObjectName(u"horizontalLayout")
        widget.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        widget.origImageScrollArea = QtW.QScrollArea(widget)
        widget.origImageScrollArea.setObjectName(u"origImageScrollArea")
        widget.origImageScrollArea.setMinimumSize(QtC.QSize(0, 0))
        widget.origImageScrollArea.setAlignment(QtC.Qt.AlignCenter)
        widget.origImageScrollArea.setHorizontalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
        widget.origImageScrollArea.setVerticalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
        widget.origImageBox = ImageBox(widget)
        widget.origImageBox.setObjectName(u"origImageBox")
        widget.origImageBox.setGeometry(QtC.QRect(0, 0, 2048, 4096))
        widget.origImageBox.setMinimumSize(widget.size())
        widget.origImageScrollArea.setWidget(widget.origImageBox)

        widget.horizontalLayout.addWidget(widget.origImageScrollArea)

        widget.horizontalSpacer = QtW.QSpacerItem(40, 20, QtW.QSizePolicy.Preferred, QtW.QSizePolicy.Minimum)

        widget.horizontalLayout.addItem(widget.horizontalSpacer)

        widget.resultImageScrollArea = QtW.QScrollArea(widget)
        widget.resultImageScrollArea.setObjectName(u"resultImageScrollArea")
        widget.resultImageScrollArea.setMinimumSize(QtC.QSize(0, 0))
        widget.resultImageScrollArea.setAlignment(QtC.Qt.AlignCenter)
        widget.resultImageScrollArea.setHorizontalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
        widget.resultImageScrollArea.setVerticalScrollBarPolicy(QtC.Qt.ScrollBarAlwaysOff)
        widget.resultImageBox = ImageBox(widget)
        widget.resultImageBox.setObjectName(u"resultImageBox")
        widget.resultImageBox.setGeometry(QtC.QRect(0, 0, 2048, 4096))
        widget.resultImageBox.setMinimumSize(widget.size())
        widget.resultImageScrollArea.setWidget(widget.resultImageBox)

        widget.horizontalLayout.addWidget(widget.resultImageScrollArea)
        widget.horizontalLayout.setStretch(0, 1)
        widget.horizontalLayout.setStretch(1, 0)
        widget.horizontalLayout.setStretch(2, 1)
        widget.horizontalLayout.setAlignment(QtC.Qt.AlignHCenter)

        QtC.QMetaObject.connectSlotsByName(widget)

    def eventFilter(self, watched, event):
        if watched is self.origImageBox or watched is self.resultImageBox:
            if event.type() in [
                QtC.QEvent.Wheel,
                QtC.QEvent.MouseMove,
                QtC.QEvent.MouseButtonPress,
                QtC.QEvent.MouseButtonRelease
            ]:
                event.accept()
                self.origImageBox.event(event)
                self.resultImageBox.event(event)
                return True
        return super(SynchronizeImageWidget, self).eventFilter(watched, event)

    def clear(self):
        self.origImageBox.clear()
        self.resultImageBox.clear()


class ImageBox(QtW.QWidget):
    def __init__(self, parent=None):
        super(ImageBox, self).__init__(parent)
        self.initialize()

    def initialize(self):
        self.img = None
        self.scaled_img = None
        self.start_pos = None
        self.end_pos = None
        self.left_click = False
        self.wheel_flag = False

        self.scale = 1
        self.old_scale = 1
        self.point = QtC.QPoint(0, 0)
        self.x = -1
        self.y = -1
        self.new_height = -1
        self.new_width = -1

    def setImage(self, img_path):
        # self.img = QtG.QPixmap(img_path)
        self.img = QtG.QImage(img_path)
        width, height = self.img.width(), self.img.height()
        if height / width > 4096 / 2048:
            new_height = 4096
            new_width = width * 4096 / height
        else:
            new_height = height * 2048 / width
            new_width = 2048
        self.point = QtC.QPoint(int((2048 - new_width) * 0.5), int((4096 - new_height) * 0.5))
        self.img = self.img.scaled(new_width, new_height, QtG.Qt.KeepAspectRatio)
        self.scaled_img = self.img

        self.new_height = new_height
        self.new_width = new_width
        self.scale = 0.5
        self.update()

    def clear(self):
        self.initialize()
        self.update()

    def paintEvent(self, e):
        if self.scaled_img:
            painter = QtG.QPainter()
            painter.begin(self)
            painter.scale(self.scale, self.scale)
            if self.wheel_flag:  # 定点缩放
                self.wheel_flag = False
                # 判断当前鼠标pos在不在图上
                this_left_x = self.point.x() * self.old_scale
                this_left_y = self.point.y() * self.old_scale
                this_scale_width = self.new_width * self.old_scale
                this_scale_height = self.new_height * self.old_scale

                # 鼠标点在图上，以鼠标点为中心动作
                gap_x = self.x - this_left_x
                gap_y = self.y - this_left_y
                if 0 < gap_x < this_scale_width and 0 < gap_y < this_scale_height:
                    new_left_x = int(self.x / self.scale - gap_x / self.old_scale)
                    new_left_y = int(self.y / self.scale - gap_y / self.old_scale)
                    self.point = QtC.QPoint(new_left_x, new_left_y)
                # 鼠标点不在图上，固定左上角进行缩放
                else:
                    true_left_x = int(self.point.x() * self.old_scale / self.scale)
                    true_left_y = int(self.point.y() * self.old_scale / self.scale)
                    self.point = QtC.QPoint(true_left_x, true_left_y)
            # painter.drawPixmap(self.point, self.scaled_img)  # 此函数中还会用scale对point进行处理
            painter.drawImage(self.point, self.scaled_img)
            painter.end()

    def wheelEvent(self, event):
        if self.scaled_img:
            angle = event.angleDelta() / 8  # 返回QtC.QPoint对象，为滚轮转过的数值，单位为1/8度
            angleY = angle.y()
            self.old_scale = self.scale
            self.x, self.y = event.x(), event.y()
            self.wheel_flag = True
            # 获取当前鼠标相对于view的位置
            if angleY > 0:
                self.scale *= 1.08
            else:  # 滚轮下滚
                self.scale *= 0.92
            if self.scale < 0.2:
                self.scale = 0.2
            self.adjustSize()
            self.update()

    def mouseMoveEvent(self, e):
        if self.scaled_img:
            if self.left_click:
                self.end_pos = e.pos() - self.start_pos  # 当前位置-起始位置=差值
                self.point = self.point + self.end_pos / self.scale  # 左上角的距离变化
                self.start_pos = e.pos()
                self.repaint()

    def mousePressEvent(self, e):
        if self.scaled_img:
            if e.button() == QtG.Qt.LeftButton:
                self.left_click = True
                self.start_pos = e.pos()

    def mouseReleaseEvent(self, e):
        if self.scaled_img:
            if e.button() == QtG.Qt.LeftButton:
                self.left_click = False



