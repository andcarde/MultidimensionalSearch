import sys
import tempfile

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from qtpy import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QTableWidgetItem

from Window import Ui_MainWindow
# from PareboLib.GUI.Window import Ui_MainWindow
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import Search2D, Search3D, SearchND_2, EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet

# TODO: Replace print's by logger
# TODO: Replace "from Window" by "ParetoLib.GUI"

# TODO: Include more options in the GUI for reading the configuration parameters
#  of PareboLib (e.g., EPS, DELTA, STEPS,...)
# TODO: Extend STLe with more interporlation options
# TODO: Implement a natural language processor that allows to write STL specifications in a nicer way
# TODO: Reimplementen the core of ParetoLib for speeding up the computations

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
        # Initialize empty Oracle
        self.oracle = OracleSTLeLib()

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
        self.load_parameters(fname[0])

    def plot_csv(self):
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        dpi = 100
        width = self.graphicsView.width() / dpi
        height = self.graphicsView.height() / dpi
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
        # fig.set_xlabel(None)
        # fig.set_ylabel(None)
        fig.set(xlabel=None)
        fig.set(ylabel=None)

        scene = QGraphicsScene()
        scene.addWidget(sc)
        self.graphicsView.setScene(scene)
        self.show()

    def load_parameters(self, stl_param_file):
        params = self.oracle._get_parameters_stl(stl_param_file)
        self.tableWidget.clearContents()

        num_params = len(params)
        self.tableWidget.setRowCount(num_params)
        for row, param in enumerate(params):
            self.tableWidget.setItem(row, 0, QTableWidgetItem(param))

    def read_parameters_intervals(self):
        # intervals = [(0.0, 0.0)] * num_params
        intervals = []
        num_params = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(num_params)
        for row in range(num_params):
            min_val_text = self.tableWidget.item(row, 1)
            max_val_text = self.tableWidget.item(row, 2)
            interval = (int(min_val_text.text()), int(max_val_text.text()))
            intervals.append(interval)

        return intervals

    def run_non_parametric_stle(self):
        # Running STLEval without parameters
        stl_prop_file = self.f_especificacion_textbox.toPlainText()
        csv_signal_file = self.f_senial_entrada_textbox.toPlainText()
        # No parameters (i.e., using empty temporary file)
        stl_param = tempfile.NamedTemporaryFile(mode='r')
        stl_param_file = stl_param.name

        # Initialize the OracleSTLeLib
        self.oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)

        # Evaluate the STLe expression
        stl_formula = self.oracle._load_stl_formula(stl_prop_file)
        satisfied = self.oracle.eval_stl_formula(stl_formula)
        return satisfied

    def run_parametric_stle(self):

        def mining_2D(oracle, intervals):
            # type: (OracleSTLeLib, list) -> ResultSet

            # Definition of the n-dimensional space
            min_x, max_x = intervals[0]
            min_y, max_y = intervals[1]

            # Mining the STLe expression
            rs = Search2D(ora=oracle,
                          min_cornerx=min_x,
                          min_cornery=min_y,
                          max_cornerx=max_x,
                          max_cornery=max_y,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0,
                          opt_level=0,
                          parallel=False,
                          logging=False,
                          simplify=False)
            return rs

        def mining_3D(oracle, intervals):
            # type: (OracleSTLeLib, list) -> ResultSet

            # Definition of the n-dimensional space
            min_x, max_x = intervals[0]
            min_y, max_y = intervals[1]
            min_z, max_z = intervals[2]

            # Mining the STLe expression
            rs = Search3D(ora=oracle,
                          min_cornerx=min_x,
                          min_cornery=min_y,
                          min_cornerz=min_z,
                          max_cornerx=max_x,
                          max_cornery=max_y,
                          max_cornerz=max_z,
                          epsilon=EPS,
                          delta=DELTA,
                          max_step=STEPS,
                          blocking=False,
                          sleep=0,
                          opt_level=0,
                          parallel=False,
                          logging=True,
                          simplify=True)
            return rs

        def mining_ND(oracle, intervals):
            # type: (OracleSTLeLib, list) -> ResultSet

            # Definition of the n-dimensional space
            min_x, max_x = intervals[0]
            min_y, max_y = intervals[1]
            min_z, max_z = intervals[2]

            # Mining the STLe expression
            rs = SearchND_2(ora=oracle,
                            list_intervals=intervals,
                            epsilon=EPS,
                            delta=DELTA,
                            max_step=STEPS,
                            blocking=False,
                            sleep=0,
                            opt_level=0,
                            parallel=False,
                            logging=True,
                            simplify=True)
            return rs

        # Running STLEval without parameters
        stl_prop_file = self.f_especificacion_textbox.toPlainText()
        csv_signal_file = self.f_senial_entrada_textbox.toPlainText()
        stl_param_file = self.f_variables_textbox.toPlainText()

        # Initialize the OracleSTLeLib
        print(stl_prop_file)
        print(csv_signal_file)
        print(stl_param_file)

        self.oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)

        # Read parameter intervals
        intervals = self.read_parameters_intervals()
        print(intervals)
        if len(intervals) == 2:
            rs = mining_2D(self.oracle, intervals)
        elif len(intervals) == 3:
            rs = mining_3D(self.oracle, intervals)
        elif len(intervals) > 3:
            rs = mining_ND(self.oracle, intervals)
        else:
            print("Error")
            rs = ResultSet()

        return rs

    def run_stle(self):
        # Running STLEval
        index = self.operacion_comboBox.currentIndex()
        is_parametric = (index == 1)
        if not is_parametric:
            # Not parametric
            satisfied = self.run_non_parametric_stle()
        else:
            # Parametric
            satisfied = self.run_parametric_stle()
        return satisfied


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # []
    window = MainWindow()
    window.show()
    window.centralwidget.adjustSize()
    sys.exit(app.exec_())
