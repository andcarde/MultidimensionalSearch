# Look at numpy and ParetoLib.Geometry.Point libraries
# import operator
import numpy as np
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.ResultSet import ResultSet

# def opera_tupla(op, tup1, tup2):
#     assert (len(tup1) == len(tup2))
#     return tuple(map(op, tup1, tup2))


# def escalar_tupla(op, esc, tup):
#     return tuple([op(esc, x) for x in tup])


# mining_method(pspace: Rectangle, n: int) -> ResultSet. Divide pspace into n Rectangles of the same size and classify them
def mining_method(pspace, n):
    verts = pspace.vertices() # Methods that start by _ usually are private methods
    half = len(verts) // 2
    # max_corner = verts[half], min_corner = verts[0]?
    ver_dist = np.subtract(verts[half], verts[0]) # Equivalent to pspace.diag_vector() ?
    rect_list = [Rectangle(np.add(verts[0], np.multiply(ver_dist, i / n)),
                           np.add(verts[half - 1], np.multiply(ver_dist, (i + 1) / n))) for i in range(n)]

    ### Approach 1: Vertex matrix. Discarded for the moment ###

    # mat_verts = list(list())
    # for i in range(half):
    #    ver_ini = verts[i]
    #    ver_dist = opera_tupla(operator.sub,verts[i+half],verts[i])
    #    mat_verts.append([opera_tupla(operator.add,ver_ini,escalar_tupla(operator.mul,j/n,ver_dist)) for j in range(n+1)])

    # rect_list = [Rectangle(mat_verts[0][i],mat_verts[len(mat_verts)-1][i+1]) for i in range(len(mat_verts[0])-1)]

    # n//2 should be equivalent
    return ResultSet(yup=rect_list[:n // 2], ylow=rect_list[n // 2:], xspace=pspace)


def plot_prueba(min_cor, max_cor, n):
    space = Rectangle(min_cor, max_cor)
    rs = mining_method(space, n)
    # It's better to check the dim() rather than the len.
    if space.dim() == 2:
        rs.plot_2D()
    elif space.dim() == 3:
        rs.plot_3D()


if __name__ == "__main__":
    min_cor = (1, 2, 3)
    max_cor = (5, 3, 7)
    n = 10
    plot_prueba(min_cor, max_cor, n)
