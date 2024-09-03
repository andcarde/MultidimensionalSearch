from abc import ABC, abstractmethod


class ControllerInterface(ABC):

    @abstractmethod
    def check_run(self, stle2_program, signal_filepath):
        """
        stle2_filepath :: str
        signal_filepath :: str
        """
        pass
