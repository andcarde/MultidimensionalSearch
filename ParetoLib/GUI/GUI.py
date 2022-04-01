from qtpy import QtWidgets
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from Window import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Conectamos los eventos con sus acciones
        self.f_senial_entrada_button.clicked.connect(self.plot_csv)

    def plot_csv(self):
        # Leer ruta csvfile de self.label_3
        csvfile = "../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv"

        # Read CSV file
        names = ["Time", "Signal"]
        df_signal = pd.read_csv(csvfile, names=names)

        # Plot the responses for different events and regions
        sns.set_theme(style="darkgrid")
        fig = sns.lineplot(x="Time",
                           y="Signal",
                           data=df_signal)
        plt.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
