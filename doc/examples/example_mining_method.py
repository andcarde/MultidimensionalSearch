# Look at numpy and ParetoLib.Geometry.Point libraries
# import operator
import numpy as np
from math import ceil, log
from typing import List, Tuple, Union, NoReturn
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Search.ParResultSet import ParResultSet
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Geometry.Point import less_equal
from multiprocessing import Pool, cpu_count
from scipy.spatial.distance import directed_hausdorff as dhf
import time
import copy
        

def champions_election_seq(rslist : List[ResultSet]) -> List[Tuple[float, Tuple[float]]]:
    dists_matr = np.empty(shape=(len(rslist),len(rslist)),dtype=tuple)
    for i in range(len(rslist)):
        yup_verts_class_i = list(rslist[i].vertices_yup()) # We want to manipulate lists but we don't want duplicates
        for j in range(i, len(rslist)):
            yup_verts_other = list(rslist[j].vertices_yup())
            dist_tup = (dhf(yup_verts_class_i,yup_verts_other), dhf(yup_verts_other, yup_verts_class_i))
            if dist_tup[0] >= dist_tup[1]:
                max_pair = [dist_tup[0][0], yup_verts_class_i[dist_tup[0][1]], yup_verts_other[dist_tup[0][2]]]
                dists_matr[i,j] = tuple(max_pair)
                max_pair[1], max_pair[2] = max_pair[2], max_pair[1]
                dists_matr[j,i] = tuple(max_pair)
            else:
                max_pair = [dist_tup[1][0], yup_verts_class_i[dist_tup[1][2]], yup_verts_other[dist_tup[1][1]]]
                dists_matr[i,j] = tuple(max_pair)
                max_pair[1], max_pair[2] = max_pair[2], max_pair[1]
                dists_matr[j,i] = tuple(max_pair)
    return [max(dists_matr[i])[:2] for i in range(len(dists_matr))]


def process_champions(args: Tuple[ResultSet,
                            ResultSet]) -> Tuple[float, Tuple[float], Tuple[float]]:
    r1, r2 = args
    vert_list1, vert_list2 = list(r1.vertices_yup()), list(r2.vertices_yup()) 
    dist_tup = (dhf(vert_list1,vert_list2), dhf(vert_list2, vert_list1))

    if dist_tup[0] >= dist_tup[1]:
        return (dist_tup[0][0], vert_list1[dist_tup[0][1]], vert_list2[dist_tup[0][2]])
    return (dist_tup[1][0], vert_list1[dist_tup[1][2]], vert_list2[dist_tup[1][1]])

def champions_election_par(rslist : List[ResultSet]) -> List[Tuple[float, Tuple[float]]]:
    rs_len = len(rslist)
    args = ((rslist[i],rslist[j]) for i in range(rs_len) for j in range(rs_len))
    p = Pool(cpu_count())
    dist_list = list(p.map(process_champions, args))
    p.close()
    p.join()
    return [max(dist_list[i*rs_len:(i+1)*rs_len])[:2] for i in range(rs_len)]


def mining_method_seq_fix(xspace: Rectangle,
                          oracles: List[Oracle],
                          num_samples: int,
                          num_cells: int) -> ResultSet:
    # type: (Rectangle, list[Oracle], int, int) -> ResultSet

    # Dimension
    n = xspace.dim()

    rect_list = xspace.cell_partition(num_cells)
    green = list()
    red = list()
    border = list()
    mems = [ora.membership() for ora in oracles]

    for cell in rect_list:
        samples = cell.uniform_sampling(num_samples)

        if any(all(f(s) for f in mems) for s in samples):
            green.append(cell)
        else:
            red.append(cell)

    return ResultSet(yup=green, ylow=red, border=border, xspace=xspace)


def mining_method_seq_dyn(xspace: Rectangle,
                          oracles: List[Oracle],
                          num_samples: int,
                          g: Tuple[float],
                          ps: float = 0.95) -> ResultSet:
    # type: (Rectangle, list[Oracle], int, tuple, float) -> ResultSet

    green = set()
    red = set()
    border = set()
    d = xspace.dim()
    mems = [ora.membership() for ora in oracles]
    samples = xspace.uniform_sampling(num_samples)

    all_fs_in_sample = (all(f(s) for f in mems) for s in samples)
    counter = sum(all_fs_in_sample)
    if counter == 0:
        red.add(xspace)
    elif counter / num_samples >= ps or less_equal(xspace.diag_vector(), g):
        green.add(xspace)
    else:
        n = pow(2, d)
        rect_list = xspace.cell_partition_bin(n)
        for r in rect_list:
            temp_rs = mining_method_seq_dyn(r, oracles, num_samples, g, ps)
            green = green.union(set(temp_rs.yup))
            red = red.union(set(temp_rs.ylow))
            border = border.union(set(temp_rs.border))

    return ResultSet(yup=list(green), ylow=list(red), border=list(border), xspace=xspace)





