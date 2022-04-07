from qtpy import QtWidgets
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tempfile

from ParetoLib.GUI.Window import Ui_MainWindow
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Conectamos los eventos con sus acciones
        self.f_senial_entrada_button.clicked.connect(self.plot_signal)

    def plot_signal(self):
        # Reading csvfile from self.label_3
        # csvfile = "../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv"
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

    def run_stle(self):
        # Running STLEval without parameters
        stl_prop_file = self.f_especificacion_textbox.toPlainText()
        csv_signal_file = self.f_senial_entrada_textbox.toPlainText()
        # No parameters (i.e., using empty temporary file)
        stl_param = tempfile.NamedTemporaryFile(mode='r')
        stl_param_file = stl_param.name

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
