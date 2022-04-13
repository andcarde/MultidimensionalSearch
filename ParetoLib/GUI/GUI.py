from qtpy import QtWidgets
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tempfile
from PyQt5.QtWidgets import QFileDialog, QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtGui import QImage, QPixmap

from Window import Ui_MainWindow
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Conectamos los eventos con sus acciones
        self.f_especificacion_button.clicked.connect(self.especificacion)
        self.f_senial_entrada_button.clicked.connect(self.senial_entrada)
        self.f_variables_button.clicked.connect(self.variables)
        self.f_ejecutar_button.clicked.connect(self.run_stle)

        # Para la imagen
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

    def especificacion(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', "../../Tests/Oracle/OracleSTLe", "(*.stl)")
        self.f_especificacion_textbox.setPlainText(fname[0])
        with open(self.f_especificacion_textbox.toPlainText()) as file:
             lines = file.readlines()
        self.formula.setPlainText(''.join(lines))

    def senial_entrada(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', "../../Tests/Oracle/OracleSTLe", "(*.csv)")
        self.f_senial_entrada_textbox.setPlainText(fname[0])
        #self.plot_signal()
        self.plot_csv()
        self.loadImage()
    
    def variables(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', "../../Tests/Oracle/OracleSTLe", "(*.param)")
        self.f_variables_textbox.setPlainText(fname[0])
        
    def plot_signal(self):
        # Reading csvfile from self.label_3
        #csvfile = "../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv"
        csv_signal_file = self.f_senial_entrada_textbox.toPlainText()

        # Read CSV file
        names = ["Time", "Signal"]
        df_signal = pd.read_csv(csv_signal_file, names=names)

        # Plot the responses for different events and regions
        sns.set_theme(style="darkgrid")
        fig = sns.lineplot(x="Time",
                           y="Signal",
                           data=df_signal)
        plt.show()
    
    ###########
    # Creamos el plot
    def plot_csv(self):
        # Leer ruta csvfile de self.label_3
        #csvfile = "../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv"
        csvfile = self.f_senial_entrada_textbox.toPlainText()
        # Read CSV file
        names = ["Time", "Signal"]
        df_signal = pd.read_csv(csvfile, names=names)

        # Plot the responses for different events and regions
        sns.set_theme(style="darkgrid")
        fig = sns.lineplot(x="Time",
                           y="Signal",
                           data=df_signal)
        #plt.show()
        
        plt.savefig('plot.png')

    # Pasamos el plot a imagen
    def loadImage(self):
        # file_name, _ = QFileDialog.getOpenFileName(
        #     self, "Open file", ".", "Image Files (*.png *.jpg *.bmp)"
        # )
        # if not file_name:
        #     return
        
        file_name = "plot.png" 
        self.image_qt = QImage(file_name)

        pic = QGraphicsPixmapItem()
        pic.setPixmap(QPixmap.fromImage(self.image_qt))
        self.scene.setSceneRect(0, 0, 400, 400)
        self.scene.addItem(pic)
    #############

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
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
