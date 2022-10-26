import copy
import sys
import time
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor

from typing import List, Tuple
from math import log, ceil
from itertools import product

from scipy.spatial.distance import directed_hausdorff
import numpy as np

from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib


def haussdorf_distance_yup(current_rs: ResultSet, rs_list: List[ResultSet]) -> Tuple[float]:
    # Use sets in order to prevent duplicated vertices
    class_i = current_rs.vertices_yup()
    other_classes_generator = (rs.vertices_yup() for rs in rs_list if rs != current_rs)
    other_classes = set()
    other_classes = other_classes.union(*other_classes_generator)

    # Adapt data type to directed_hausdorff format. Besides, lists allow indexing.
    class_i_list = list(class_i)
    # Removing class_i vertices from other_classes may raise errors when class_i is strictly included inside other_classes
    other_classes_list = list(other_classes - class_i)

    # (distance, index_i, index_other_classes) = directed_hausdorff(class_i, other_classes)
    _, index_i, _ = directed_hausdorff(class_i_list, other_classes_list)
    return class_i_list[index_i]


def par_haussdorf_distance_yup(args: Tuple[ResultSet, List[ResultSet]]) -> Tuple[float]:
    current_rs, rs_list = args
    return haussdorf_distance_yup(current_rs, rs_list)


def par_champions_selection(rs_list: List[ResultSet]) -> List[Tuple]:

    p = Pool(cpu_count())

    args = ((current_rs, copy.deepcopy(rs_list)) for current_rs in rs_list)
    champions = p.map(par_haussdorf_distance_yup, args)

    p.close()
    p.join()

    return champions


def champions_selection(rs_list: List[ResultSet]) -> List[Tuple]:
    champions = [haussdorf_distance_yup(current_rs, rs_list) for current_rs in rs_list]
    return champions


def confidence(p0: float, alpha: float) -> int:
    """As a concrete example, let us set p0 = 0.01 and alpha = 0.05. In this setting, we need to examine
    N >= log(1−p0) alpha = log0.99(0.05) = 298 parameter valuations to conclude with confidence 95% that the proportion
    of satisfied parameter valuation in the cell is smaller than 1%."""
    n = log(alpha, 1.0 - p0)
    return ceil(n)


def cell_partition(pspace: Rectangle, num_cells: int) -> List:
    d = pspace.dim()

    # num_cells = k^d
    k = log(num_cells, 10) / d
    k = ceil(pow(10, k))

    step = np.subtract(pspace.max_corner, pspace.min_corner)
    step = np.divide(step, k)

    indices_min_corners = product(range(k), repeat=d)
    list_min_corners = (np.add(pspace.min_corner, np.multiply(index, step)) for index in indices_min_corners)
    res = [Rectangle(min_corner, np.add(min_corner, step)) for min_corner in list_min_corners]
    return res


def test_sample(sample: iter, fs: list[callable]) -> bool:
    return all(f(sample) for f in fs)


def mining_method(pspace: Rectangle, num_cells: int, num_samples: int, oracles: list[OracleSTLeLib]) -> ResultSet:
    cells = cell_partition(pspace, num_cells)
    undef = []
    green = []
    red = []

    d = pspace.dim()
    fs = [ora.membership() for ora in oracles]
    for cell in cells:
        # Take num_samples uniformly between cell.min_corner and cell.max_corner
        samples = np.random.uniform(cell.min_corner, cell.max_corner, (num_samples, d))
        # Call the oracles with the current sample
        if any(test_sample(sample, fs) for sample in samples):
            # If all the signals eval a sample to True, then the cell goes to green.
            # It suffices that a single sample is validated by all the signals.
            green.append(cell)
        else:
            # Otherwise, the cell goes to red.
            red.append(cell)

    return ResultSet(undef, red, green, pspace)


def par_test_sample(args: tuple[iter, list[callable]]) -> bool:
    sample, fs = args
    return all(f(sample) for f in fs)


def process(args: tuple[Rectangle, list[OracleSTLeLib], int, int]) -> bool:
    cell, oracles, num_samples, d = args

    fs = [ora.membership() for ora in oracles]

    # Take num_samples uniformly between cell.min_corner and cell.max_corner
    samples = np.random.uniform(cell.min_corner, cell.max_corner, (num_samples, d))
    # Call the oracle with the current sample
    res = any(test_sample(sample, fs) for sample in samples)

    # args = ((copy.deepcopy(sample), copy.deepcopy(fs)) for sample in samples)
    # executor = ThreadPoolExecutor(max_workers=5)
    # res = any(executor.map(par_test_sample, args))

    return res


def par_mining_method(pspace: Rectangle, num_cells: int, num_samples: int, oracles: list[OracleSTLeLib]) -> ResultSet:
    cells = cell_partition(pspace, num_cells)
    undef = []
    green = []
    red = []

    d = pspace.dim()

    p = Pool(cpu_count())
    args = ((cell, copy.deepcopy(oracles), num_samples, d) for cell in cells)
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

    nfile = 'Tests/Oracle/OracleSTLe/2D/stabilization/derivative/stabilization.txt'
    oracle = OracleSTLeLib()
    oracle.from_file(nfile, human_readable=True)
    oracles = [copy.deepcopy(oracle)] * 1

    num_samples = confidence(p0, alpha)
    # pspace = Rectangle((0.0,) * 3, (1.0,) * 3)
    min_x, min_y = (80.0, 0.0)
    max_x, max_y = (120.0, 0.005)
    pspace = Rectangle((min_x, min_y), (max_x, max_y))

    start_time = time.time()
    r1 = par_mining_method(pspace, num_cells, num_samples, oracles)
    end_time = time.time()
    print("Execution time of parallel method: {0}".format(end_time - start_time))
    r1.plot_2D()

    start_time = time.time()
    r2 = mining_method(pspace, num_cells, num_samples, oracles)
    end_time = time.time()
    print("Execution time of normal method: {0}".format(end_time - start_time))
    r2.plot_2D()

    rs = [r1, r2]
    champs = champions_selection(rs)
    for i in range(len(rs)):
        print("Reference point for class {0}: {1}".format(i, champs[i]))
