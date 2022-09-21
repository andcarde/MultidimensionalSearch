import sys

from typing import List
from math import log, ceil
from itertools import product
import numpy as np
# from ParetoLib.Geometry.Point import add, subtract, mult, div
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet


# def cell_partition(pspace: Rectangle, num_cells: int) -> List:
#     d = pspace.dim()
#     # num_cells = k^d
#     k = log(num_cells, d)
#     k = floor(k)
#     step = subtract(pspace.max_corner, pspace.min_corner)
#     step = div(step, k)
#     indices_min_corners = product(range(k), repeat=d)
#     list_min_corners = (add(pspace.min_corner, mult(index, step)) for index in indices_min_corners)
#     res = [Rectangle(min_corner, add(min_corner, step)) for min_corner in list_min_corners]
#     return res

def cell_partition(pspace: Rectangle, num_cells: int) -> List:
    d = pspace.dim()
    # num_cells = k^d
    k = log(num_cells, 10)/d
    print("k: {0}".format(k))
    k = ceil(pow(10, k))
    print("k: {0}".format(k))
    step = np.subtract(pspace.max_corner, pspace.min_corner)
    step = np.divide(step, k)
    print("step: {0}".format(step))
    indices_min_corners = product(range(k), repeat=d)
    list_min_corners = (np.add(pspace.min_corner, np.multiply(index, step)) for index in indices_min_corners)
    res = [Rectangle(min_corner, np.add(min_corner, step)) for min_corner in list_min_corners]
    # print("res: {0} len: {1}".format(res, len(res)))
    print("len(res): {0}".format(len(res)))
    return res


def mining_method(pspace: Rectangle, num_cells: int) -> ResultSet:
    cells = cell_partition(pspace, num_cells)
    num_cells = len(cells)
    undef = []
    green = []
    red = []
    half = num_cells // 2
    for i in range(half):
        green.append(cells[i])

    for i in range(half, num_cells):
        red.append(cells[i])

    return ResultSet(undef, red, green, pspace)


if __name__ == "__main__":
    n = int(sys.argv[1])
    pspace = Rectangle((0.0,) * 3, (1.0,) * 3)
    r = mining_method(pspace, n)
    r.plot_3D()
