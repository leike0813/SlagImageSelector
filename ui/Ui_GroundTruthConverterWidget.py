# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ui_GroundTruthConverterWidget.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_GroundTruthConverterWidget(object):
    def setupUi(self, GroundTruthConverterWidget):
        if not GroundTruthConverterWidget.objectName():
            GroundTruthConverterWidget.setObjectName(u"GroundTruthConverterWidget")
        GroundTruthConverterWidget.setWindowModality(Qt.WindowModal)
        GroundTruthConverterWidget.resize(402, 300)
        self.verticalLayout = QVBoxLayout(GroundTruthConverterWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.centralWidget = QWidget(GroundTruthConverterWidget)
        self.centralWidget.setObjectName(u"centralWidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(self.centralWidget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.sourceFileLineEdit = QLineEdit(self.centralWidget)
        self.sourceFileLineEdit.setObjectName(u"sourceFileLineEdit")
        self.sourceFileLineEdit.setReadOnly(True)

        self.horizontalLayout.addWidget(self.sourceFileLineEdit)

        self.browsePushButton = QPushButton(self.centralWidget)
        self.browsePushButton.setObjectName(u"browsePushButton")

        self.horizontalLayout.addWidget(self.browsePushButton)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(9, -1, 9, -1)
        self.categoryLabel = QLabel(self.centralWidget)
        self.categoryLabel.setObjectName(u"categoryLabel")
        self.categoryLabel.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.categoryLabel)

        self.categoryComboBox = QComboBox(self.centralWidget)
        self.categoryComboBox.setObjectName(u"categoryComboBox")
        self.categoryComboBox.setEnabled(False)

        self.horizontalLayout_3.addWidget(self.categoryComboBox)

        self.horizontalLayout_3.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.convertOptionGroupBox = QGroupBox(self.centralWidget)
        self.convertOptionGroupBox.setObjectName(u"convertOptionGroupBox")
        self.convertOptionGroupBox.setEnabled(False)
        self.gridLayout = QGridLayout(self.convertOptionGroupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.convertOptionGroupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.boundarySmoothCoefDoubleSpinBox = QDoubleSpinBox(self.convertOptionGroupBox)
        self.boundarySmoothCoefDoubleSpinBox.setObjectName(u"boundarySmoothCoefDoubleSpinBox")
        self.boundarySmoothCoefDoubleSpinBox.setSingleStep(0.100000000000000)
        self.boundarySmoothCoefDoubleSpinBox.setValue(0.300000000000000)

        self.gridLayout.addWidget(self.boundarySmoothCoefDoubleSpinBox, 1, 3, 1, 1)

        self.boundaryHalfWidthSpinBox = QSpinBox(self.convertOptionGroupBox)
        self.boundaryHalfWidthSpinBox.setObjectName(u"boundaryHalfWidthSpinBox")
        self.boundaryHalfWidthSpinBox.setMinimum(1)
        self.boundaryHalfWidthSpinBox.setMaximum(20)
        self.boundaryHalfWidthSpinBox.setValue(10)

        self.gridLayout.addWidget(self.boundaryHalfWidthSpinBox, 1, 1, 1, 1)

        self.label_3 = QLabel(self.convertOptionGroupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 1, 2, 1, 1)

        self.simpleBoundaryCheckBox = QCheckBox(self.convertOptionGroupBox)
        self.simpleBoundaryCheckBox.setObjectName(u"simpleBoundaryCheckBox")

        self.gridLayout.addWidget(self.simpleBoundaryCheckBox, 2, 0, 1, 1)

        self.smoothBoundaryCheckBox = QCheckBox(self.convertOptionGroupBox)
        self.smoothBoundaryCheckBox.setObjectName(u"smoothBoundaryCheckBox")
        self.smoothBoundaryCheckBox.setChecked(True)

        self.gridLayout.addWidget(self.smoothBoundaryCheckBox, 2, 1, 1, 1)

        self.simpleRegionCheckBox = QCheckBox(self.convertOptionGroupBox)
        self.simpleRegionCheckBox.setObjectName(u"simpleRegionCheckBox")

        self.gridLayout.addWidget(self.simpleRegionCheckBox, 2, 2, 1, 1)

        self.centralizeRegionCheckBox = QCheckBox(self.convertOptionGroupBox)
        self.centralizeRegionCheckBox.setObjectName(u"centralizeRegionCheckBox")
        self.centralizeRegionCheckBox.setChecked(True)

        self.gridLayout.addWidget(self.centralizeRegionCheckBox, 2, 3, 1, 1)

        self.label_4 = QLabel(self.convertOptionGroupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.kernelShapeComboBox = QComboBox(self.convertOptionGroupBox)
        self.kernelShapeComboBox.addItem("")
        self.kernelShapeComboBox.addItem("")
        self.kernelShapeComboBox.addItem("")
        self.kernelShapeComboBox.setObjectName(u"kernelShapeComboBox")

        self.gridLayout.addWidget(self.kernelShapeComboBox, 0, 1, 1, 1)

        self.label_6 = QLabel(self.convertOptionGroupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)

        self.regionProbLowerBoundDoubleSpinBox = QDoubleSpinBox(self.convertOptionGroupBox)
        self.regionProbLowerBoundDoubleSpinBox.setObjectName(u"regionProbLowerBoundDoubleSpinBox")
        self.regionProbLowerBoundDoubleSpinBox.setMaximum(1.000000000000000)
        self.regionProbLowerBoundDoubleSpinBox.setSingleStep(0.050000000000000)
        self.regionProbLowerBoundDoubleSpinBox.setValue(0.550000000000000)

        self.gridLayout.addWidget(self.regionProbLowerBoundDoubleSpinBox, 0, 3, 1, 1)


        self.verticalLayout_2.addWidget(self.convertOptionGroupBox)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.convertPushButton = QPushButton(self.centralWidget)
        self.convertPushButton.setObjectName(u"convertPushButton")
        self.convertPushButton.setEnabled(False)

        self.horizontalLayout_2.addWidget(self.convertPushButton)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(2, 4)

        self.verticalLayout.addWidget(self.centralWidget)


        self.retranslateUi(GroundTruthConverterWidget)

        QMetaObject.connectSlotsByName(GroundTruthConverterWidget)
    # setupUi

    def retranslateUi(self, GroundTruthConverterWidget):
        GroundTruthConverterWidget.setWindowTitle(QCoreApplication.translate("GroundTruthConverterWidget", u"\u771f\u503c\u8f6c\u6362\u5668", None))
        self.label.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u76ee\u6807\u6587\u4ef6", None))
        self.browsePushButton.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u6d4f\u89c8", None))
        self.categoryLabel.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u8f6c\u6362\u7c7b\u522b", None))
        self.convertOptionGroupBox.setTitle(QCoreApplication.translate("GroundTruthConverterWidget", u"\u8f6c\u6362\u9009\u9879", None))
        self.label_2.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u8fb9\u754c\u6269\u5c55\u534a\u5bbd\n"
"(1\u4ee3\u8868\u4e0d\u6269\u5c55)", None))
        self.label_3.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u8fb9\u754c\u5e73\u6ed1\u7cfb\u6570\n"
"(0\u4ee3\u8868\u4e0d\u5e73\u6ed1)", None))
        self.simpleBoundaryCheckBox.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u666e\u901a\u8fb9\u754c", None))
        self.smoothBoundaryCheckBox.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u5e73\u6ed1\u6269\u5c55\u8fb9\u754c", None))
        self.simpleRegionCheckBox.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u666e\u901a\u533a\u57df", None))
        self.centralizeRegionCheckBox.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u4e2d\u5fc3\u5e73\u6ed1\u533a\u57df", None))
        self.label_4.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u5185\u6838\u5f62\u72b6", None))
        self.kernelShapeComboBox.setItemText(0, QCoreApplication.translate("GroundTruthConverterWidget", u"\u5706\u5f62", None))
        self.kernelShapeComboBox.setItemText(1, QCoreApplication.translate("GroundTruthConverterWidget", u"\u65b9\u5f62", None))
        self.kernelShapeComboBox.setItemText(2, QCoreApplication.translate("GroundTruthConverterWidget", u"\u5341\u5b57\u5f62", None))

        self.label_6.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u533a\u57df\u6982\u7387\u4e0b\u754c", None))
        self.convertPushButton.setText(QCoreApplication.translate("GroundTruthConverterWidget", u"\u8f6c\u6362", None))
    # retranslateUi

