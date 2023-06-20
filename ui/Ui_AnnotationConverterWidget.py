# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AnnotationConverterWidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_AnnotationConverterWidget(object):
    def setupUi(self, AnnotationConverterWidget):
        if not AnnotationConverterWidget.objectName():
            AnnotationConverterWidget.setObjectName(u"AnnotationConverterWidget")
        AnnotationConverterWidget.setWindowModality(Qt.WindowModal)
        AnnotationConverterWidget.resize(800, 150)
        self.verticalLayout = QVBoxLayout(AnnotationConverterWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 9, -1, -1)
        self.tabWidget = QTabWidget(AnnotationConverterWidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.batchConvertTab = QWidget()
        self.batchConvertTab.setObjectName(u"batchConvertTab")
        self.verticalLayout_2 = QVBoxLayout(self.batchConvertTab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.batchConvertTab)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.targetFolderLineEdit = QLineEdit(self.batchConvertTab)
        self.targetFolderLineEdit.setObjectName(u"targetFolderLineEdit")
        self.targetFolderLineEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.targetFolderLineEdit)

        self.browseFolderPushButton = QPushButton(self.batchConvertTab)
        self.browseFolderPushButton.setObjectName(u"browseFolderPushButton")

        self.horizontalLayout.addWidget(self.browseFolderPushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.newPushButton = QPushButton(self.batchConvertTab)
        self.newPushButton.setObjectName(u"newPushButton")
        self.newPushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.newPushButton)

        self.mergePushButton = QPushButton(self.batchConvertTab)
        self.mergePushButton.setObjectName(u"mergePushButton")
        self.mergePushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.mergePushButton)

        self.overwritePushButton = QPushButton(self.batchConvertTab)
        self.overwritePushButton.setObjectName(u"overwritePushButton")
        self.overwritePushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.overwritePushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.tabWidget.addTab(self.batchConvertTab, "")
        self.singleConvertTab = QWidget()
        self.singleConvertTab.setObjectName(u"singleConvertTab")
        self.verticalLayout_3 = QVBoxLayout(self.singleConvertTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.singleConvertTab)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_4.addWidget(self.label_2)

        self.targetFileLineEdit = QLineEdit(self.singleConvertTab)
        self.targetFileLineEdit.setObjectName(u"targetFileLineEdit")
        self.targetFileLineEdit.setReadOnly(True)

        self.horizontalLayout_4.addWidget(self.targetFileLineEdit)

        self.browseFilePushButton = QPushButton(self.singleConvertTab)
        self.browseFilePushButton.setObjectName(u"browseFilePushButton")

        self.horizontalLayout_4.addWidget(self.browseFilePushButton)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.convertFilePushButton = QPushButton(self.singleConvertTab)
        self.convertFilePushButton.setObjectName(u"convertFilePushButton")
        self.convertFilePushButton.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.convertFilePushButton)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.tabWidget.addTab(self.singleConvertTab, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(AnnotationConverterWidget)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(AnnotationConverterWidget)
    # setupUi

    def retranslateUi(self, AnnotationConverterWidget):
        AnnotationConverterWidget.setWindowTitle(QCoreApplication.translate("AnnotationConverterWidget", u"\u6807\u6ce8\u8f6c\u6362\u5668", None))
        self.label.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u76ee\u6807\u6587\u4ef6\u5939", None))
        self.browseFolderPushButton.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u6d4f\u89c8", None))
        self.newPushButton.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u65b0\u5efa", None))
        self.mergePushButton.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u5408\u5e76", None))
        self.overwritePushButton.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u8986\u5199", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.batchConvertTab), QCoreApplication.translate("AnnotationConverterWidget", u"\u6279\u91cf\u8f6c\u6362", None))
        self.label_2.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u76ee\u6807\u6587\u4ef6", None))
        self.browseFilePushButton.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u6d4f\u89c8", None))
        self.convertFilePushButton.setText(QCoreApplication.translate("AnnotationConverterWidget", u"\u8f6c\u6362", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.singleConvertTab), QCoreApplication.translate("AnnotationConverterWidget", u"\u5355\u6587\u4ef6\u8f6c\u6362", None))
    # retranslateUi

