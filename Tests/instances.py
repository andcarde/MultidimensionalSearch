"""
<instances.py>

This file aims to implement instances for classes that will be used as placeholders in tests. The lack of interfaces in
the project severely impacts the maintainability of the code. This file seeks to generate randomized instances of the
classes to import them as examples, avoiding the need to deal with their internal logic or complex constructors.
"""
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet


def generate_rectangle():
    rectangle = Rectangle((0.0, 0.0), (0.5, 0.5))
    return rectangle


def generate_result_set():
    border = [Rectangle((0.0, 0.5), (0.5, 1.0)), Rectangle((0.5, 1.0), (1.0, 1.0))]
    xspace = Rectangle((0.0, 0.0), (1.0, 1.0))
    ylow = [Rectangle((0.0, 0.0), (0.5, 0.5))]
    yup = [Rectangle((0.5, 0.5), (1.0, 1.0))]
    result_set = ResultSet(border, ylow, yup, xspace)
    return result_set
