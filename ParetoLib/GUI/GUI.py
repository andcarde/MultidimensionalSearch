import os
import sys
import tempfile

import pandas as pd
import seaborn as sns
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT

from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTableWidgetItem, QWidget, QVBoxLayout, QLabel

import ParetoLib.GUI as RootGUI
from ParetoLib.GUI.Window import Ui_MainWindow
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Oracle.OracleEpsSTLe import OracleEpsSTLe
from ParetoLib.Search.Search import SearchND_2, SearchIntersectionND_2, SearchND_2_BMNN22, EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet

matplotlib.use('Qt5Agg')

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
        # dpi = 100
        # width = self.width() / dpi
        # height = self.height() / dpi
        # canvas = MplCanvas(parent=self, width=width, height=height, dpi=dpi)
        canvas = MplCanvas(parent=self)
        # Do not create axis because rs.plot_XD will adjust them to 2D/3D

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar2QT(canvas, self)
        self.layout().addWidget(toolbar)
        self.layout().addWidget(canvas)

        if rs.xspace.dim() == 2:
            rs.plot_2D_light(var_names=var_names, fig1=canvas.figure)
        elif rs.xspace.dim() == 3:
            rs.plot_3D_light(var_names=var_names, fig1=canvas.figure)

    def set_bool_signal(self, bool_signal):
        # type: (_, dict) -> None
        x = bool_signal.keys()
        y = bool_signal.values()
        canvas = MplCanvas(parent=self)
        canvas.set_axis()
        canvas.axes.step(x, y, where='post')  # where='pre'
        canvas.figure.tight_layout(pad=0)
        self.layout().addWidget(canvas)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # type: (_, _, int, int, int) -> None
        self.axes = None
        fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(fig)

    def set_axis(self):
        # type: (_) -> None
        self.axes = self.figure.add_subplot(111)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Connecting events and actions
        self.open_spec_file_button.clicked.connect(self.read_spec_filepath)
        self.open_signal_file_button.clicked.connect(self.read_signal_filepath)
        self.open_param_file_button.clicked.connect(self.read_param_filepath)
        self.pareto_execution_button.clicked.connect(self.run_stle)
        # Initialize empty Oracles:
        # - BBMJ19: requires 1 Oracle
        # - BDMJ20: requires 2 Oracles
        self.oracle = OracleSTLeLib()
        self.oracle_2 = OracleSTLeLib()
        self.oracles = []
        # Filepaths
        self.spec_filepaths = []
        self.signal_filepaths = []
        self.param_filepath = None
        # Solution
        self.solution = None

    def clearLayout(self, layout):
        # type: (_, QVBoxLayout) -> None
        while layout.count() > 0:
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def read_spec_filepath(self):
        # type: (_) -> None
        self.spec_filepaths, _ = QFileDialog.getOpenFileNames(self, 'Select a file', '../../Tests/Oracle/OracleSTLe',
                                                              '(*.stl)')
        # TODO: Show each spec file in fnames in a separated tab
        try:
            self.spec_filepath_textbox.setPlainText("\n".join(fname for fname in self.spec_filepaths))
            with open(self.spec_filepath_textbox.toPlainText()) as file:
                lines = file.readlines()
            self.formula_textEdit.setPlainText(''.join(lines))
        except Exception as e:
            RootGUI.logger.debug(e)

    def read_signal_filepath(self):
        # type: (_) -> None
        self.signal_filepaths, _ = QFileDialog.getOpenFileNames(self, 'Select a file', '../../Tests/Oracle/OracleSTLe',
                                                                '(*.csv)')
        # TODO: Show each component of a single csv file in a separated tab
        try:
            self.signal_filepath_textbox.setPlainText("\n".join(fname for fname in self.signal_filepaths))
            self.plot_csv()
        except Exception as e:
            RootGUI.logger.debug(e)

    def read_param_filepath(self):
        # type: (_) -> None
        self.param_filepath, _ = QFileDialog.getOpenFileName(self, 'Select a file', '../../Tests/Oracle/OracleSTLe',
                                                             '(*.param)')
        try:
            self.param_filepath_textbox.setPlainText(self.param_filepath)
            self.load_parameters(self.param_filepath)
        except Exception as e:
            RootGUI.logger.debug(e)

    def plot_csv(self):
        # type: (_) -> None
        # Create the maptlotlib FigureCanvas object,
        # which defines a single set of axes as self.axes.
        canvas = MplCanvas(parent=self)
        canvas.set_axis()
        try:
            # Read csvfile from self.label_3
            # csvfile = '../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv'
            csvfile = self.signal_filepath_textbox.toPlainText()

            # Read CSV file
            names = ['Time', 'Signal']
            df_signal = pd.read_csv(csvfile, names=names)

            # Plot the responses for different events and regions
            # sns.set_theme(style='darkgrid')
            ax = sns.lineplot(x='Time',
                              y='Signal',
                              data=df_signal,
                              ax=canvas.axes)
            ax.set(xlabel=None)
            ax.set(ylabel=None)
            canvas.figure.tight_layout(pad=0)

            self.clearLayout(self.signal_layout)
            # self.signal_layout.layout().addWidget(canvas)
            self.signal_layout.addWidget(canvas)
            self.show()
        except Exception as e:
            RootGUI.logger.debug(e)

    def load_parameters(self, stl_param_file):
        # type: (_, str) -> None
        self.param_tableWidget.clearContents()
        try:
            params = self.oracle._get_parameters_stl(stl_param_file)
            num_params = len(params)
            self.param_tableWidget.setRowCount(num_params)
            for row, param in enumerate(params):
                self.param_tableWidget.setItem(row, 0, QTableWidgetItem(param))
        except Exception as e:
            RootGUI.logger.debug(e)

    def read_parameters_intervals(self):
        # type: (_) -> list
        # intervals = [(0.0, 0.0)] * num_params
        intervals = []
        num_params = self.param_tableWidget.rowCount()
        self.param_tableWidget.setRowCount(num_params)
        for row in range(num_params):
            min_val_text = self.param_tableWidget.item(row, 1)
            max_val_text = self.param_tableWidget.item(row, 2)
            interval = (float(min_val_text.text()), float(max_val_text.text()))
            intervals.append(interval)
        return intervals

    def run_non_parametric_stle(self):
        # type: (_) -> (bool, dict)
        # Running STLEval without parameters
        stl_prop_file = self.spec_filepath_textbox.toPlainText()
        csv_signal_file = self.signal_filepath_textbox.toPlainText()
        satisfied, bool_signal = False, dict()
        try:
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

            # Generate Boolean signal
            stl_formula = self.oracle._load_stl_formula(stl_prop_file)
            bool_signal = self.oracle.get_stle_pcseries(stl_formula)

            os.remove(stl_param_file)
        except Exception as e:
            RootGUI.logger.debug(e)
        finally:
            return satisfied, bool_signal

    def run_parametric_stle(self):
        # type: (_) -> ResultSet
        # Running STLEval without parameters
        stl_prop_file = self.spec_filepaths[0]
        csv_signal_file = self.signal_filepaths[0]
        stl_param_file = self.param_filepath

        rs = None
        f = lambda x : True if(x == 0) else False
        method = self.mining_comboBox.currentIndex()
        self.parallel = f(self.search_type_comboBox.currentIndex())
        self.opt_level = self.opt_level_comboBox.currentIndex()

        try:
            # Initialize the OracleSTLeLib
            RootGUI.logger.debug('Evaluating...')
            RootGUI.logger.debug(stl_prop_file)
            RootGUI.logger.debug(csv_signal_file)
            RootGUI.logger.debug(stl_param_file)

            # Read parameter intervals
            intervals = self.read_parameters_intervals()
            RootGUI.logger.debug('Intervals:')
            RootGUI.logger.debug(intervals)
            assert len(intervals) >= 2, 'Warning! Invalid number of dimensions. Returning empty ResultSet.'

            # Mining the STLe expression
            if method == 0:
                RootGUI.logger.debug('Method 0...')
                self.oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)
                rs = SearchND_2(ora=self.oracle,
                                list_intervals=intervals,
                                epsilon=EPS,
                                delta=DELTA,
                                max_step=STEPS,
                                blocking=False,
                                sleep=0.0,
                                opt_level=self.opt_level,
                                parallel=self.parallel,
                                logging=False,
                                simplify=False)
            elif method == 1:
                # TODO: Popup window for reading the parameters "bound_on_count" and "intvl_epsilon"
                #  for Oracle1 and Oracle2

                RootGUI.logger.debug('Method 1...')
                stl_prop_file = self.spec_filepaths[0]
                stl_prop_file_2 = self.spec_filepaths[1]
                self.oracle = OracleEpsSTLe(bound_on_count=0, intvl_epsilon=10, stl_prop_file=stl_prop_file,
                                            csv_signal_file=csv_signal_file, stl_param_file=stl_param_file)
                self.oracle_2 = OracleEpsSTLe(bound_on_count=0, intvl_epsilon=10, stl_prop_file=stl_prop_file_2,
                                              csv_signal_file=csv_signal_file, stl_param_file=stl_param_file)
                rs = SearchIntersectionND_2(self.oracle, self.oracle_2,
                                            intervals,
                                            list_constraints=[],
                                            epsilon=EPS,
                                            delta=DELTA,
                                            max_step=STEPS,
                                            blocking=False,
                                            sleep=0.0,
                                            opt_level=0,
                                            parallel=False,
                                            logging=False,
                                            simplify=False)
            elif method == 2:
                # TODO: Use SearchND_2_BMNN22 rather than Search_BMNN22
                self.oracles = [OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file) for csv_signal_file in self.signal_filepaths]
                # self.oracle.from_file(stl_prop_file, human_readable=True)
                # self.oracle.from_file(stl_prop_file_2, human_readable=True)
                rs = SearchND_2_BMNN22(ora_list=self.oracles,
                                   intervals=intervals,
                                   blocking=False,
                                   num_cells=4,
                                   sleep=0.0,
                                   opt_level=self.opt_level,
                                   parallel=self.parallel,
                                   logging=False,
                                   simplify=False)

        except Exception as e:
            RootGUI.logger.debug(e)
        finally:
            return rs

    def run_stle(self):
        # type: (_) -> None
        # Running STLEval
        index = self.param_stl_selection_comboBox.currentIndex()
        is_parametric = (index == 1)
        if not is_parametric:
            # Not parametric
            satisfied, bool_signal = self.run_non_parametric_stle()
            # Visualization
            self.solution = StandardSolutionWindow()
            self.solution.set_bool_signal(bool_signal)
            self.solution.set_message(satisfied)
        else:
            # Parametric
            rs = self.run_parametric_stle()
            # Visualization
            self.solution = StandardSolutionWindow()
            if rs is not None:
                if self.oracles is not None: # For an oracle list
                    param_list = list()
                    for ora in self.oracles:
                        param_list = param_list + ora.get_var_names()
                    self.solution.set_resultset(rs, param_list)
                else: # For a single oracle
                    self.solution.set_resultset(rs, self.oracle.get_var_names())

        self.solution.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)  # []
    window = MainWindow()
    window.show()
    window.centralwidget.adjustSize()
    sys.exit(app.exec_())
