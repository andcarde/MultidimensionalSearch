"""
<manual_GUI_StandardSolutionWindow.py>
"""

import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from ParetoLib.GUI.solution_window import StandardSolutionWindow
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet


class MainWindowMock(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Test Solution Window")
        self.setGeometry(100, 100, 800, 600)

        # Create the "Open Solution Window" button
        self.open_solution_button = QPushButton("Open Solution Window", self)
        self.open_solution_button.setGeometry(350, 250, 100, 50)
        self.open_solution_button.clicked.connect(self.open_solution_window)

        self.solution_window = None

    def open_solution_window(self):
        # Ensure the solution window is only created once and is shown as a floating window
        if not self.solution_window:
            self.solution_window = StandardSolutionWindow()
        self.solution_window.show()
        return self.solution_window

    def get_solution_window(self):
        return self.solution_window


def generate_result_set(index):
    if index == 1:
        xspace = Rectangle((0.0, 0.0), (1.0, 1.0))
        ylow = [Rectangle((0.0, 0.0), (0.5, 0.5))]
        yup = [Rectangle((0.5, 0.5), (1.0, 1.0))]
        border = [Rectangle((0.0, 0.5), (0.5, 1.0)), Rectangle((0.5, 1.0), (1.0, 1.0))]
        result_set = ResultSet(border, ylow, yup, xspace)
    elif index == 2:
        xspace = Rectangle((0.0, 0.0), (1.5, 1.5))
        ylow = [Rectangle((0.0, 0.0), (0.8, 0.8))]
        yup = [Rectangle((0.5, 0.5), (1.0, 1.0))]
        border = [Rectangle((0.0, 0.5), (0.5, 1.0)), Rectangle((0.6, 1.0), (1.0, 1.0))]
        result_set = ResultSet(border, ylow, yup, xspace)
    else:
        xspace = Rectangle((0.0, 0.0), (1.0, 1.0))
        ylow = [Rectangle((0.0, 0.0), (0.7, 0.7))]
        yup = [Rectangle((0.7, 0.7), (1.0, 1.0))]
        border = [Rectangle((0.2, 0.7), (0.6, 1.0)), Rectangle((0.6, 1.0), (1.2, 1.0))]
        result_set = ResultSet(border, ylow, yup, xspace)
    return result_set


def mytest_set_message(solution_window):
    # :: Bool
    result = False
    solution_window._set_message(result)


def mytest_set_result_sets(solution_window):
    result_sets = [generate_result_set(i) for i in range(3)]
    var_names_list = [['variable1', 'variable2', 'variable3'], ['variable4', 'variable5'], ['variable6', 'variable7']]
    solution_window._set_result_sets(result_sets, var_names_list)


def mytest_set_output_signal(solution_window):
    c_double_t1 = 1.0
    c_double_t2 = 2.0
    c_double_t3 = 3.0
    c_double_t4 = 4.0
    c_double_t5 = 5.0
    c_double_v1 = 0.0
    c_double_v2 = 2.0
    c_double_v3 = 4.0
    c_double_v4 = 6.0
    c_double_v5 = 7.0
    bool_signal = {
        c_double_t1: c_double_v1,
        c_double_t2: c_double_v2,
        c_double_t3: c_double_v3,
        c_double_t4: c_double_v4,
        c_double_t5: c_double_v5
    }
    solution_window.set_output_signal(bool_signal)


def main():
    # Create the application instance
    app = QApplication(sys.argv)

    # Create and show the main window
    main_window = MainWindowMock()
    main_window.show()

    def after_startup():
        print(1)
        solution_window = None
        while solution_window is None:
            solution_window = main_window.solution_window
            string = 'Is none? '
            if solution_window:
                string += 'No'
            else:
                string += 'Yes'
            print(string)
        print(2)
        # Breakpoint 1
        mytest_set_message(solution_window)
        print(3)
        # Breakpoint 2
        mytest_set_result_sets(solution_window)
        print(4)
        # Breakpoint 3
        mytest_set_output_signal(solution_window)

    QTimer.singleShot(5000, after_startup)

    # Start the event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
