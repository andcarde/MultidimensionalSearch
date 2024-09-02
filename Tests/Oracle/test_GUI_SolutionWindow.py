
# test_GUI_SolutionWindow.py

import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from unittest.mock import MagicMock

from ParetoLib.GUI.solution_window import StandardSolutionWindow


class TestStandardSolutionWindow(unittest.TestCase):

    app = QApplication([])

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication([])

    def setUp(self):
        # Initialize the window
        self.window = StandardSolutionWindow()

        # Create mock ResultSets
        self.result_set_1 = MagicMock()
        self.result_set_2 = MagicMock()
        self.result_set_3 = MagicMock()

        # Set up mock behavior for dimension and plotting
        self.result_set_1.xspace.dim.return_value = 2
        self.result_set_2.xspace.dim.return_value = 3
        self.result_set_3.xspace.dim.return_value = 2

        # List of ResultSets
        self.result_sets = [self.result_set_1, self.result_set_2, self.result_set_3]
        self.var_names_list = [['x', 'y', 'z'], ['x', 'y'], ['y', 'z']]

        # Load the ResultSets into the window
        self.window._set_result_sets(self.result_sets, self.var_names_list)
        self.window.show()

    def test_initial_state(self):
        # Initially, the first ResultSet should be displayed, and the "Previous" button should be disabled
        self.assertEqual(self.window.current_index, 0)
        self.assertFalse(self.window.prev_button.isEnabled())
        self.assertTrue(self.window.next_button.isEnabled())
        self.result_set_1.plot_2D_light.assert_called_once()

    def test_navigate_next(self):
        # Simulate clicking the "Next" button
        QTest.mouseClick(self.window.next_button, Qt.LeftButton)

        # Check if the next ResultSet is displayed
        self.assertEqual(self.window.current_index, 1)
        self.result_set_2.plot_3D_light.assert_called_once()

        # The "Previous" button should now be enabled
        self.assertTrue(self.window.prev_button.isEnabled())

    def test_navigate_previous(self):
        # Navigate to the second ResultSet
        self.window.current_index = 1
        self.window.__display_result_set()

        # Simulate clicking the "Previous" button
        QTest.mouseClick(self.window.prev_button, Qt.LeftButton)

        # Check if the first ResultSet is displayed again
        self.assertEqual(self.window.current_index, 0)
        self.result_set_1.plot_2D_light.assert_called()

        # The "Previous" button should be disabled again
        self.assertFalse(self.window.prev_button.isEnabled())

    def test_last_result_set(self):
        # Navigate to the last ResultSet
        self.window.current_index = 2
        self.window.__display_result_set()

        # The "Next" button should be disabled at the last ResultSet
        self.assertFalse(self.window.next_button.isEnabled())

        # Simulate clicking the "Previous" button
        QTest.mouseClick(self.window.prev_button, Qt.LeftButton)

        # Check if the second ResultSet is displayed again
        self.assertEqual(self.window.current_index, 1)
        self.result_set_2.plot_3D_light.assert_called()

        # The "Next" button should be enabled again
        self.assertTrue(self.window.next_button.isEnabled())

    def tearDown(self):
        self.window.close()

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()


if __name__ == '__main__':
    unittest.main()
