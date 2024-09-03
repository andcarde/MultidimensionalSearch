"""
<mpl_canvas.py>
"""

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, width: int = 5, height: int = 4, dpi: int = 100):
        """
        Parameters:
            width :: int
            height :: int
            dpi :: int
        """
        self.axes = None
        # :: Figure
        figure = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(figure)

    def set_axis(self):
        """
        Sets the axis.

        Returns: None
        """
        self.axes = self.figure.add_subplot(111)
