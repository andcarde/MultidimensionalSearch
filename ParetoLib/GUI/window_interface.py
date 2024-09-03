"""
<window_interface.py>
"""

from abc import abstractmethod

from PyQt5.QtWidgets import QMainWindow

from ParetoLib.GUI.controller_interface import ControllerInterface


class WindowInterface(QMainWindow):
    """
    Main Window Interface with all methods.
    ABC is not used for multiple inheritance compatibility

    Methods:
        # Called by Controller
        set_controller(controller: ControllerInterface)
        show_message(title : str, body : str, is_error : bool)
        get_program()
        set_program(program: str)

        # Called by ApplicationService
        get_method()
        generate_is_parallel()
        generate_opt_level()
        get_signal_filepath()
    """

    """
    Methods called by the Controller.
    """

    @abstractmethod
    def set_controller(self, controller: ControllerInterface):
        """
        Sets the controller.

        Parameters:
            controller: Controller

        Returns:
            None
        """
        pass

    @abstractmethod
    def show_message(self, title: str, body: str, is_error: bool):
        """
        Show the message with 'title' and 'body'.

        Parameters_
            title :: str
            body :: str
            is_error :: bool

        Returns: None
        """
        pass

    @abstractmethod
    def get_program(self):
        """
        Gives the STLe2 program in plain text from the textarea.

        Returns:
            stle2_program :: str
        """
        pass

    @abstractmethod
    def set_program(self, program: str):
        """
        Sets the STLe2 program in the textarea.

        Parameters:
            program :: str

        Returns: None
        """
        pass

    """
    Methods called by the ApplicationService
    """

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
    def get_signal_filepath(self):
        """
        Gives the filepath of the signal.

        Returns:
            signal_filepath :: str
        """
        pass
