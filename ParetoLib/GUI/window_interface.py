"""
<window_interface.py>
"""

from abc import ABC, abstractmethod

from ParetoLib.GUI.application_service_interface import ApplicationServiceInterface
from ParetoLib.Search.ResultSet import ResultSet


class WindowInterface(ABC):
    """
    Main Window Interface with all methods.

    Methods:
        get_program()
        show_message(title : str, body : str)
        get_textarea()
        set_textarea(content: str)
        set_param_filepath(parameters_file_path : str)

        set_application_service(application_service: ApplicationServiceInterface)
        show_solution(satisfied: bool, bool_signal: dict)
        show_no_result_set_solution()
        show_multi_oracle_solution(result_set : ResultSet)
        show_single_oracle_solution(result_set : list, var_names : list)
        get_method()
        generate_is_parallel()
        generate_opt_level()
        read_parameters_intervals()
        get_specification_filepath(index: int)
        get_signal_filepaths()
    """

    """
    Methods called by the Controller.
    """

    @abstractmethod
    def get_program(self):
        """
        Gives the STLe2 program in plain text.

        Returns:
            stle2_program :: str
        """
        pass

    @abstractmethod
    def show_message(self, title: str, body: str):
        """
        Show the message with 'title' and 'body'.

        Parameters_
            title :: str
            body :: str
        Returns: None
        """
        pass

    @abstractmethod
    def get_textarea(self):
        """
        Gives the content of the textarea.

        Returns: str
        """
        pass

    @abstractmethod
    def set_textarea(self, content: str):
        """
        Puts the content of the textarea.

        Parameters:
            content :: str

        Returns: None
        """
        pass

    @abstractmethod
    def set_param_filepath(self, parameters_file_path: str):
        """
        Save the variable 'parameters_file_path'

        Parameters:
            parameters_file_path :: str

        Returns: None
        """

    """
    Methods called by the ApplicationService
    """

    @abstractmethod
    def set_application_service(self, application_service: ApplicationServiceInterface):
        """
        Save the variable 'application_service'

        Parameters:
            application_service :: ApplicationService

        Returns: None
        """
        pass

    @abstractmethod
    def show_solution(self, satisfied: bool, bool_signal: dict):
        """
        Show the solution using the StandardSolutionWindow

        Parameters:
            satisfied :: bool
            bool_signal :: dict[c_double, c_double]

        Returns: None
        """
        pass

    @abstractmethod
    def show_no_result_set_solution(self):
        """
        Show the solution when there is no result.

        Returns: None
        """
        pass

    @abstractmethod
    def show_multi_oracle_solution(self, result_set: ResultSet):
        """
        Show the solution when multiple oracles are present.

        Parameters:
            result_set :: ResultSet

        Returns: None
        """
        pass

    @abstractmethod
    def show_single_oracle_solution(self, result_set: ResultSet, var_names: list):
        """
        Show the solution when there is only one oracle.

        Parameters:
            result_set :: ResultSet
            var_names :: List[str]

        Returns: None
        """
        pass

    @abstractmethod
    def get_method(self):
        """
        Gives the method.

        Returns:
            method :: int
        """
        pass

    @abstractmethod
    def generate_is_parallel(self):
        """
        Generates and gives if is_parallel.

        Returns:
            is_parallel :: bool
        """
        pass

    @abstractmethod
    def generate_opt_level(self):
        """
        Generates and gives the option level.

        Returns:
            opt_level :: int
        """
        pass

    @abstractmethod
    def read_parameters_intervals(self):
        """
        Gives the parameters intervals.

        Returns:
            parameters_intervals :: List[Tuple = (float, float)]
        """
        pass

    @abstractmethod
    def get_specification_filepath(self, index: int):
        """
        Gives the specification filepath with the passed index.

        Parameters:
            index :: int

        Returns:
            specification_filepath :: str
        """
        pass

    @abstractmethod
    def get_signal_filepaths(self):
        """
        Gives the filepaths of the signals.

        Returns:
            signal_filepaths :: List[str]
        """
        pass
