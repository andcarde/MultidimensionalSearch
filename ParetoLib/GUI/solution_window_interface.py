"""
<solution_window_interface.py>
"""

from abc import ABC, abstractmethod

from PyQt5.QtWidgets import QWidget

from ParetoLib.Search.ResultSet import ResultSet


class SolutionWindowInterface(type(ABC), type(QWidget)):
    """
    Solution Window Interface with all methods.

    Methods:
        # Called by ApplicationService
        show_solution(satisfied: bool, bool_signal: dict)
        show_no_result_set_solution()
        show_multi_oracle_solution(result_set: ResultSet)
        show_single_oracle_solution(result_set: ResultSet, var_names: list)
    """

    @staticmethod
    @abstractmethod
    def show_solution(satisfied: bool, bool_signal: dict):
        """
        Show the solution using the StandardSolutionWindow

        Parameters:
            satisfied :: bool
            bool_signal :: dict[c_double, c_double]

        Returns: None
        """
        pass

    @staticmethod
    @abstractmethod
    def show_no_result_set_solution():
        """
        Show the solution when there is no result.

        Returns: None
        """
        pass

    @staticmethod
    @abstractmethod
    def show_multi_oracle_solution(result_set: ResultSet, parameters: list):
        """
        Show the solution when multiple oracles are present.

        Parameters:
            result_set :: ResultSet
            parameters :: List[str]

        Returns: None
        """
        pass

    @staticmethod
    @abstractmethod
    def show_single_oracle_solution(result_set: ResultSet, var_names: list):
        """
        Show the solution when there is only one oracle.

        Parameters:
            result_set :: ResultSet
            var_names :: List[str]

        Returns: None
        """
        pass
