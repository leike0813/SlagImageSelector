# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from lib.customWidgets.synchronizeImageWidget import SynchronizeImageWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(819, 600)
        self.action_OpenFolder = QAction(MainWindow)
        self.action_OpenFolder.setObjectName(u"action_OpenFolder")
        self.action_OpenFolder.setCheckable(False)
        self.action_Save = QAction(MainWindow)
        self.action_Save.setObjectName(u"action_Save")
        self.action_Save.setEnabled(False)
        self.action_Exit = QAction(MainWindow)
        self.action_Exit.setObjectName(u"action_Exit")
        self.action_Console = QAction(MainWindow)
        self.action_Console.setObjectName(u"action_Console")
        self.action_Export = QAction(MainWindow)
        self.action_Export.setObjectName(u"action_Export")
        self.action_Export.setCheckable(False)
        self.action_Export.setEnabled(False)
        self.action_AnnotationConverter = QAction(MainWindow)
        self.action_AnnotationConverter.setObjectName(u"action_AnnotationConverter")
        self.action_AnnotationConverter.setCheckable(False)
        self.action_GroundTruthConverter = QAction(MainWindow)
        self.action_GroundTruthConverter.setObjectName(u"action_GroundTruthConverter")
        self.action_GroundTruthConverter.setCheckable(False)
        self.action_AnnotationExtractor = QAction(MainWindow)
        self.action_AnnotationExtractor.setObjectName(u"action_AnnotationExtractor")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_3 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)

        self.imageWidget = SynchronizeImageWidget(self.centralwidget)
        self.imageWidget.setObjectName(u"imageWidget")
        self.imageWidget.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.imageWidget.sizePolicy().hasHeightForWidth())
        self.imageWidget.setSizePolicy(sizePolicy)
        self.imageWidget.setMinimumSize(QSize(100, 200))
        self.imageWidget.setBaseSize(QSize(2048, 4096))

        self.horizontalLayout.addWidget(self.imageWidget)

        self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_6)

        self.horizontalLayout.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.controlButtonHorizontalLayout = QHBoxLayout()
        self.controlButtonHorizontalLayout.setObjectName(u"controlButtonHorizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.controlButtonHorizontalLayout.addItem(self.horizontalSpacer)

        self.adoptPushButton = QPushButton(self.centralwidget)
        self.adoptPushButton.setObjectName(u"adoptPushButton")
        self.adoptPushButton.setEnabled(False)

        self.controlButtonHorizontalLayout.addWidget(self.adoptPushButton)

        self.abandonPushButton = QPushButton(self.centralwidget)
        self.abandonPushButton.setObjectName(u"abandonPushButton")
        self.abandonPushButton.setEnabled(False)

        self.controlButtonHorizontalLayout.addWidget(self.abandonPushButton)

        self.skipPushButton = QPushButton(self.centralwidget)
        self.skipPushButton.setObjectName(u"skipPushButton")
        self.skipPushButton.setEnabled(False)

        self.controlButtonHorizontalLayout.addWidget(self.skipPushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.controlButtonHorizontalLayout.addItem(self.horizontalSpacer_2)

        self.additiveModeCheckBox = QCheckBox(self.centralwidget)
        self.additiveModeCheckBox.setObjectName(u"additiveModeCheckBox")

        self.controlButtonHorizontalLayout.addWidget(self.additiveModeCheckBox)

        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.controlButtonHorizontalLayout.addWidget(self.label)

        self.numSelectedSpinBox = QSpinBox(self.centralwidget)
        self.numSelectedSpinBox.setObjectName(u"numSelectedSpinBox")
        self.numSelectedSpinBox.setEnabled(True)
        self.numSelectedSpinBox.setAutoFillBackground(True)
        self.numSelectedSpinBox.setFrame(False)
        self.numSelectedSpinBox.setAlignment(Qt.AlignCenter)
        self.numSelectedSpinBox.setReadOnly(True)
        self.numSelectedSpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numSelectedSpinBox.setMaximum(9999)

        self.controlButtonHorizontalLayout.addWidget(self.numSelectedSpinBox)

        self.clearPushButton = QPushButton(self.centralwidget)
        self.clearPushButton.setObjectName(u"clearPushButton")
        self.clearPushButton.setEnabled(False)

        self.controlButtonHorizontalLayout.addWidget(self.clearPushButton)

        self.selectionViewPushButton = QPushButton(self.centralwidget)
        self.selectionViewPushButton.setObjectName(u"selectionViewPushButton")
        self.selectionViewPushButton.setEnabled(False)

        self.controlButtonHorizontalLayout.addWidget(self.selectionViewPushButton)


        self.verticalLayout_2.addLayout(self.controlButtonHorizontalLayout)

        self.verticalLayout_2.setStretch(0, 19)
        self.verticalLayout_2.setStretch(1, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.listWidget = QListWidget(self.centralwidget)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout_3.addWidget(self.listWidget)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.previousPushButton = QPushButton(self.centralwidget)
        self.previousPushButton.setObjectName(u"previousPushButton")
        self.previousPushButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.previousPushButton)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)

        self.currentImageSpinBox = QSpinBox(self.centralwidget)
        self.currentImageSpinBox.setObjectName(u"currentImageSpinBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.currentImageSpinBox.sizePolicy().hasHeightForWidth())
        self.currentImageSpinBox.setSizePolicy(sizePolicy1)
        self.currentImageSpinBox.setMinimumSize(QSize(40, 20))
        self.currentImageSpinBox.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.currentImageSpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.currentImageSpinBox.setMaximum(0)

        self.horizontalLayout_4.addWidget(self.currentImageSpinBox)

        self.totalImagesLabel = QLabel(self.centralwidget)
        self.totalImagesLabel.setObjectName(u"totalImagesLabel")
        self.totalImagesLabel.setMinimumSize(QSize(40, 20))
        self.totalImagesLabel.setMaximumSize(QSize(60, 40))

        self.horizontalLayout_4.addWidget(self.totalImagesLabel)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_4)

        self.nextPushButton = QPushButton(self.centralwidget)
        self.nextPushButton.setObjectName(u"nextPushButton")
        self.nextPushButton.setEnabled(False)

        self.horizontalLayout_4.addWidget(self.nextPushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.verticalLayout_3.setStretch(0, 19)
        self.verticalLayout_3.setStretch(1, 1)

        self.horizontalLayout_3.addLayout(self.verticalLayout_3)

        self.horizontalLayout_3.setStretch(0, 8)
        self.horizontalLayout_3.setStretch(1, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 819, 23))
        self.menu = QMenu(self.menubar)
        self.menu.setObjectName(u"menu")
        self.tools = QMenu(self.menubar)
        self.tools.setObjectName(u"tools")
        self.about = QMenu(self.menubar)
        self.about.setObjectName(u"about")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QSize(32, 32))
        self.toolBar.setFloatable(False)
        MainWindow.addToolBar(Qt.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.tools.menuAction())
        self.menubar.addAction(self.about.menuAction())
        self.menu.addAction(self.action_OpenFolder)
        self.menu.addAction(self.action_Save)
        self.menu.addAction(self.action_Export)
        self.menu.addSeparator()
        self.menu.addAction(self.action_Exit)
        self.tools.addAction(self.action_AnnotationConverter)
        self.tools.addAction(self.action_AnnotationExtractor)
        self.tools.addAction(self.action_GroundTruthConverter)
        self.about.addAction(self.action_Console)
        self.toolBar.addAction(self.action_OpenFolder)
        self.toolBar.addAction(self.action_Save)
        self.toolBar.addAction(self.action_Export)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_AnnotationConverter)
        self.toolBar.addAction(self.action_AnnotationExtractor)
        self.toolBar.addAction(self.action_GroundTruthConverter)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.action_Console)
        self.toolBar.addAction(self.action_Exit)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u6e23\u571f\u56fe\u50cf\u7b5b\u9009", None))
        self.action_OpenFolder.setText(QCoreApplication.translate("MainWindow", u"\u6253\u5f00\u6587\u4ef6\u5939", None))
        self.action_Save.setText(QCoreApplication.translate("MainWindow", u"\u4fdd\u5b58\u9009\u62e9\u96c6", None))
        self.action_Exit.setText(QCoreApplication.translate("MainWindow", u"\u9000\u51fa", None))
        self.action_Console.setText(QCoreApplication.translate("MainWindow", u"\u63a7\u5236\u53f0", None))
        self.action_Export.setText(QCoreApplication.translate("MainWindow", u"\u5bfc\u51fa\u9009\u62e9\u96c6", None))
        self.action_AnnotationConverter.setText(QCoreApplication.translate("MainWindow", u"\u6807\u6ce8\u8f6c\u6362\u5668", None))
        self.action_GroundTruthConverter.setText(QCoreApplication.translate("MainWindow", u"\u771f\u503c\u8f6c\u6362\u5668", None))
        self.action_AnnotationExtractor.setText(QCoreApplication.translate("MainWindow", u"\u6807\u6ce8\u63d0\u53d6\u5668", None))
