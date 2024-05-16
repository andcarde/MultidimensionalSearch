# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Window.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1102, 917)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(1000, 710))
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.main_groupbox = QtWidgets.QGroupBox(self.centralwidget)
        self.main_groupbox.setMaximumSize(QtCore.QSize(1000, 710))
        self.main_groupbox.setTitle("")
        self.main_groupbox.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.main_groupbox.setObjectName("main_groupbox")
        self.left_groupBox = QtWidgets.QGroupBox(self.main_groupbox)
        self.left_groupBox.setGeometry(QtCore.QRect(0, 0, 351, 711))
        self.left_groupBox.setMaximumSize(QtCore.QSize(500, 16777215))
        self.left_groupBox.setTitle("")
        self.left_groupBox.setObjectName("left_groupBox")
        self.input_files_groupBox = QtWidgets.QGroupBox(self.left_groupBox)
        self.input_files_groupBox.setGeometry(QtCore.QRect(0, 0, 351, 311))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.input_files_groupBox.sizePolicy().hasHeightForWidth())
        self.input_files_groupBox.setSizePolicy(sizePolicy)
        self.input_files_groupBox.setMaximumSize(QtCore.QSize(400, 480))
        self.input_files_groupBox.setObjectName("input_files_groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.input_files_groupBox)
        self.formLayout.setObjectName("formLayout")
        self.open_signal_file_button = QtWidgets.QPushButton(self.input_files_groupBox)
        self.open_signal_file_button.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.open_signal_file_button.setObjectName("open_signal_file_button")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.open_signal_file_button)
        self.signal_filepath_textbox = QtWidgets.QPlainTextEdit(self.input_files_groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signal_filepath_textbox.sizePolicy().hasHeightForWidth())
        self.signal_filepath_textbox.setSizePolicy(sizePolicy)
        self.signal_filepath_textbox.setAcceptDrops(True)
        self.signal_filepath_textbox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.signal_filepath_textbox.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
        self.signal_filepath_textbox.setReadOnly(True)
        self.signal_filepath_textbox.setPlainText("")
        self.signal_filepath_textbox.setBackgroundVisible(False)
        self.signal_filepath_textbox.setObjectName("signal_filepath_textbox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.signal_filepath_textbox)
        self.options_groupbox = QtWidgets.QGroupBox(self.left_groupBox)
        self.options_groupbox.setGeometry(QtCore.QRect(0, 420, 351, 221))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.options_groupbox.sizePolicy().hasHeightForWidth())
        self.options_groupbox.setSizePolicy(sizePolicy)
        self.options_groupbox.setMaximumSize(QtCore.QSize(500, 16777215))
        self.options_groupbox.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.options_groupbox.setObjectName("options_groupbox")
        self.gridLayout = QtWidgets.QGridLayout(self.options_groupbox)
        self.gridLayout.setObjectName("gridLayout")
        self.opt_level_comboBox = QtWidgets.QComboBox(self.options_groupbox)
        self.opt_level_comboBox.setObjectName("opt_level_comboBox")
        self.opt_level_comboBox.addItem("")
        self.opt_level_comboBox.addItem("")
        self.gridLayout.addWidget(self.opt_level_comboBox, 7, 0, 1, 1)
        self.param_stl_selection_label = QtWidgets.QLabel(self.options_groupbox)
        self.param_stl_selection_label.setObjectName("param_stl_selection_label")
        self.gridLayout.addWidget(self.param_stl_selection_label, 3, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.mining_label = QtWidgets.QLabel(self.options_groupbox)
        self.mining_label.setObjectName("mining_label")
        self.gridLayout.addWidget(self.mining_label, 0, 1, 1, 1)
        self.interpolation_label = QtWidgets.QLabel(self.options_groupbox)
        self.interpolation_label.setObjectName("interpolation_label")
        self.gridLayout.addWidget(self.interpolation_label, 0, 0, 1, 1)
        self.mining_label_2 = QtWidgets.QLabel(self.options_groupbox)
        self.mining_label_2.setObjectName("mining_label_2")
        self.gridLayout.addWidget(self.mining_label_2, 6, 0, 1, 1)
        self.param_stl_selection_comboBox = QtWidgets.QComboBox(self.options_groupbox)
        self.param_stl_selection_comboBox.setObjectName("param_stl_selection_comboBox")
        self.param_stl_selection_comboBox.addItem("")
        self.param_stl_selection_comboBox.addItem("")
        self.gridLayout.addWidget(self.param_stl_selection_comboBox, 5, 0, 1, 1)
        self.interpolation_comboBox = QtWidgets.QComboBox(self.options_groupbox)
        self.interpolation_comboBox.setObjectName("interpolation_comboBox")
        self.interpolation_comboBox.addItem("")
        self.interpolation_comboBox.addItem("")
        self.gridLayout.addWidget(self.interpolation_comboBox, 1, 0, 1, 1, QtCore.Qt.AlignLeft)
        self.type_search_label = QtWidgets.QLabel(self.options_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.type_search_label.sizePolicy().hasHeightForWidth())
        self.type_search_label.setSizePolicy(sizePolicy)
        self.type_search_label.setObjectName("type_search_label")
        self.gridLayout.addWidget(self.type_search_label, 3, 1, 1, 1)
        self.search_type_comboBox = QtWidgets.QComboBox(self.options_groupbox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.search_type_comboBox.sizePolicy().hasHeightForWidth())
        self.search_type_comboBox.setSizePolicy(sizePolicy)
        self.search_type_comboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.search_type_comboBox.setIconSize(QtCore.QSize(16, 16))
        self.search_type_comboBox.setObjectName("search_type_comboBox")
        self.search_type_comboBox.addItem("")
        self.search_type_comboBox.addItem("")
        self.gridLayout.addWidget(self.search_type_comboBox, 4, 1, 2, 1)
        self.mining_comboBox = QtWidgets.QComboBox(self.options_groupbox)
        self.mining_comboBox.setObjectName("mining_comboBox")
        self.mining_comboBox.addItem("")
        self.mining_comboBox.addItem("")
        self.mining_comboBox.addItem("")
        self.gridLayout.addWidget(self.mining_comboBox, 1, 1, 1, 1)
        self.right_groupbox = QtWidgets.QGroupBox(self.main_groupbox)
        self.right_groupbox.setGeometry(QtCore.QRect(350, 0, 641, 711))
        self.right_groupbox.setTitle("")
        self.right_groupbox.setObjectName("right_groupbox")
        self.signal_groupbox = QtWidgets.QGroupBox(self.right_groupbox)
        self.signal_groupbox.setGeometry(QtCore.QRect(0, 0, 651, 371))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.signal_groupbox.sizePolicy().hasHeightForWidth())
        self.signal_groupbox.setSizePolicy(sizePolicy)
        self.signal_groupbox.setSizeIncrement(QtCore.QSize(1, 1))
        self.signal_groupbox.setObjectName("signal_groupbox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.signal_groupbox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.signal_layout = QtWidgets.QVBoxLayout()
        self.signal_layout.setObjectName("signal_layout")
        self.verticalLayout.addLayout(self.signal_layout)
        self.checkrun_button = QtWidgets.QPushButton(self.right_groupbox)
        self.checkrun_button.setGeometry(QtCore.QRect(510, 660, 121, 33))
        self.checkrun_button.setObjectName("checkrun_button")
        self.save_button = QtWidgets.QPushButton(self.right_groupbox)
        self.save_button.setGeometry(QtCore.QRect(30, 660, 97, 33))
        self.save_button.setObjectName("save_button")
        self.textarea = QtWidgets.QPlainTextEdit(self.right_groupbox)
        self.textarea.setGeometry(QtCore.QRect(10, 420, 621, 231))
        self.textarea.setObjectName("textarea")
        self.check_button = QtWidgets.QPushButton(self.right_groupbox)
        self.check_button.setGeometry(QtCore.QRect(400, 660, 97, 33))
        self.check_button.setObjectName("check_button")
        self.stle2_label = QtWidgets.QLabel(self.right_groupbox)
        self.stle2_label.setGeometry(QtCore.QRect(240, 400, 181, 17))
        self.stle2_label.setObjectName("stle2_label")
        self.load_button = QtWidgets.QPushButton(self.right_groupbox)
        self.load_button.setGeometry(QtCore.QRect(140, 660, 97, 33))
        self.load_button.setObjectName("load_button")
        self.signal_groupbox.raise_()
        self.textarea.raise_()
        self.save_button.raise_()
        self.checkrun_button.raise_()
        self.check_button.raise_()
        self.stle2_label.raise_()
        self.load_button.raise_()
        self.horizontalLayout.addWidget(self.main_groupbox)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1102, 29))
        self.menubar.setObjectName("menubar")
        self.menuCreate = QtWidgets.QMenu(self.menubar)
        self.menuCreate.setObjectName("menuCreate")
        self.menuOpen = QtWidgets.QMenu(self.menubar)
        self.menuOpen.setObjectName("menuOpen")
        self.menuSave_project = QtWidgets.QMenu(self.menubar)
        self.menuSave_project.setObjectName("menuSave_project")
        self.menuClassification = QtWidgets.QMenu(self.menubar)
        self.menuClassification.setObjectName("menuClassification")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.new_project_button = QtWidgets.QAction(MainWindow)
        self.new_project_button.setObjectName("new_project_button")
        self.load_project_button = QtWidgets.QAction(MainWindow)
        self.load_project_button.setObjectName("load_project_button")
        self.save_project_button = QtWidgets.QAction(MainWindow)
        self.save_project_button.setObjectName("save_project_button")
        self.save_as_button = QtWidgets.QAction(MainWindow)
        self.save_as_button.setObjectName("save_as_button")
        self.actionIdentify_champion = QtWidgets.QAction(MainWindow)
        self.actionIdentify_champion.setObjectName("actionIdentify_champion")
        self.menuCreate.addAction(self.new_project_button)
        self.menuOpen.addAction(self.load_project_button)
        self.menuSave_project.addAction(self.save_project_button)
        self.menuClassification.addAction(self.actionIdentify_champion)
        self.menubar.addAction(self.menuCreate.menuAction())
        self.menubar.addAction(self.menuOpen.menuAction())
        self.menubar.addAction(self.menuSave_project.menuAction())
        self.menubar.addAction(self.menuClassification.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ParetoLib"))
        self.input_files_groupBox.setTitle(_translate("MainWindow", "Input signal"))
        self.open_signal_file_button.setText(_translate("MainWindow", "Open"))
        self.options_groupbox.setTitle(_translate("MainWindow", "Options"))
        self.opt_level_comboBox.setItemText(0, _translate("MainWindow", "0 - Fixed size cells"))
        self.opt_level_comboBox.setItemText(1, _translate("MainWindow", "1 - Adaptative cells"))
        self.param_stl_selection_label.setText(_translate("MainWindow", "Parametric STL"))
        self.mining_label.setText(_translate("MainWindow", "Mining method"))
        self.interpolation_label.setText(_translate("MainWindow", "Interpolation"))
        self.mining_label_2.setText(_translate("MainWindow", "Opt level"))
        self.param_stl_selection_comboBox.setItemText(0, _translate("MainWindow", "No"))
        self.param_stl_selection_comboBox.setItemText(1, _translate("MainWindow", "Yes"))
        self.interpolation_comboBox.setItemText(0, _translate("MainWindow", "Constant"))
        self.interpolation_comboBox.setItemText(1, _translate("MainWindow", "Linear"))
        self.type_search_label.setText(_translate("MainWindow", "Type Search"))
        self.search_type_comboBox.setItemText(0, _translate("MainWindow", "Parallel"))
        self.search_type_comboBox.setItemText(1, _translate("MainWindow", "Sequential"))
        self.mining_comboBox.setCurrentText(_translate("MainWindow", "BBMJ19"))
        self.mining_comboBox.setItemText(0, _translate("MainWindow", "BBMJ19"))
        self.mining_comboBox.setItemText(1, _translate("MainWindow", "BDMJ20"))
        self.mining_comboBox.setItemText(2, _translate("MainWindow", "BMNN22"))
        self.signal_groupbox.setTitle(_translate("MainWindow", "Signal"))
        self.checkrun_button.setText(_translate("MainWindow", "Check and Run"))
        self.save_button.setText(_translate("MainWindow", "Save"))
        self.check_button.setText(_translate("MainWindow", "Check"))
        self.stle2_label.setText(_translate("MainWindow", "Command Languaje STLE2"))
        self.load_button.setText(_translate("MainWindow", "Load"))
        self.menuCreate.setTitle(_translate("MainWindow", "Create"))
        self.menuOpen.setTitle(_translate("MainWindow", "Open"))
        self.menuSave_project.setTitle(_translate("MainWindow", "Save project"))
        self.menuClassification.setTitle(_translate("MainWindow", "Classification"))
        self.new_project_button.setText(_translate("MainWindow", "New project"))
        self.load_project_button.setText(_translate("MainWindow", "Load project"))
        self.save_project_button.setText(_translate("MainWindow", "Save"))
        self.save_as_button.setText(_translate("MainWindow", "Save as..."))
        self.actionIdentify_champion.setText(_translate("MainWindow", "Identify champion"))
