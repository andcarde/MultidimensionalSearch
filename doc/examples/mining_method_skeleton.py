# Look at numpy and ParetoLib.Geometry.Point libraries
# import operator
import numpy as np
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Oracle.OracleSTLe import OracleSTLe, OracleSTLeLib
from ParetoLib.Oracle.Oracle import Oracle

def mining_method(pspace: Rectangle, n: int, alpha : float, p0 : float, oracle: Oracle) -> ResultSet:
    verts = pspace.vertices()
    half = len(verts) // 2
    ver_dist = np.subtract(verts[half], verts[0]) # Not equivalent to diag_vector. This is the "side length" of the rectangle
    rect_list = [Rectangle(np.add(verts[0], np.multiply(ver_dist, i / n)),
                           np.add(verts[half - 1], np.multiply(ver_dist, (i + 1) / n))) for i in range(n)]
                           
    num_samples = int(np.ceil(np.log(alpha) / np.log(1-p0)))
    green = list()
    red = list()
    border = list()
    f = oracle.membership()

    for cell in rect_list:
        samples = np.random.uniform(cell.min_corner,cell.max_corner,size=(num_samples,cell.dim()))
        witness = True
        for s in samples:
            witness = f(s)
            if not witness:
                red.append(cell)
                break
        if witness:
            green.append(cell)
            
    return ResultSet(yup=green, ylow=red, border=border, xspace=pspace)


def plot_prueba(min_cor, max_cor, n, alpha, p0, filename):
    space = Rectangle(min_cor, max_cor)
    oracle = OracleSTLeLib()
    oracle.from_file(filename,True)
    rs = mining_method(space, n, alpha, p0, oracle)
    # It's better to check the dim() rather than the len.
    if space.dim() == 2:
        rs.plot_2D()
    elif space.dim() == 3:
        rs.plot_3D()


if __name__ == "__main__":
    min_cor = (1950.0, 0.0)
    max_cor = (2000.0, 3.0)
    n = np.random.randint(57,81)
    alpha = 0.05
    p0 = 0.01
    file = 'Tests/Oracle/OracleSTLe/2D/triangular/integral/triangular_float.txt'
    plot_prueba(min_cor, max_cor, n, alpha, p0, file)