#if QT_CONFIG(tooltip)
        self.adoptPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u5c06\u5f53\u524d\u56fe\u7247\u52a0\u5165\u9009\u62e9\u96c6", None))
#endif // QT_CONFIG(tooltip)
        self.adoptPushButton.setText(QCoreApplication.translate("MainWindow", u"\u91c7\u7528(A)", None))
#if QT_CONFIG(shortcut)
        self.adoptPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"A", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.abandonPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u4e0d\u91c7\u7528\u5f53\u524d\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.abandonPushButton.setText(QCoreApplication.translate("MainWindow", u"\u653e\u5f03(D)", None))
#if QT_CONFIG(shortcut)
        self.abandonPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"D", None))
#endif // QT_CONFIG(shortcut)
#if QT_CONFIG(tooltip)
        self.skipPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u8df3\u8fc7\u5f53\u524d\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.skipPushButton.setText(QCoreApplication.translate("MainWindow", u"\u8df3\u8fc7(S)", None))
#if QT_CONFIG(shortcut)
        self.skipPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"S", None))
#endif // QT_CONFIG(shortcut)
        self.additiveModeCheckBox.setText(QCoreApplication.translate("MainWindow", u"\u589e\u9009\u6a21\u5f0f", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u5f53\u524d\u5df2\u9009\u62e9:", None))
        self.clearPushButton.setText(QCoreApplication.translate("MainWindow", u"\u6e05\u7a7a(Ctrl+Del)", None))
#if QT_CONFIG(shortcut)
        self.clearPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Del", None))
#endif // QT_CONFIG(shortcut)
        self.selectionViewPushButton.setText(QCoreApplication.translate("MainWindow", u"\u67e5\u770b\u5df2\u9009", None))
#if QT_CONFIG(tooltip)
        self.previousPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u4e0a\u4e00\u5f20\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.previousPushButton.setText("")
#if QT_CONFIG(shortcut)
        self.previousPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Left", None))
#endif // QT_CONFIG(shortcut)
        self.totalImagesLabel.setText(QCoreApplication.translate("MainWindow", u"/ 0", None))
#if QT_CONFIG(tooltip)
        self.nextPushButton.setToolTip(QCoreApplication.translate("MainWindow", u"\u4e0b\u4e00\u5f20\u56fe\u7247", None))
#endif // QT_CONFIG(tooltip)
        self.nextPushButton.setText("")
#if QT_CONFIG(shortcut)
        self.nextPushButton.setShortcut(QCoreApplication.translate("MainWindow", u"Right", None))
#endif // QT_CONFIG(shortcut)
        self.menu.setTitle(QCoreApplication.translate("MainWindow", u"\u83dc\u5355", None))
        self.tools.setTitle(QCoreApplication.translate("MainWindow", u"\u5de5\u5177", None))
        self.about.setTitle(QCoreApplication.translate("MainWindow", u"\u5173\u4e8e", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

