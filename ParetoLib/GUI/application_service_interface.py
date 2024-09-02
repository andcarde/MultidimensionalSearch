"""
<application_service_interface.py>
"""

from abc import ABC, abstractmethod


class ApplicationServiceInterface(ABC):
    """
    Application Service Interface with all methods.

    Methods:
        run_stle(self, is_parametric : bool, stle1_filepath : str, signal_filepath : str, parameter_filepath)
    """

    """
    Methods called by the Controller.
    """

    @abstractmethod
    def run_stle(self, is_parametric: bool, stle1_filepath: str, signal_filepath: str, parameter_filepath: str):
        """
        Executes the STLe with 'program_file_path'

        Parameters:
            is_parametric :: bool
            stle1_filepath :: str : STLe1 program
            signal_filepath :: str
            parameter_filepath : str


        Returns: None
        """
        pass

    """
    Methods called by the MainWindow.
    """