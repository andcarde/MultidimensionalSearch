# Look at numpy and ParetoLib.Geometry.Point libraries
# import operator
import numpy as np
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Oracle.OracleSTLe import OracleSTLe, OracleSTLeLib
from ParetoLib.Oracle.OracleFunction import OracleFunction, Condition
from ParetoLib.Oracle.Oracle import Oracle
from multiprocessing import Pool


def mining_method_seq_dyn(cell: Rectangle, ps : float, m : int, g : tuple[float], alpha : float, p0 : float, oracles: list[Oracle]) -> ResultSet:

    num_samples = int(np.ceil(np.log(alpha) / np.log(1-p0)))
    green = set()
    red = set()
    border = set()
    mems = [ora.membership() for ora in oracles]
    samples = np.random.uniform(cell.min_corner,cell.max_corner,size=(num_samples,cell.dim()))
    counter = 0


    for s in samples:
        if all([f(s) for f in mems]):
            counter += 1
    
    if counter == 0:
        red.add(cell)
    elif counter / num_samples >= ps or cell.diag_vector() <= g:
        green.add(cell)
    else:
        print(cell.diag_vector())
        print(g)
        n = m//2
        verts = cell.vertices()
        half = len(verts) // 2
        ver_dist = np.subtract(verts[half], verts[0])
        rect_list = [Rectangle(np.add(verts[0], np.multiply(ver_dist, i / n)),
                            np.add(verts[half - 1], np.multiply(ver_dist, (i + 1) / n))) for i in range(n)]
        rest = m-n
        for rect in rect_list:
            verts = rect.vertices()
            ver_dist = np.subtract(verts[half-1],verts[0])
            new_rect_list = [Rectangle(np.add(verts[0], np.multiply(ver_dist, i / rest)),
                                np.add(verts[half], np.multiply(ver_dist, (i + 1) / rest))) for i in range(rest)]
            for r in new_rect_list:
                temp_rs = mining_method_seq_dyn(r,ps,m,g,alpha,p0,oracles)
                green = green.union(set(temp_rs.yup))
                red = red.union(set(temp_rs.ylow))
                border = border.union(set(temp_rs.border))
            
    return ResultSet(yup=list(green), ylow=list(red), border=list(border), xspace=cell)

def mining_method_seq_fix(pspace: Rectangle, n: int, alpha : float, p0 : float, oracles: list[Oracle]) -> ResultSet:
    rect_list = pspace.static_cell_partition(n)

    num_samples = int(np.ceil(np.log(alpha) / np.log(1-p0)))
    green = list()
    red = list()
    border = list()
    mems = [ora.membership() for ora in oracles]

    for cell in rect_list:
        samples = np.random.uniform(cell.min_corner,cell.max_corner,size=(num_samples,cell.dim()))
        if any([all([f(s) for f in mems]) for s in samples]):
            green.append(cell)
        else:
            red.append(cell)
        
            
    return ResultSet(yup=green, ylow=red, border=border, xspace=pspace)





def mining_method_par_fix(pspace: Rectangle, n: int, alpha : float, p0 : float, oracles: list[Oracle]) -> ResultSet:
    rect_list = pspace.static_cell_partition(n)
                           
    num_samples = int(np.ceil(np.log(alpha) / np.log(1-p0)))
    green = list()
    red = list()
    border = list()
    mems = [ora.membership() for ora in oracles]

    proc_pool = Pool(n)
    proc_pool.map()

    for cell in rect_list:
        samples = np.random.uniform(cell.min_corner,cell.max_corner,size=(num_samples,cell.dim()))
        if any([all([f(s) for f in mems]) for s in samples]):
            green.append(cell)
        else:
            red.append(cell)
        
            
    return ResultSet(yup=green, ylow=red, border=border, xspace=pspace)


def plot_prueba(min_cor, max_cor, n, alpha, p0, filenames):
    space = Rectangle(min_cor, max_cor)
    oracle_list = []

    for f in filenames:
        ora = OracleSTLeLib()
        ora.from_file(f,True)  
        oracle_list.append(ora)
    rs = mining_method_seq_fix(space, n, alpha, p0, oracle_list)
    if space.dim() == 2:
        rs.plot_2D()
    elif space.dim() == 3:
        rs.plot_3D()
    
    ps = 0.95
    m = 7
    g = [1] * space.dim()

    rs = mining_method_seq_dyn(space, ps, m, tuple(g), alpha, p0, oracle_list)
    if space.dim() == 2:
        rs.plot_2D()
    elif space.dim() == 3:
        rs.plot_3D()





if __name__ == "__main__":
    min_cor = (1950.0, 0.0)
    max_cor = (2000.0, 3.0)
    n = 10
    alpha = 0.05
    p0 = 0.01
    files = list()
    files.append('Tests/Oracle/OracleSTLe/2D/triangular/integral/triangular_float.txt')
    files.append('Tests/Oracle/OracleSTLe/2D/stabilization/derivative/stabilization.txt')
    plot_prueba(min_cor, max_cor, n, alpha, p0, files)

