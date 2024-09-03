import os
import json
from json.decoder import JSONDecodeError

import pandas as pd
import seaborn as sns
import matplotlib
from PyQt5.QtCore import QEvent

from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

import ParetoLib.GUI
from ParetoLib.GUI.controller_interface import ControllerInterface
from ParetoLib.GUI.mpl_canvas import MplCanvas
from ParetoLib.GUI.Window import Ui_MainWindow
from ParetoLib.GUI.window_interface import WindowInterface
from ParetoLib.CommandLanguage.FileUtils import read_file

RootGUI = ParetoLib.GUI

matplotlib.use('Qt5Agg')
pd.set_option('display.float_format', lambda x: '%.7f' % x)  # For rounding purposes


class MainWindow(WindowInterface, Ui_MainWindow):
    """
    Main window of the Pareto Lib.
    """

    PROJECT_DIRECTORY_PATH = './Projects'

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

        self.mining_comboBox.activated.connect(self._set_unsaved)
        self.param_stl_selection_comboBox.activated.connect(self._set_unsaved)
        self.search_type_comboBox.activated.connect(self._set_unsaved)
        self.opt_level_comboBox.activated.connect(self._set_unsaved)
        self.interpolation_comboBox.activated.connect(self._set_unsaved)
        self.param_tableWidget.cellChanged.connect(self._set_unsaved)

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
        self.project_path = None
        # :: bool
        self.saved_changes = False
        # :: bool
        self.is_parallel = False
        # :: Integer
        self.opt_level = 0
        self.data = None

        # :: Controller : The container of the logic of the business
        # The initialization is deferred due to mutual reference resolution
        self.controller = None

    def set_controller(self, controller: ControllerInterface):
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
                self.controller.check_run(stle2_program, self.signal_filepath)

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
        self._set_unsaved()

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
        Returns:
            int
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

        Returns:
            None
        """
        while layout.count() > 0:
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _set_unsaved(self):
        """
        Returns: None
        """
        self.saved_changes = False

    def closeEvent(self, event: QEvent):
        """
        Handles the window close event to prompt the user to save unsaved changes.

        Parameters:
            event :: QEvent

        Returns:
            None
        """
        if self.project_path is not None and not self.saved_changes:
            try:
                # :: str
                title = 'Unsaved Changes'
                # :: str
                message = 'Do you want to save the changes you made to the project?'
                # :: QMessageBox : Display a message box to the user
                reply = QMessageBox.question(self, title, message,
                                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if reply == QMessageBox.Yes:
                    self._save_project()
                    event.accept()
                elif reply == QMessageBox.No:
                    event.accept()
                else:
                    event.ignore()
            except (IOError, OSError) as file_error:
                RootGUI.logger.debug(f"File operation error: {file_error}")
                QMessageBox.critical(self, "Error", "An error occurred while saving the project.")
                event.accept()
            except RuntimeError as runtime_error:
                RootGUI.logger.debug(f"Runtime error: {runtime_error}")
                QMessageBox.critical(self, "Error", "A runtime error occurred.")
                event.accept()
            except Exception as general_error:
                RootGUI.logger.debug(f"Unexpected error: {general_error}")
                QMessageBox.critical(self, "Error", "An unexpected error occurred.")
                event.accept()

    def _save_project(self):
        """
        Save all the configuration data in the project file.

        Returns:
            None
        """
        # If the project file does not exist, create a new project
        if not self.project_filepath:
            self._create_project()
        try:
            # :: dict[str, object] : Create the JSON object to store all the necessary data
            self.data = dict()
            self.data["project_path"] = self.project_path
            # :: dict[str, object]
            options = dict()
            options["interpolation"] = self.interpolation_comboBox.currentText()
            options["mining_method"] = self.mining_comboBox.currentText()
            options["type_search"] = self.search_type_comboBox.currentText()
            options["option_level"] = self.opt_level_comboBox.currentText()
            self.data["options"] = options
            self.data["stl_specification"] = self.get_program()
            self.data["signal_specification"] = self.signal_filepath
            self.data["parameters"] = self.read_parameters_intervals()

            # Write data to file
            with open(self.project_path, 'w') as saved_file:
                # Raise TypeError at fail
                saved_file.write(json.dumps(self.data, indent=2))

            # Set the 'saved_changes' flag to True
            self.saved_changes = True
        except (OSError, TypeError):
            QMessageBox.about(self, "File not exist", "There is no current file loaded or created")

    def _create_project(self):
        """
        Prompts the user to specify a location and filename to create a new project.
        Initializes a new project file and sets the `has_been_saved` flag to False.

        Returns:
            None
        """
        # Ensure the directory for the project exists, or create it if necessary
        if not MainWindow._check_directory():
            QMessageBox.critical(self, 'Directory Error', f'An error occurred while creating the directory of projects')
            return False
        else:
            # project_file_path :: str
            # Prompt the user to select a location and filename for the new project
            project_filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Create New Project",
                "./Projects",
                "JSON Files (*.json)"
            )

            # Check if the user canceled the dialog
            if not project_filepath:
                return False
            else:
                try:
                    with open(project_filepath, 'w') as file:
                        # Initially, the file is empty
                        pass
                except OSError:
                    # Handle errors during file operations
                    QMessageBox.critical(self, 'File Error', f'An error occurred while creating the project file')
                    return False

                # Update the project path
                self.project_filepath = project_filepath
                self.saved_changes = False
                return True

    def _load_project(self):
        """
        # Raise JSONDecodeError or TypeError at fail
        Returns: None
        """
        # Open the project file that we want to load and store in a variable
        self.project_path = QFileDialog.getOpenFileName(self, "Open project", "./Projects", "(*.json)")

        # Open the file with option read
        self.project_path = ''.join(self.project_path[0])
        load_path = open(self.project_path, 'r')

        data = json.load(load_path)

        self._load_data(data)
        self.saved_changes = True

    def _load_data(self, data):
        """
        Parameters:
            data: dict

        Returns:
            None
        """
        # :: str
        program = data["program"]
        if program:
            self.set_program(program)

        # :: str
        signal_filepath = data["signal_specification"]
        if signal_filepath:
            self._set_signal_filepath(signal_filepath)

        # :: dict
        options = data["options"]
        if options:
            interpolation = options["interpolation"]
            if interpolation:
                self.interpolation_comboBox.setCurrentText(options["interpolation"])

            mining_method = options["mining_method"]
            if mining_method:
                self.mining_comboBox.setCurrentText(mining_method)
            type_search = options["type_search"]
            if type_search:
                self.search_type_comboBox.setCurrentText(type_search)
            option_level = options["option_level"]
            if option_level:
                self.opt_level_comboBox.setCurrentText(option_level)

        self.saved_changes = True

    @staticmethod
    def _check_directory():
        """
        Ensure the directory for storing projects exists. Create it if it doesn't,
        and handle cases where the path exists but is not a directory.

        Returns:
            bool: True if the directory check and creation were successful, False otherwise.
        """
        try:
            # Check if the project directory exists
            if not os.path.exists(MainWindow.PROJECT_DIRECTORY_PATH):
                # Create the directory
                os.mkdir(MainWindow.PROJECT_DIRECTORY_PATH)
            # If path exists but is not a directory; remove and recreate it
            elif not os.path.isdir(MainWindow.PROJECT_DIRECTORY_PATH):
                os.remove(MainWindow.PROJECT_DIRECTORY_PATH)
                os.mkdir(MainWindow.PROJECT_DIRECTORY_PATH)
            return True
        except (OSError, IOError) as e:
            # Handle exceptions related to file and directory operations
            print(f"Error: {e}")
            return False

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
            self._set_unsaved()
            self.signal_filepath_textbox.setPlainText(signal_filepath)
            self._plot_csv(signal_filepath)
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
        canvas = MplCanvas()
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
