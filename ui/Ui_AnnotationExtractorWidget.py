# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_AnnotationExtractorWidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_AnnotationExtractorWidget(object):
    def setupUi(self, AnnotationExtractorWidget):
        if not AnnotationExtractorWidget.objectName():
            AnnotationExtractorWidget.setObjectName(u"AnnotationExtractorWidget")
        AnnotationExtractorWidget.setWindowModality(Qt.WindowModal)
        AnnotationExtractorWidget.resize(800, 600)
        self.verticalLayout = QVBoxLayout(AnnotationExtractorWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tableWidget = QTableWidget(AnnotationExtractorWidget)
        self.tableWidget.setObjectName(u"tableWidget")

        self.verticalLayout.addWidget(self.tableWidget)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.openPushButton = QPushButton(AnnotationExtractorWidget)
        self.openPushButton.setObjectName(u"openPushButton")

        self.horizontalLayout.addWidget(self.openPushButton)

        self.extractPushButton = QPushButton(AnnotationExtractorWidget)
        self.extractPushButton.setObjectName(u"extractPushButton")

        self.horizontalLayout.addWidget(self.extractPushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.label = QLabel(AnnotationExtractorWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.numSelectedSpinBox = QSpinBox(AnnotationExtractorWidget)
        self.numSelectedSpinBox.setObjectName(u"numSelectedSpinBox")
        self.numSelectedSpinBox.setAlignment(Qt.AlignCenter)
        self.numSelectedSpinBox.setReadOnly(True)
        self.numSelectedSpinBox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.numSelectedSpinBox.setMaximum(999999)

        self.horizontalLayout.addWidget(self.numSelectedSpinBox)

        self.totalImageLabel = QLabel(AnnotationExtractorWidget)
        self.totalImageLabel.setObjectName(u"totalImageLabel")

        self.horizontalLayout.addWidget(self.totalImageLabel)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(AnnotationExtractorWidget)

        QMetaObject.connectSlotsByName(AnnotationExtractorWidget)
    # setupUi

    def retranslateUi(self, AnnotationExtractorWidget):
        AnnotationExtractorWidget.setWindowTitle(QCoreApplication.translate("AnnotationExtractorWidget", u"\u6807\u6ce8\u4fe1\u606f\u63d0\u53d6\u5668", None))
        self.openPushButton.setText(QCoreApplication.translate("AnnotationExtractorWidget", u"\u5bfc\u5165\u6807\u6ce8", None))
        self.extractPushButton.setText(QCoreApplication.translate("AnnotationExtractorWidget", u"\u63d0\u53d6\u6807\u6ce8", None))
        self.label.setText(QCoreApplication.translate("AnnotationExtractorWidget", u"\u5df2\u9009:", None))
        self.totalImageLabel.setText(QCoreApplication.translate("AnnotationExtractorWidget", u"/ 0 (\u51710)", None))
    # retranslateUi

