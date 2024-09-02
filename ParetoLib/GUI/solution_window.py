"""
<solution_window.py>
"""

import matplotlib
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout

from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.GUI.mpl_canvas import MplCanvas
from ParetoLib.GUI.solution_window_interface import SolutionWindowInterface

matplotlib.use('Qt5Agg')


class StandardSolutionWindow(QWidget, SolutionWindowInterface):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    # :: StandardSolutionWindow: Single instance using the singleton pattern
    instance = None

    def __init__(self):
        super().__init__()
        self.setObjectName("Solution")

        # :: QVBoxLayout
        self.setLayout(QVBoxLayout())

        # Initialize result sets list and current index
        self.result_sets = []
        self.var_names_list = []
        self.current_index = 0

        # Create navigation buttons
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        # Connect buttons to navigation methods
        # noinspection PyUnresolvedReferences
        self.prev_button.clicked.connect(self._show_previous_result_set)
        # noinspection PyUnresolvedReferences
        self.next_button.clicked.connect(self._show_next_result_set)

        # Create a horizontal layout for buttons and add them to the main layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        self.layout().addLayout(button_layout)

        # Set the buttons initially disabled until result sets are loaded
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

    def _set_message(self, result: bool):
        """
        Parameters:
        result: bool

        Returns: None
        """
        # :: QLabel : Message
        label = QLabel(str(result))
        self.layout().addWidget(label)

    def _set_result_sets(self, result_sets: list, var_names_list: list):
        """
        Set multiple ResultSets and initialize the view.

        Parameters:
        result_set :: List[ResultSet]
        var_names :: List[List[str]]

        Returns: None
        """
        self.result_sets = result_sets
        self.var_names_list = var_names_list
        # Start with the first ResultSet
        self.current_index = 0

        if self.result_sets:
            self._display_result_set()

    def _clear(self):
        """
        Clear existing canvas.

        Returns: None
        """
        for i in reversed(range(self.layout().count())):
            widget = self.layout().itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

    def _display_result_set(self):
        """
        Display the ResultSet at the given index.

        Parameters:
        index: int

        Returns: None
        """
        # Clear existing canvas
        self._clear()

        # :: ResultSet
        result_set = self.result_sets[self.current_index]

        # :: MplCanvas : Create the canvas
        canvas = MplCanvas(parent=self)
        self._set_toolbar(canvas)
        self.layout().addWidget(canvas)

        # Plot based on the dimension of the result set
        # :: List[str]
        var_names = self.var_names_list[self.current_index]
        if result_set.xspace.dim() == 2:
            result_set.plot_2D_light(var_names=var_names, fig1=canvas.figure)
        elif result_set.xspace.dim() == 3:
            result_set.plot_3D_light(var_names=var_names, fig1=canvas.figure)

        # Update buttons
        self._update_buttons()

    def _show_previous_result_set(self):
        """
        Show the previous ResultSet in the list.

        Returns: None
        """
        if self.current_index > 0:
            self.current_index -= 1
            self._display_result_set()

    def _show_next_result_set(self):
        """
        Show the next ResultSet in the list.

        Returns: None
        """
        if self.current_index < len(self.result_sets) - 1:
            self.current_index += 1
            self._display_result_set()

    def _update_buttons(self):
        """
        Update the state of navigation buttons based on the current index.

        Returns: None
        """
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.result_sets) - 1)

    def _set_toolbar(self, canvas: MplCanvas):
        """
        Create toolbar, passing canvas as first parameter and the main_window as second.

        Parameters:
        canvas: MplCanvas

        Returns: None
        """
        toolbar = NavigationToolbar2QT(canvas, parent=self)
        self.layout().addWidget(toolbar)

    def set_output_signal(self, bool_signal: dict):
        """
        Parameters:
        bool_signal :: dict[c_double, c_double]

        Returns: None
        """
        x = bool_signal.keys()
        y = bool_signal.values()
        canvas = MplCanvas(parent=self)
        canvas.set_axis()
        canvas.axes.step(x, y, where='post')
        canvas.figure.tight_layout(pad=0)

        self._set_toolbar(canvas)
        self.layout().addWidget(canvas)

    @classmethod
    def _new_solution_window(cls):
        if cls.instance:
            cls.instance.close()
        cls.instance = StandardSolutionWindow()
        return cls.instance

    @staticmethod
    def show_solution(satisfied: bool, bool_signal: dict):
        """
        Parameters:
        satisfied :: bool
        bool_signal :: dict[c_double, c_double]

        Return: None
        """
        # :: StandardSolutionWindow
        solution_window = StandardSolutionWindow._new_solution_window()
        solution_window.set_output_signal(bool_signal)
        solution_window._set_message(satisfied)
        solution_window.show()

    @staticmethod
    def show_single_oracle_solution(result_set: ResultSet, var_names: list):
        """
        Parameters:
        result_set :: ResultSet
        var_names :: List[str]

        Return: None
        """
        # :: StandardSolutionWindow
        solution_window = StandardSolutionWindow._new_solution_window()
        solution_window._set_result_sets([result_set], [var_names])
        solution_window.show()

    @staticmethod
    def show_multi_oracle_solution(result_set: ResultSet, parameters: list):
        """
        Parameters:
            result_set :: ResultSet
            parameters :: List[str]

        Return: None
        """
        # :: StandardSolutionWindow
        solution_window = StandardSolutionWindow._new_solution_window()
        solution_window._set_result_sets([result_set], [parameters])
        solution_window.show()

    @staticmethod
    def show_no_result_set_solution():
        """
        Returns: None
        """
        # :: StandardSolutionWindow
        solution_window = StandardSolutionWindow._new_solution_window()
        solution_window.show()
