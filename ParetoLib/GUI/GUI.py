import os
import sys
import json
from json.decoder import JSONDecodeError

import pandas as pd
import seaborn as sns
import matplotlib

from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox

import ParetoLib.GUI
from ParetoLib.GUI.mpl_canvas import MplCanvas
from ParetoLib.GUI.Window import Ui_MainWindow
from ParetoLib.GUI.application_service import ApplicationService
from ParetoLib.GUI.controller import Controller
from ParetoLib.GUI.window_interface import WindowInterface
from ParetoLib.CommandLanguage.FileUtils import read_file

RootGUI = ParetoLib.GUI

matplotlib.use('Qt5Agg')
pd.set_option('display.float_format', lambda x: '%.7f' % x)  # For rounding purposes


class MainWindow(QMainWindow, Ui_MainWindow, WindowInterface):
    """
    Main window of the Pareto Lib.
    """

    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        # Connecting events and actions

        self.open_program_file_button.clicked.connect(self._read_program_filepath)
        self.open_signal_file_button.clicked.connect(self.read_signal_filepath)
        self.new_project_button.setShortcut("Ctrl+N")
        self.new_project_button.triggered.connect(self._create_project)
        self.save_project_button.setShortcut("Ctrl+S")
        self.save_project_button.triggered.connect(self._save_project)
        self.load_project_button.setShortcut("Ctrl+O")
        self.load_project_button.triggered.connect(self._load_project)
        self.pareto_execution_button.setEnabled(False)
        # Connecting execution button clicked (event) running stle (action)
        self.pareto_execution_button.clicked.connect(self._run_stle)

        self.mining_comboBox.activated.connect(self._not_saved)
        self.param_stl_selection_comboBox.activated.connect(self._not_saved)
        self.search_type_comboBox.activated.connect(self._not_saved)
        self.opt_level_comboBox.activated.connect(self._not_saved)
        self.interpolation_comboBox.activated.connect(self._not_saved)
        self.param_tableWidget.cellChanged.connect(self._not_saved)

        # Filepaths
        # :: str
        self.program_filepath = None
        # :: str
        self.signal_filepath = None

        # :: StandardSolutionWindow
        self.solution_window = None
        # Store the relative path where the projects will be saved in a variable
        # This path is created with the 'PYTHONPATH' variable set to the directory 'multidimensional_search'.
        # If your variable points to a different directory, you may update it accordingly.
        # self.path_project = os.path.abspath('multidimensional_search/Projects')
        # :: str
        self.path_project = "./Projects"
        # :: str
        self.project_path = None
        # :: bool
        self.has_been_saved = False
        # :: bool
        self.is_parallel = False
        # :: Integer
        self.opt_level = 0
        self.data = None

        # :: Controller : The container of the logic of the business
        # The initialization is deferred due to mutual reference resolution
        self.controller = None

    def set_controller(self, controller: Controller):
        """
        Parameters:
        controller : Controller

        Returns: None
        """
        self.controller = controller
        self.pareto_execution_button.setEnabled(True)

    def _run_stle(self):
        """
        Returns: None
        """
        if self.controller is None:
            raise Exception('The controller has not been assigned so it is not possible to run stle')
        else:
            if self.signal_filepath is None:
                self.show_message('Missing signal', 'The signal has not been set.', True)
            else:
                stle2_program = self.get_program()
                self.controller.check_run(self, stle2_program, self.signal_filepath)

    def show_message(self, title: str, body: str, is_error: bool):
        if is_error:
            QMessageBox.critical(self, title, body)

    """
    def _is_parametric(self):
        ""
        @deprecated
        Returns: bool : If the formula is parametric or not
        ""
        # :: Integer : Index of the combobox of parameters. Possible values: 0: Not parametric, 1: Parametric
        index = self.param_stl_selection_comboBox.currentIndex()
        # :: Bool : The formula is parametric when the combobox of parameters is in position 1
        is_parametric = (index == 1)
        return is_parametric
    """

    def get_program(self):
        """
        Returns:
            program :: str
        """
        # :: str
        program = self.program_textarea.toPlainText()
        return program

    def set_program(self, program: str):
        """
        Set the STLe2 program

        Parameters:
            program :: str

        Returns: None
        """
        self.program_textarea.setPlainText(program)

    def get_method(self):
        """
        Returns: int
        """
        # :: int
        method = self.mining_comboBox.currentIndex()
        return method

    def generate_is_parallel(self):
        """
        Returns: bool
        """
        # :: bool
        self.is_parallel = (self.search_type_comboBox.currentIndex() == 0)
        return self.is_parallel

    def generate_opt_level(self):
        """
        Returns: int
        """
        # :: int
        self.opt_level = self.opt_level_comboBox.currentIndex()
        return self.opt_level

    def get_signal_filepath(self):
        """
        Gives the filepath of the signal.

        Returns:
            signal_filepath :: str
        """
        return self.signal_filepath

    @staticmethod
    def _clear_layout(layout):
        """
        Parameters:
        layout :: QVBoxLayout

        Returns: None
        """
        while layout.count() > 0:
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _not_saved(self):
        """
        Returns: None
        """
        self.has_been_saved = False

    def closeEvent(self, event):
        """
        Parameters:
        event :: ?

        Returns: None
        """
        try:
            if self.project_path is not None and not self.has_been_saved:
                title = "Close Project?"
                message = "WARNING \n\nDo you want to save the changes you made to " + self.project_path + "?"
                reply = QMessageBox.question(self, title, message,
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

                if reply == QMessageBox.Yes:
                    self._save_project()
                    event.accept()
                elif reply == QMessageBox.No:
                    # Check if the file is empty, if it is we delete the file, otherwise we leave it as it is
                    # project_filename = ''.join(self.project_path)
                    # :: bool
                    is_non_zero_file = os.path.isfile(self.project_path) and os.path.getsize(self.project_path) > 0
                    if is_non_zero_file:
                        os.remove(self.project_path)
                    event.accept()
                else:
                    event.ignore()
        except Exception as e:
            RootGUI.logger.debug(str(e))
            event.accept()

    def _save_project(self):
        # Check if the directory exists and if is a dir, else create the dir
        self._check_directory()

        # Create the new project configuration in dir ./Projects
        # self.create_project()

        # Save all the necessary configuration data of a project in the specified file
        self._save_data()
        self.has_been_saved = True

    def _create_project(self):
        """
        Returns: None
        """
        self.has_been_saved = False

        # Check if the directory exists and if is a dir, else create the dir
        self._check_directory()

        # Open the folder where we are going to save the project
        self.project_path = QFileDialog.getSaveFileName(self, "Create project", "./Projects", ".json")
        # Create the JSON file where we are going to save the configuration options
        self.project_path = ''.join(self.project_path)
        saved_file = open(self.project_path, 'w')

        saved_file.close()

    def _save_data(self):
        """
        Returns: None
        """
        # :: str
        name_project = f'"name_project":"{self.project_path}"'
        # :: str
        name_project_json = "{" + name_project + "}"
        try:
            # :: dict[str, object] : Create the JSON object to store all the necessary data
            # Raise JSONDecodeError or TypeError at fail
            self.data = json.loads(name_project_json)
            # :: dict[str, object]
            # Raise JSONDecodeError or TypeError at fail
            options = json.loads('{}')
            options["interpolation"] = self.interpolation_comboBox.currentText()
            options["mining_method"] = self.mining_comboBox.currentText()
            options["type_search"] = self.search_type_comboBox.currentText()
            options["option_level"] = self.opt_level_comboBox.currentText()
            options["parametric"] = self.param_stl_selection_comboBox.currentText()
            self.data["options"] = options
            self.data["stl_specification"] = self.program_filepath
            self.data["signal_specification"] = self.signal_filepath
            self.data["parameters"] = self.read_parameters_intervals()

            # Raise OSError at fail
            saved_file = open(self.project_path, 'w')
            # Raise TypeError at fail
            saved_file.write(json.dumps(self.data, indent=2))
            saved_file.close()
        except (JSONDecodeError, TypeError):
            QMessageBox.about(self, "File not exist", "There is no current file loaded or created")

    def _load_project(self):
        """
        Returns: None
        """
        # Open the project file that we want to load and store in a variable
        self.project_path = QFileDialog.getOpenFileName(self, "Open project", "./Projects", "(*.json)")

        # Open the file with option read
        self.project_path = ''.join(self.project_path[0])
        load_path = open(self.project_path, 'r')

        data = json.load(load_path)

        self._load_data(data)
        self.has_been_saved = True

    def _load_data(self, data):
        """
        data: ?

        Returns: None
        """
        # :: str
        self.program_filepath = data["stl_specification"]
        if self.program_filepath:
            self._set_program_filepath(self.program_filepath)

        # :: str
        signal_filepath = data["signal_specification"]
        if signal_filepath:
            self._set_signal_filepath(signal_filepath)

        options = data["options"]

        self.interpolation_comboBox.setCurrentText(options["interpolation"])
        self.mining_comboBox.setCurrentText(options["mining_method"])
        self.search_type_comboBox.setCurrentText(options["type_search"])
        self.opt_level_comboBox.setCurrentText(options["option_level"])
        self.param_stl_selection_comboBox.setCurrentText(options["parametric"])

    def _check_directory(self):
        """
        Check if the directory where we are going to store the projects exists

        Returns: None
        """
        if not os.path.exists(self.path_project):
            os.mkdir(self.path_project)
        # If is not a directory
        elif not os.path.isdir(self.path_project):
            os.remove(self.path_project)
            os.mkdir(self.path_project)

    def _read_program_filepath(self):
        """
        Returns: None
        """
        # :: str
        program_filepath, _ = QFileDialog.getOpenFileName(self, 'Select a file', '../../Tests/Oracle/OracleSTLe',
                                                          '(*.stl)')
        # :: str
        program = read_file(program_filepath)
        self.set_program(program)

    def read_signal_filepath(self):
        """
        Returns: None
        """
        # :: List[str]
        signal_filepath, _ = QFileDialog.getOpenFileName(self, 'Select a file', '../../Tests/Oracle/OracleSTLe',
                                                         '(*.csv)')
        self._set_signal_filepath(signal_filepath)

    def _set_signal_filepath(self, signal_filepath: str):
        """
        Parameters:
            signal_filepath :: str
        Returns: None
        """
        try:
            self.signal_filepath = signal_filepath
            self.signal_filepath_textbox.setPlainText(signal_filepath)
            self._plot_csv(signal_filepath)
            self._not_saved()
        except Exception as e:
            RootGUI.logger.debug(e)

    """
    def set_param_filepath(self):
        ""
        @deprecated
        
        Returns: None
        ""
        try:
            self.param_filepath_textbox.setPlainText(self.param_filepath)
            self.load_parameters(self.param_filepath)
            self._not_saved()
        except Exception as e:
            RootGUI.logger.debug(e)
    """

    def _plot_csv(self, signal_filepath: str):
        """
        Parameters:
            signal_filepath: str

        Returns:
            None
        """
        # Create the 'maptlotlib' FigureCanvas object,
        # which defines a single set of axes as self.axes.
        canvas = MplCanvas(parent=self)
        canvas.set_axis()
        try:
            # signal_filepath = '../../Tests/Oracle/OracleSTLe/2D/stabilization/stabilization.csv'

            # Read CSV file
            names = ['Time', 'Signal']
            # dtypes = [int, float]
            # df_signal = pd.read_csv(csvfile, sep=',', names=names, dtypes=dtypes)
            df_signal = pd.read_csv(signal_filepath, sep=',', names=names)

            # Plot the responses for different events and regions
            sns.set_theme(style='darkgrid')
            ax = sns.lineplot(x='Time',
                              y='Signal',
                              data=df_signal,
                              ax=canvas.axes)
            ax.set(xlabel=None)
            ax.set(ylabel=None)
            canvas.figure.tight_layout(pad=0)

            MainWindow._clear_layout(self.signal_layout)
            self.signal_layout.addWidget(canvas)
            self.show()
        except Exception as e:
            RootGUI.logger.debug(e)

    """
    def load_parameters(self, stl_param_file):
        ""
        @deprecated
        Loads the parameters in the table.
        
        Parameters:
        stl_param_file : str

        Returns: None
        ""
        self.param_tableWidget.clearContents()
        try:
            # List[str]
            parameters = self.oracle_container.get_parameters2(stl_param_file)
            self.param_tableWidget.setRowCount(len(parameters))
            for row, parameter in enumerate(parameters):
                self.param_tableWidget.setItem(row, 0, QTableWidgetItem(parameter))
        except Exception as e:
            RootGUI.logger.debug(e)
    """

    """
    def read_parameters_intervals(self):
        ""
        @deprecated
        Read the parameters from the table in the Graphic User Interface

        Returns: List[Tuple = (float, float)]
        ""
        # :: List[Tuple = (float, float)] : Example: [(0.0, 0.0), (1.0, 2.0)]. There are as many intervals as parameters
        intervals = []
        num_parameters = self.param_tableWidget.rowCount()
        for row in range(num_parameters):
            min_val_text = self.param_tableWidget.item(row, 1)
            max_val_text = self.param_tableWidget.item(row, 2)
            interval = (float(min_val_text.text()), float(max_val_text.text()))
            intervals.append(interval)
        return intervals
    """


def main():
    # :: QApplication
    app = QApplication(sys.argv)
    # :: MainWindow
    window = MainWindow()
    window.centralwidget.adjustSize()
    window.show()
    # :: ApplicationService
    application_service = ApplicationService(window)
    Controller(application_service, window)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
