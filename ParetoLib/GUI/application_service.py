# ApplicationService.py

import tempfile
import os

import ParetoLib.GUI
from ParetoLib.GUI.application_service_interface import ApplicationServiceInterface
from ParetoLib.GUI.oracle_container import OracleContainer
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Oracle.OracleEpsSTLe import OracleEpsSTLe
from ParetoLib.Search.Search import SearchND_2, SearchIntersectionND_2, SearchND_2_BMNN22, EPS, DELTA, STEPS
from ParetoLib.CommandLanguage.FileUtils import read_file
from ParetoLib.GUI.solution_window import StandardSolutionWindow

RootGUI = ParetoLib.GUI


class InvalidFormatError(Exception):
    """Exception raised for errors in the input format."""
    def __init__(self, message="Invalid format in parameters file"):
        self.message = message
        super().__init__(self.message)


class ApplicationService(ApplicationServiceInterface):

    def __init__(self, main_window):
        """
        main_window :: MainWindow
        """
        # :: OracleContainer
        self.oracle_container = OracleContainer()
        self.main_window = main_window
        self.main_window.set_application_service(self)

    def _get_parameters(self):
        # :: List[str]
        parameters = self.oracle_container.get_parameters()
        return parameters

    def get_parameters2(self, stl_param_file):
        # :: List[str]
        parameters = self.oracle_container.get_parameters2(stl_param_file)
        return parameters

    def run_stle(self, is_parametric, stl_prop_file, csv_signal_file, stl_param_file):
        """
        Runs STLEval

        Parameters:
        stl_prop_file :: str
        csv_signal_file :: str
        stl_param_file :: str

        Returns: None
        """
        if not is_parametric:
            # satisfied :: bool, bool_signal :: dict[c_double, c_double]
            satisfied, bool_signal = self._run_non_parametric_stle(stl_prop_file, csv_signal_file)
            # Visualization of the solution
            StandardSolutionWindow.show_solution(satisfied, bool_signal)
        # Parametric
        else:
            # :: ResultSet
            result_set = self._run_parametric_stle(stl_prop_file, csv_signal_file, stl_param_file)
            if result_set is None:
                # Visualization of the solution
                StandardSolutionWindow.show_no_result_set_solution()
            # For an oracle list
            elif self.oracle_container.exist_oracles():
                # Visualization of the solution
                # :: List[str]
                parameters = self._get_parameters()
                StandardSolutionWindow.show_multi_oracle_solution(self, result_set, parameters)
            # For a single oracle
            else:
                # Visualization of the solution
                # :: List[str]
                var_names = self.oracle_container.get_oracle().get_var_names()
                StandardSolutionWindow.show_single_oracle_solution(result_set, var_names)

    def _run_non_parametric_stle(self, property_file_name, signal_file_name):
        """
        Runs STLEval without parameters

        Parameters:
        property_file_name :: str
        csv_signal_file :: str

        Returns: Tuple = (bool, dict[c_double, c_double])
        """

        # :: Bool
        is_satisfied = False
        # :: Dictionary[Double, Double]
        bool_signal = dict()
        try:
            # :: _TemporaryFileWrapper : Since there are no parameters, an empty temporary file is used
            parameters_file = tempfile.NamedTemporaryFile(delete=False)
            parameters_file.close()
            # :: str
            parameters_file_name = parameters_file.name

            # :: OracleSTLeLib : Initialize the OracleSTLeLib
            oracle = OracleSTLeLib(property_file_name, signal_file_name, parameters_file_name)
            self.oracle_container.set_oracle(oracle)
            # :: str : Evaluate the STLe expression
            stl_formula = oracle._load_stl_formula(property_file_name)
            is_satisfied = oracle.eval_stl_formula(stl_formula)
            RootGUI.logger.debug('Satisfied? {0}'.format(is_satisfied))

            # :: str : Generate Boolean signal
            stl_formula = oracle._load_stl_formula(property_file_name)
            # :: dict[c_double, c_double]
            bool_signal = oracle.get_stle_pcseries(stl_formula)

            os.remove(property_file_name)
        except Exception as exception:
            RootGUI.logger.debug(exception)
        finally:
            return is_satisfied, bool_signal

    @staticmethod
    def _read_parameters_intervals(parameters_filepath: str):
        """
        Read the parameters intervals from the file of parameters

        Parameters:
            parameters_filepath :: str

        Returns:
            intervals :: List[Tuple = (float, float)]

        """
        # :: str
        content = read_file(parameters_filepath)
        # :: List[Tuple = (float, float)]
        intervals = []

        for line in content.splitlines():
            parts = line.split()
            # Check that the line has exactly two elements
            if len(parts) != 2:
                raise InvalidFormatError(f"Line '{line}' does not have exactly two values.")
            try:
                # Convert to float
                start, end = map(float, parts)
                intervals.append((start, end))
            except ValueError:
                raise InvalidFormatError(f"Line '{line}' contains non-numeric values.")

        return intervals

    def _run_parametric_stle(self, stl_prop_file, csv_signal_file, stl_param_file):
        """
        Running STLEval without parameters

        Parameters:
        stl_prop_file :: str
        csv_signal_file :: str
        stl_param_file :: str

        Returns: ResultSet
        """

        # :: ResultSet
        result_set = None
        # :: int
        method = self.main_window.get_method()
        # :: bool
        parallel = self.main_window.generate_is_parallel()
        # :: int
        opt_level = self.main_window.generate_opt_level()

        try:
            # Initialize the OracleSTLeLib
            RootGUI.logger.debug('Evaluating...')
            RootGUI.logger.debug(stl_prop_file)
            RootGUI.logger.debug(csv_signal_file)
            RootGUI.logger.debug(stl_param_file)

            # Read parameter intervals --> Save the parameters
            # :: List[Tuple = (float, float)]
            intervals = ApplicationService._read_parameters_intervals(stl_param_file)
            RootGUI.logger.debug('Intervals:')
            RootGUI.logger.debug(intervals)
            assert len(intervals) >= 2, 'Warning! Invalid number of dimensions. Returning empty ResultSet.'

            # Mining the STLe expression
            if method == 0:
                RootGUI.logger.debug('Method 0...')
                oracle = OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)
                self.oracle_container.set_oracle(oracle)
                result_set = SearchND_2(ora=oracle,
                                        list_intervals=intervals,
                                        epsilon=EPS,
                                        delta=DELTA,
                                        max_step=STEPS,
                                        blocking=False,
                                        sleep=0.0,
                                        opt_level=opt_level,
                                        parallel=parallel,
                                        logging=False,
                                        simplify=False)
            elif method == 1:
                RootGUI.logger.debug('Method 1')
                # :: str : File path number 2
                stl_prop_file2 = self.main_window.get_specification_filepath(1)
                oracle = OracleEpsSTLe(bound_on_count=0, intvl_epsilon=10, stl_prop_file=stl_prop_file,
                                       csv_signal_file=csv_signal_file, stl_param_file=stl_param_file)
                self.oracle_container.set_oracle(oracle)
                oracle2 = OracleEpsSTLe(bound_on_count=0, intvl_epsilon=10, stl_prop_file=stl_prop_file2,
                                        csv_signal_file=csv_signal_file, stl_param_file=stl_param_file)
                self.oracle_container.set_oracle2(oracle2)
                result_set = SearchIntersectionND_2(oracle, oracle2,
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
                # :: List[str]
                signal_filepaths = self.main_window.get_signal_filepaths()
                oracles = [OracleSTLeLib(stl_prop_file, csv_signal_file, stl_param_file)
                           for csv_signal_file in signal_filepaths]
                self.oracle_container.set_oracles(oracles)
                RootGUI.logger.debug('Method 2')
                result_set = SearchND_2_BMNN22(ora_list=oracles,
                                               list_intervals=intervals,
                                               blocking=False,
                                               num_cells=25,
                                               sleep=0.0,
                                               opt_level=opt_level,
                                               parallel=parallel,
                                               logging=False,
                                               simplify=False)

        except Exception as e:
            RootGUI.logger.debug(e)
        finally:
            return result_set