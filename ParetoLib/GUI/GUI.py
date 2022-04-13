import sys

from qtpy import QtWidgets
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

import tempfile
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene

from Window import Ui_MainWindow
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Conectamos los eventos con sus acciones
        self.f_especificacion_button.clicked.connect(self.especificacion)
        self.f_senial_entrada_button.clicked.connect(self.senial_entrada)
        self.f_variables_button.clicked.connect(self.variables)
        self.f_ejecutar_button.clicked.connect(self.run_stle)

    def especificacion(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', "../../Tests/Oracle/OracleSTLe", "(*.stl)")
        self.f_especificacion_textbox.setPlainText(fname[0])
        with open(self.f_especificacion_textbox.toPlainText()) as file:
             lines = file.readlines()
        self.formula.setPlainText(''.join(lines))

    def senial_entrada(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', "../../Tests/Oracle/OracleSTLe", "(*.csv)")
        self.f_senial_entrada_textbox.setPlainText(fname[0])
        self.plot_csv()

    def variables(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', "../../Tests/Oracle/OracleSTLe", "(*.param)")
        self.f_variables_textbox.setPlainText(fname[0])
    
    def plot_csv(self):
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        dpi = 100
        width = self.graphicsView.width()/dpi
        height = self.graphicsView.height()/dpi
        sc = MplCanvas(self, width=width, height=height, dpi=dpi)

        # Read csvfile from self.label_3
        # csvfile = "../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv"
        csvfile = self.f_senial_entrada_textbox.toPlainText()
        # Read CSV file
        names = ["Time", "Signal"]
        df_signal = pd.read_csv(csvfile, names=names)

        # Plot the responses for different events and regions
        sns.set_theme(style="darkgrid")
        fig = sns.lineplot(x="Time",
                           y="Signal",
                           data=df_signal,
                           ax=sc.axes)
        #fig.set_xlabel(None)
        #fig.set_ylabel(None)
        fig.set(xlabel=None)
        fig.set(ylabel=None)

        scene = QGraphicsScene()
        scene.addWidget(sc)
        self.graphicsView.setScene(scene)
        self.show()

    def run_stle(self):
        # Running STLEval without parameters
        stl_prop_file = self.f_especificacion_textbox.toPlainText()
        csv_signal_file = self.f_senial_entrada_textbox.toPlainText()
        # No parameters (i.e., using empty temporary file)
        #stl_param = tempfile.NamedTemporaryFile(mode='r')
        #stl_param_file = stl_param.name
        stl_param_file = self.f_variables_textbox.toPlainText()

        # Initialize the OracleSTLeLib
        oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)

        # Evaluate the STLe expression
        stl_formula = oracle._load_stl_formula(stl_prop_file)
        satisfied = oracle.eval_stl_formula(stl_formula)
        return satisfied


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) # []
    window = MainWindow()
    window.show()
    window.centralwidget.adjustSize()
    sys.exit(app.exec_())
