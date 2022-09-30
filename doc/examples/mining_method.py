import copy
import sys
import time
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor

from typing import List
from math import log, ceil
from itertools import product
import numpy as np
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib


def confidence(p0: float, alpha: float) -> int:
    """As a concrete example, let us set p0 = 0.01 and alpha = 0.05. In this setting, we need to examine
    N >= log(1−p0) alpha = log0.99(0.05) = 298 parameter valuations to conclude with confidence 95% that the proportion
    of satisfied parameter valuation in the cell is smaller than 1%."""
    n = log(alpha, 1-p0)
    return ceil(n)


def cell_partition(pspace: Rectangle, num_cells: int) -> List:
    d = pspace.dim()

    # num_cells = k^d
    k = log(num_cells, 10)/d
    k = ceil(pow(10, k))

    step = np.subtract(pspace.max_corner, pspace.min_corner)
    step = np.divide(step, k)

    indices_min_corners = product(range(k), repeat=d)
    list_min_corners = (np.add(pspace.min_corner, np.multiply(index, step)) for index in indices_min_corners)
    res = [Rectangle(min_corner, np.add(min_corner, step)) for min_corner in list_min_corners]
    return res


# Inicializacion del Oracle
# Num_muestras
def mining_method(pspace: Rectangle, num_cells: int, num_samples: int, oracle: OracleSTLeLib) -> ResultSet:
    cells = cell_partition(pspace, num_cells)
    undef = []
    green = []
    red = []

    d = pspace.dim()
    f = oracle.membership()
    for cell in cells:
        # Take num_samples uniformly between cell.min_corner and cell.max_corner
        samples = np.random.uniform(cell.min_corner, cell.max_corner, (num_samples, d))
        # Call the oracle with the current sample
        eval_samples = (f(sample) for sample in samples)
        # If all the samples eval to True, then the cell goes to green. Otherwise, cell goes to red.
        if all(eval_samples):
            green.append(cell)
        else:
            red.append(cell)

    return ResultSet(undef, red, green, pspace)


# def process(cell: Rectangle, f: callable, num_samples: int, d: int) -> bool:
def process(args: tuple) -> bool:
    cell, oracle, num_samples, d = args

    f = oracle.membership()

    # Take num_samples uniformly between cell.min_corner and cell.max_corner
    samples = np.random.uniform(cell.min_corner, cell.max_corner, (num_samples, d))
    # Call the oracle with the current sample
    eval_samples = (f(sample) for sample in samples)
    # executor = ThreadPoolExecutor(max_workers=5)
    # eval_samples = executor.map(f, samples)
    # If all the samples eval to True, then the cell goes to green. Otherwise, cell goes to red.
    return all(eval_samples)


def par_mining_method(pspace: Rectangle, num_cells: int, num_samples: int, oracle: OracleSTLeLib) -> ResultSet:

    cells = cell_partition(pspace, num_cells)
    undef = []
    green = []
    red = []

    d = pspace.dim()

    p = Pool(cpu_count())
    args = ((cell, copy.deepcopy(oracle), num_samples, d) for cell in cells)
    green_cells = p.map(process, args)
    for i, cell in enumerate(cells):
        if green_cells[i]:
            green.append(cell)
        else:
            red.append(cell)

    p.close()
    p.join()
    return ResultSet(undef, red, green, pspace)


if __name__ == "__main__":
    # python3 this_file.py num_cells p0 alpha
    # python3 mining_method.py 1000 0.01 0.05

    num_cells = int(sys.argv[1])
    p0 = float(sys.argv[2])
    alpha = float(sys.argv[3])

    nfile = '../../Tests/Oracle/OracleSTLe/2D/stabilization/derivative/stabilization.txt'
    oracle = OracleSTLeLib()
    oracle.from_file(nfile, human_readable=True)

    num_samples = confidence(p0, alpha)
    # pspace = Rectangle((0.0,) * 3, (1.0,) * 3)
    min_x, min_y = (80.0, 0.0)
    max_x, max_y = (120.0, 0.005)
    pspace = Rectangle((min_x, min_y), (max_x, max_y))

    start_time = time.time()
    r = par_mining_method(pspace, num_cells, num_samples, oracle)
    end_time = time.time()
    print("Execution time: {0}".format(end_time - start_time))

    r.plot_2D()

    start_time = time.time()
    r = mining_method(pspace, num_cells, num_samples, oracle)
    end_time = time.time()
    print("Execution time: {0}".format(end_time - start_time))
    r.plot_2D()
