# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_SelectionViewWidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from lib.customWidgets.synchronizeImageWidget import SynchronizeImageWidget


class Ui_SelectionViewWidget(object):
    def setupUi(self, SelectionViewWidget):
        if not SelectionViewWidget.objectName():
            SelectionViewWidget.setObjectName(u"SelectionViewWidget")
        SelectionViewWidget.setWindowModality(Qt.ApplicationModal)
        SelectionViewWidget.resize(800, 600)
        self.verticalLayout = QVBoxLayout(SelectionViewWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(SelectionViewWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.thumbnailTab = QWidget()
        self.thumbnailTab.setObjectName(u"thumbnailTab")
        self.verticalLayout_2 = QVBoxLayout(self.thumbnailTab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tableWidget = QTableWidget(self.thumbnailTab)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout_2.addWidget(self.tableWidget)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.switchPushButton_1 = QPushButton(self.thumbnailTab)
        self.switchPushButton_1.setObjectName(u"switchPushButton_1")

        self.horizontalLayout_2.addWidget(self.switchPushButton_1)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.currentImageSpinBox_1 = QSpinBox(self.thumbnailTab)
        self.currentImageSpinBox_1.setObjectName(u"currentImageSpinBox_1")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.currentImageSpinBox_1.sizePolicy().hasHeightForWidth())
        self.currentImageSpinBox_1.setSizePolicy(sizePolicy)
        self.currentImageSpinBox_1.setMinimumSize(QSize(40, 20))
        self.currentImageSpinBox_1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.currentImageSpinBox_1.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.currentImageSpinBox_1.setMaximum(0)

        self.horizontalLayout_2.addWidget(self.currentImageSpinBox_1)

        self.totalImagesLabel_1 = QLabel(self.thumbnailTab)
        self.totalImagesLabel_1.setObjectName(u"totalImagesLabel_1")
        self.totalImagesLabel_1.setMinimumSize(QSize(40, 20))
        self.totalImagesLabel_1.setMaximumSize(QSize(60, 40))

        self.horizontalLayout_2.addWidget(self.totalImagesLabel_1)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.abandonPushButton_1 = QPushButton(self.thumbnailTab)
        self.abandonPushButton_1.setObjectName(u"abandonPushButton_1")
        self.abandonPushButton_1.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.abandonPushButton_1)

        self.currentImageLineEdit_1 = QLineEdit(self.thumbnailTab)
        self.currentImageLineEdit_1.setObjectName(u"currentImageLineEdit_1")
        self.currentImageLineEdit_1.setMinimumSize(QSize(400, 20))
        self.currentImageLineEdit_1.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.currentImageLineEdit_1.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.currentImageLineEdit_1)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.setStretch(0, 1)
        self.tabWidget.addTab(self.thumbnailTab, "")
        self.fullScaleTab = QWidget()
        self.fullScaleTab.setObjectName(u"fullScaleTab")
        self.verticalLayout_3 = QVBoxLayout(self.fullScaleTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.imageWidget = SynchronizeImageWidget(self.fullScaleTab)
        self.imageWidget.setObjectName(u"imageWidget")

        self.verticalLayout_3.addWidget(self.imageWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.switchPushButton_2 = QPushButton(self.fullScaleTab)
        self.switchPushButton_2.setObjectName(u"switchPushButton_2")
        self.switchPushButton_2.setEnabled(False)

        self.horizontalLayout.addWidget(self.switchPushButton_2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.previousPushButton = QPushButton(self.fullScaleTab)
        self.previousPushButton.setObjectName(u"previousPushButton")
        self.previousPushButton.setEnabled(False)

        self.horizontalLayout.addWidget(self.previousPushButton)

        self.currentImageSpinBox_2 = QSpinBox(self.fullScaleTab)
        self.currentImageSpinBox_2.setObjectName(u"currentImageSpinBox_2")
        sizePolicy.setHeightForWidth(self.currentImageSpinBox_2.sizePolicy().hasHeightForWidth())
        self.currentImageSpinBox_2.setSizePolicy(sizePolicy)
        self.currentImageSpinBox_2.setMinimumSize(QSize(40, 20))
        self.currentImageSpinBox_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.currentImageSpinBox_2.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.currentImageSpinBox_2.setMaximum(0)

        self.horizontalLayout.addWidget(self.currentImageSpinBox_2)

        self.totalImagesLabel_2 = QLabel(self.fullScaleTab)
        self.totalImagesLabel_2.setObjectName(u"totalImagesLabel_2")
        self.totalImagesLabel_2.setMinimumSize(QSize(40, 20))
        self.totalImagesLabel_2.setMaximumSize(QSize(60, 40))

        self.horizontalLayout.addWidget(self.totalImagesLabel_2)

        self.nextPushButton = QPushButton(self.fullScaleTab)
        self.nextPushButton.setObjectName(u"nextPushButton")
        self.nextPushButton.setEnabled(False)

        self.horizontalLayout.addWidget(self.nextPushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.abandonPushButton_2 = QPushButton(self.fullScaleTab)
        self.abandonPushButton_2.setObjectName(u"abandonPushButton_2")
        self.abandonPushButton_2.setEnabled(False)

        self.horizontalLayout.addWidget(self.abandonPushButton_2)

        self.currentImageLineEdit_2 = QLineEdit(self.fullScaleTab)
        self.currentImageLineEdit_2.setObjectName(u"currentImageLineEdit_2")
        self.currentImageLineEdit_2.setMinimumSize(QSize(400, 20))
        self.currentImageLineEdit_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.currentImageLineEdit_2.setReadOnly(True)

        self.horizontalLayout.addWidget(self.currentImageLineEdit_2)


        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.verticalLayout_3.setStretch(0, 1)
        self.tabWidget.addTab(self.fullScaleTab, "")

        self.verticalLayout.addWidget(self.tabWidget)


        self.retranslateUi(SelectionViewWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(SelectionViewWidget)
    # setupUi

    def retranslateUi(self, SelectionViewWidget):
        SelectionViewWidget.setWindowTitle(QCoreApplication.translate("SelectionViewWidget", u"\u9009\u62e9\u96c6\u67e5\u770b\u5668", None))
        self.switchPushButton_1.setText(QCoreApplication.translate("SelectionViewWidget", u"\u5207\u6362\u5230\u539f\u56fe(\u7a7a\u683c)", None))
#if QT_CONFIG(shortcut)
        self.switchPushButton_1.setShortcut(QCoreApplication.translate("SelectionViewWidget", u"Space", None))
#endif // QT_CONFIG(shortcut)
        self.totalImagesLabel_1.setText(QCoreApplication.translate("SelectionViewWidget", u"/ 0", None))
#if QT_CONFIG(tooltip)
        self.abandonPushButton_1.setToolTip(QCoreApplication.translate("SelectionViewWidget", u"\u4e0d\u91c7\u7528\u5f53\u524d\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.abandonPushButton_1.setText(QCoreApplication.translate("SelectionViewWidget", u"\u4ece\u5f53\u524d\u9009\u62e9\u96c6\u4e2d\u5220\u9664(D)", None))
#if QT_CONFIG(shortcut)
        self.abandonPushButton_1.setShortcut(QCoreApplication.translate("SelectionViewWidget", u"D", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.thumbnailTab), QCoreApplication.translate("SelectionViewWidget", u"\u7f29\u7565\u56fe", None))
        self.switchPushButton_2.setText(QCoreApplication.translate("SelectionViewWidget", u"\u5207\u6362\u5230\u7f29\u7565\u56fe(\u7a7a\u683c)", None))
#if QT_CONFIG(shortcut)
        self.switchPushButton_2.setShortcut(QCoreApplication.translate("SelectionViewWidget", u"Space", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.previousPushButton.setToolTip(QCoreApplication.translate("SelectionViewWidget", u"\u4e0a\u4e00\u5f20\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.previousPushButton.setText("")
#if QT_CONFIG(shortcut)
        self.previousPushButton.setShortcut(QCoreApplication.translate("SelectionViewWidget", u"Left", None))
#endif // QT_CONFIG(shortcut)
        self.totalImagesLabel_2.setText(QCoreApplication.translate("SelectionViewWidget", u"/ 0", None))
#if QT_CONFIG(tooltip)
        self.nextPushButton.setToolTip(QCoreApplication.translate("SelectionViewWidget", u"\u4e0b\u4e00\u5f20\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.nextPushButton.setText("")
#if QT_CONFIG(shortcut)
        self.nextPushButton.setShortcut(QCoreApplication.translate("SelectionViewWidget", u"Right", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.abandonPushButton_2.setToolTip(QCoreApplication.translate("SelectionViewWidget", u"\u4e0d\u91c7\u7528\u5f53\u524d\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.abandonPushButton_2.setText(QCoreApplication.translate("SelectionViewWidget", u"\u4ece\u5f53\u524d\u9009\u62e9\u96c6\u4e2d\u5220\u9664(D)", None))
#if QT_CONFIG(shortcut)
        self.abandonPushButton_2.setShortcut(QCoreApplication.translate("SelectionViewWidget", u"D", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fullScaleTab), QCoreApplication.translate("SelectionViewWidget", u"\u539f\u56fe", None))
    # retranslateUi