# Fixed size cell method
def process_fix(args: Tuple[Rectangle,
                            List[Oracle],
                            int,
                            int]) -> bool:
    cell, oracles, num_samples, d = args

    fs = [ora.membership() for ora in oracles]

    # Take num_samples uniformly between cell.min_corner and cell.max_corner
    samples = cell.uniform_sampling(num_samples)
    # Call the oracle with the current sample
    res = any(all(f(sample) for f in fs) for sample in samples)

    return res


def mining_method_par_fix(xspace: Rectangle,
                          oracles: List[Oracle],
                          num_samples: int,
                          num_cells: int) -> ParResultSet:
    cells = xspace.cell_partition(num_cells)
    border = list()
    green = list()
    red = list()
    d = xspace.dim()
    step = 0

    p = Pool(cpu_count())
    args = ((cell, copy.deepcopy(oracles), num_samples, d) for cell in cells)
    green_cells = p.map(process_fix, args)
    for i, cell in enumerate(cells):
        if green_cells[i]:
            green.append(cell)
        else:
            red.append(cell)

    p.close()
    p.join()
    return ParResultSet(border=border, ylow=red, yup=green, xspace=xspace)


# Dynamic size cell method
def process_dyn(args: Tuple[Rectangle,
                            List[Oracle],
                            int,
                            int,
                            float,
                            Tuple[float]]) -> Tuple[Rectangle, Union[bool,None]]:
    cell, oracles, num_samples, d, ps, g = args

    fs = [ora.membership() for ora in oracles]

    # Take num_samples uniformly between cell.min_corner and cell.max_corner
    samples = cell.uniform_sampling(num_samples)
    all_fs_in_sample = (all(f(s) for f in fs) for s in samples)
    counter = sum(all_fs_in_sample)
    if counter == 0:
        return cell, False
    elif counter / num_samples >= ps or less_equal(cell.diag_vector(), g):
        return cell, True
    return cell, None



def mining_method_par_dyn(xspace: Rectangle,
                          oracles: List[Oracle],
                          num_samples: int,
                          g: Tuple[float],
                          ps: float = 0.95) -> ParResultSet:
    # type: (Rectangle, list[Oracle], int, tuple[float], float) -> ParResultSet

    green = list()
    red = list()
    border = list()
    d = xspace.dim()
    p = Pool(cpu_count())

    # Create temporary directory for storing the result of each step
    cell_list = [xspace]

    while len(cell_list) > 0:
        args = ((cell, copy.deepcopy(oracles), num_samples, d, ps, g) for cell in cell_list)
        cols_list = p.map(process_dyn, args)
        cell_list = list()
        for (cell, is_green) in cols_list:
            if is_green is None:
                n = pow(2, d)
                cell_list = cell_list + cell.cell_partition_bin(n)
            elif is_green:
                green.append(cell)
            else:
                red.append(cell)
    
    p.close()
    p.join()
    return ParResultSet(border, red, green, xspace)





def plot_prueba_mining_method(min_cor, max_cor, n, alpha, p0, filenames):
    space = Rectangle(min_cor, max_cor)
    oracle_list = []

    for f in filenames:
        ora = OracleSTLeLib()
        ora.from_file(f,True)  
        oracle_list.append(ora)
    rs = mining_method_seq_fix(space, n, alpha, p0, oracle_list)
    end = time.time()
    print(end-start)
    if space.dim() == 2:
        rs.plot_2D()
    elif space.dim() == 3:
        rs.plot_3D()

    ps = 0.95
    m = 3
    g = np.multiply(space.diag_vector(),1/10)

    start = time.time()
    rs = mining_method_seq_dyn(space, ps, g, alpha, p0, oracle_list)
    end = time.time()
    print(end-start)
    if space.dim() == 2:
        rs.plot_2D()
    elif space.dim() == 3:
        rs.plot_3D()


def plot_prueba_champions(min_cor, max_cor, n, alpha, p0, filenames):
    space = Rectangle(min_cor, max_cor)
    oracle_list = []
    g = np.multiply(space.diag_vector(),1/10)

    for f in filenames:
        ora = OracleSTLeLib()
        ora.from_file(f,True)  
        oracle_list.append(ora)
    resultset_list = list()
    resultset_list.append(mining_method_seq_fix(space,oracle_list,ceil(log(alpha, 1.0 - p0)),n))
    resultset_list.append(mining_method_seq_dyn(space,oracle_list,ceil(log(alpha, 1.0 - p0)),g))
    print(champions_election_seq(resultset_list))
    print(champions_election_par(resultset_list))





if __name__ == "__main__":
    min_cor = (1950.0, 0.0)
    max_cor = (2000.0, 3.0)
    n = 25
    alpha = 0.05
    p0 = 0.01
    files = list()
    files.append('Tests/Oracle/OracleSTLe/2D/triangular/integral/triangular_int.txt')
    files.append('Tests/Oracle/OracleSTLe/2D/stabilization/derivative/stabilization.txt')
    # plot_prueba_mining_method(min_cor, max_cor, n, alpha, p0, files)
    plot_prueba_champions(min_cor, max_cor, n, alpha, p0, files)


