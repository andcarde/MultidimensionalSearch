import os
import sys
import tempfile

import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsScene, QMainWindow, QTableWidgetItem, QWidget, QVBoxLayout, QLabel

import ParetoLib.GUI as RootGUI
from ParetoLib.GUI.Window import Ui_MainWindow
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import SearchND_2, EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet


class StandardSolutionWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        self.setObjectName("Solution")
        layout = QVBoxLayout()
        self.setLayout(layout)

    def set_message(self, result):
        # type: (_, bool) -> None
        # Message
        label = QLabel(str(result))
        self.layout().addWidget(label)

    def set_resultset(self, rs, var_names):
        # type: (_, ResultSet, list) -> None
        # Create the canvas
        dpi = 100
        width = self.width() / dpi
        height = self.height() / dpi
        sc = MplCanvas(self, width=width, height=height, dpi=dpi)
        # Do not create axis because rs.plot_XD will adjust them to 2D/3D

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar2QT(sc, self)
        self.layout().addWidget(toolbar)
        self.layout().addWidget(sc)

        if rs.xspace.dim() == 2:
            rs.plot_2D_light(var_names=var_names, fig1=sc.figure)
        elif rs.xspace.dim() == 3:
            rs.plot_3D_light(var_names=var_names, fig1=sc.figure)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.axes = None
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(fig)

    def set_axis(self):
        self.axes = self.figure.add_subplot(111)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Conectamos los eventos con sus acciones
        self.f_especificacion_button.clicked.connect(self.especificacion)
        self.f_senial_entrada_button.clicked.connect(self.senial_entrada)
        self.f_variables_button.clicked.connect(self.variables)
        self.f_ejecutar_button.clicked.connect(self.run_stle)
        # Initialize empty Oracle
        self.oracle = OracleSTLeLib()
        # Solution
        self.solution = None

    def especificacion(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', '../../Tests/Oracle/OracleSTLe', '(*.stl)')
        self.f_especificacion_textbox.setPlainText(fname[0])
        with open(self.f_especificacion_textbox.toPlainText()) as file:
            lines = file.readlines()
        self.formula.setPlainText(''.join(lines))

    def senial_entrada(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', '../../Tests/Oracle/OracleSTLe', '(*.csv)')
        self.f_senial_entrada_textbox.setPlainText(fname[0])
        self.plot_csv()

    def variables(self):
        fname = QFileDialog.getOpenFileName(self, 'Select a file', '../../Tests/Oracle/OracleSTLe', '(*.param)')
        self.f_variables_textbox.setPlainText(fname[0])
        self.load_parameters(fname[0])

    def plot_csv(self):
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        dpi = 100
        width = self.graphicsView.width() / dpi
        height = self.graphicsView.height() / dpi
        sc = MplCanvas(self, width=width, height=height, dpi=dpi)
        sc.set_axis()
        # Read csvfile from self.label_3
        # csvfile = '../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv'
        csvfile = self.f_senial_entrada_textbox.toPlainText()
        # Read CSV file
        names = ['Time', 'Signal']
        df_signal = pd.read_csv(csvfile, names=names)

        # Plot the responses for different events and regions
        sns.set_theme(style='darkgrid')
        fig = sns.lineplot(x='Time',
                           y='Signal',
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
        stl_param = tempfile.NamedTemporaryFile(delete=False)
        stl_param_file = stl_param.name
        stl_param.close()

        # Initialize the OracleSTLeLib
        self.oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)

        # Evaluate the STLe expression
        stl_formula = self.oracle._load_stl_formula(stl_prop_file)
        satisfied = self.oracle.eval_stl_formula(stl_formula)
        RootGUI.logger.debug('Satisfied? {0}'.format(satisfied))

        os.remove(stl_param_file)
        return satisfied

    def run_parametric_stle(self):

        # Running STLEval without parameters
        stl_prop_file = self.f_especificacion_textbox.toPlainText()
        csv_signal_file = self.f_senial_entrada_textbox.toPlainText()
        stl_param_file = self.f_variables_textbox.toPlainText()

        # Initialize the OracleSTLeLib
        RootGUI.logger.debug('Evaluating...')
        RootGUI.logger.debug(stl_prop_file)
        RootGUI.logger.debug(csv_signal_file)
        RootGUI.logger.debug(stl_param_file)

        self.oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)

        # Read parameter intervals
        intervals = self.read_parameters_intervals()
        RootGUI.logger.debug('Intervals:')
        RootGUI.logger.debug(intervals)

        # Mining the STLe expression
        assert len(intervals) >= 2, 'Warning! Invalid number of dimensions. Returning empty ResultSet.'
        rs = SearchND_2(ora=self.oracle,
                        list_intervals=intervals,
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

    def run_stle(self):
        # Running STLEval
        index = self.operacion_comboBox.currentIndex()
        is_parametric = (index == 1)
        if not is_parametric:
            # Not parametric
            satisfied = self.run_non_parametric_stle()
            # Visualization
            self.solution = StandardSolutionWindow()
            self.solution.set_message(satisfied)
        else:
            # Parametric
            rs = self.run_parametric_stle()
            # Visualization
            self.solution = StandardSolutionWindow()
            self.solution.set_resultset(rs, self.oracle.get_var_names())

        self.solution.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # []
    window = MainWindow()
    window.show()
    window.centralwidget.adjustSize()
    sys.exit(app.exec_())
