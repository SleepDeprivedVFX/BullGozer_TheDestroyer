# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\sleep\OneDrive\Documents\Scripts\Python\Utilities\BullGozer_TheDestroyer\BullGozer_TheDestroyer\ui\bullgozer_ui.ui'
#
# Created: Sun May 13 14:56:45 2018
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1738, 930)
        Form.setStyleSheet("background-color: rgb(100, 100, 100);\n"
"color: rgb(230, 230, 230);")
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(Form)
        self.label.setStyleSheet("font: 75 22pt \"BankGothic\";")
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.output_log = QtGui.QPlainTextEdit(Form)
        self.output_log.setObjectName("output_log")
        self.verticalLayout.addWidget(self.output_log)
        self.destroyer_file = QtGui.QLineEdit(Form)
        self.destroyer_file.setStyleSheet("border:none;")
        self.destroyer_file.setObjectName("destroyer_file")
        self.verticalLayout.addWidget(self.destroyer_file)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.grand_total = QtGui.QLineEdit(Form)
        self.grand_total.setMaximumSize(QtCore.QSize(100, 16777215))
        self.grand_total.setStyleSheet("border:none;")
        self.grand_total.setObjectName("grand_total")
        self.horizontalLayout.addWidget(self.grand_total)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.seek_btn = QtGui.QPushButton(Form)
        self.seek_btn.setObjectName("seek_btn")
        self.horizontalLayout.addWidget(self.seek_btn)
        self.load_btn = QtGui.QPushButton(Form)
        self.load_btn.setObjectName("load_btn")
        self.horizontalLayout.addWidget(self.load_btn)
        self.destroy_btn = QtGui.QPushButton(Form)
        self.destroy_btn.setObjectName("destroy_btn")
        self.horizontalLayout.addWidget(self.destroy_btn)
        self.oh_shit_btn = QtGui.QPushButton(Form)
        self.oh_shit_btn.setObjectName("oh_shit_btn")
        self.horizontalLayout.addWidget(self.oh_shit_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Bull Gozer", None))
        self.label.setText(QtGui.QApplication.translate("Form", "Bull Gozer - The Destroyer of Files", None))
        self.label_2.setText(QtGui.QApplication.translate("Form", "Destroyable Files Found:", None))
        self.seek_btn.setText(QtGui.QApplication.translate("Form", "Seek", None))
        self.load_btn.setText(QtGui.QApplication.translate("Form", "Load the Destroyer", None))
        self.destroy_btn.setText(QtGui.QApplication.translate("Form", "Destroy", None))
        self.oh_shit_btn.setText(QtGui.QApplication.translate("Form", "Oh Shit!", None))

