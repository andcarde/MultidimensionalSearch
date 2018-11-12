import math
import numpy as np
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from itertools import product, tee

from ParetoLib.Geometry.Segment import Segment
from ParetoLib.Geometry.Point import greater, greater_equal, less, less_equal, add, subtract, div, mult, distance, dim, \
    incomparables, select, subt, int_to_bin_tuple
from ParetoLib._py3k import reduce


# Rectangle
# Rectangular Half-Space
# Rectangular Cones

class Rectangle(object):
    # min_corner, max_corner
    def __init__(self,
                 min_corner=(float('-inf'),) * 2,
                 max_corner=(float('-inf'),) * 2):
        # type: (Rectangle, tuple, tuple) -> None
        assert dim(min_corner) == dim(max_corner)

        self.min_corner = tuple(min(mini, maxi) for mini, maxi in zip(min_corner, max_corner))
        self.max_corner = tuple(max(mini, maxi) for mini, maxi in zip(min_corner, max_corner))
        # Volume (self.vol) is calculated on demand the first time is accessed, and cached afterwards.
        # Using 'None' for indicating that attribute vol is outdated (e.g., user changes min_corner or max_corners)
        self.vol = None
        self.vertx = None

        assert greater_equal(self.max_corner, self.min_corner) or incomparables(self.min_corner, self.max_corner)

    # Attribute access
    def __setattr__(self, name, value):
        # type: (Rectangle, str, None) -> None

        str_vertx = 'vertx'
        if name != str_vertx:
            # self.__dict__[str_vertx] = None
            object.__setattr__(self, str_vertx, None)

        # Every time a corner is changed, the volume is marked as 'outdated'. 
        # It is used for a lazy computation of volume when requested by the user,
        # and therefore avoiding unecessary computations
        str_vol = 'vol'
        if name != str_vol:
            # self.__dict__[str_vol] = None
            object.__setattr__(self, str_vol, None)

        # self.__dict__[name] = None
        object.__setattr__(self, name, value)

    # Membership function
    def __contains__(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        # xpoint is strictly inside the rectangle (i.e., is not along the border)
        return (greater(xpoint, self.min_corner) and
                less(xpoint, self.max_corner))

    def inside(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        # xpoint is inside the rectangle or along the border
        return (greater_equal(xpoint, self.min_corner) and
                less_equal(xpoint, self.max_corner))

    # Printers
    def to_str(self):
        # type: (Rectangle) -> str
        _string = '['
        _string += str(self.min_corner)
        _string += ', '
        _string += str(self.max_corner)
        _string += ']'
        return _string

    def __repr__(self):
        # type: (Rectangle) -> str
        return self.to_str()

    def __str__(self):
        # type: (Rectangle) -> str
        return self.to_str()

    # Equality functions
    def __eq__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return (other.min_corner == self.min_corner) and (other.max_corner == self.max_corner)

    def __ne__(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    def __hash__(self):
        # type: (Rectangle) -> int
        return hash((self.min_corner, self.max_corner))

    # Rectangle properties
    def dim(self):
        # type: (Rectangle) -> int
        return dim(self.min_corner)

    def diag_length(self):
        # type: (Rectangle) -> tuple
        return subtract(self.max_corner, self.min_corner)

    # def norm(self):
    #     # type: (Rectangle) -> float
    # diagonal_length = self.diag_length()
    # return norm(diagonal_length)

    def norm(self):
        # type: (Rectangle) -> float
        diagonal = self.diag()
        return diagonal.norm()

    def _volume(self):
        # type: (Rectangle) -> float
        diagonal_length = self.diag_length()
        _prod = reduce(lambda si, sj: si * sj, diagonal_length)
        return abs(_prod)

    def volume(self):
        # type: (Rectangle) -> float
        # Recalculate volume if it is outdated
        if self.vol is None:
            self.vol = self._volume()
        return self.vol

    def num_vertices(self):
        # type: (Rectangle) -> int
        return int(math.pow(2, self.dim()))

    def _vertices(self):
        # type: (Rectangle) -> list
        deltas = self.diag_length()
        vertex = self.min_corner
        num_vertex = self.num_vertices()
        d = self.dim()
        vertices = [None] * num_vertex
        for i in range(num_vertex):
            delta_index = int_to_bin_tuple(i, d)
            deltai = select(deltas, delta_index)
            vertices[i] = add(vertex, deltai)
        assert (len(vertices) == num_vertex), 'Error in the number of vertices'
        return vertices

    def vertices(self):
        # type: (Rectangle) -> list
        # Recalculate vertices if it is outdated
        if self.vertx is None:
            self.vertx = self._vertices()
        return self.vertx

    def diag(self):
        # type: (Rectangle) -> Segment
        return Segment(self.min_corner, self.max_corner)

    def center(self):
        # type: (Rectangle) -> tuple
        offset = div(self.diag_length(), 2.0)
        return add(self.min_corner, offset)

    def distance_to_center(self, xpoint):
        # type: (Rectangle, tuple) -> float
        middle_point = self.center()
        euclidean_dist = distance(xpoint, middle_point)
        return euclidean_dist

    def get_points(self, n):
        # type: (Rectangle, int) -> list
        # Return n points along the rectangle diagonal, excluding min/max corners
        # n internal points = n + 1 internal segments
        m = n + 1
        diag_step = div(self.diag_length(), m)
        min_point = add(self.min_corner, diag_step)
        point_list = [add(min_point, mult(diag_step, i)) for i in range(n)]
        return point_list

    # Geometric operations between two rectangles
    def is_concatenable(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        d = self.dim()
        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)
        # (self != other)
        return (not self.overlaps(other)) \
               and len(vert_self) == len(vert_other) \
               and len(vert_self) == pow(2, d) \
               and len(inter) == pow(2, d - 1)

    def concatenate(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap'

        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)
        rect = Rectangle(self.min_corner, self.max_corner)

        # if len(vert_1) == len(vert_2) and \
        #    len(vert_1) == pow(2, d) and \
        #    len(inter) == pow(2, d - 1):
        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            new_union_vertices = (vert_self.union(vert_other)) - inter
            assert len(new_union_vertices) > 0, \
                'Error in computing vertices for the concatenation of "' + str(self) + '" and "' + str(other) + '"'

            rect.min_corner = min(new_union_vertices)
            rect.max_corner = max(new_union_vertices)
        return rect

    def concatenate_update(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        assert (not self.overlaps(other)), 'Rectangles should not overlap'

        vert_self = set(self.vertices())
        vert_other = set(other.vertices())
        inter = vert_self.intersection(vert_other)

        # if 'self' and 'other' are concatenable
        if self.is_concatenable(other):
            new_union_vertices = (vert_self.union(vert_other)) - inter
            assert len(new_union_vertices) > 0, \
                'Error in computing vertices for the concatenation of "' + str(self) + '" and "' + str(other) + '"'

            self.min_corner = min(new_union_vertices)
            self.max_corner = max(new_union_vertices)
        return self

    @staticmethod
    def _overlaps(minc, maxc):
        return less(minc, maxc)

    def overlaps(self, other):
        # type: (Rectangle, Rectangle) -> bool
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        # return less(minc, maxc)
        return self._overlaps(minc, maxc)

    def intersection(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        # if less(minc, maxc):
        if self._overlaps(minc, maxc):
            return Rectangle(minc, maxc)
        else:
            return Rectangle(self.min_corner, self.max_corner)

    def intersection_update(self, other):
        # type: (Rectangle, Rectangle) -> Rectangle
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        minc = tuple(max(self_i, other_i) for self_i, other_i in zip(self.min_corner, other.min_corner))
        maxc = tuple(min(self_i, other_i) for self_i, other_i in zip(self.max_corner, other.max_corner))
        # if less(minc, maxc):
        if self._overlaps(minc, maxc):
            self.min_corner = minc
            self.max_corner = maxc
        return self

    __and__ = intersection

    def difference(self, other):
        # type: (Rectangle, Rectangle) -> iter
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'

        def pairwise(iterable):
            """s -> (s0, s1), (s1, s2), (s2, s3), ..."""
            a, b = tee(iterable)
            next(b, None)
            return zip(a, b)

        inter = self & other
        if inter == self:
            yield self
        else:
            # d is a list with dimension equal to the rectangle dimension.
            dimension = self.dim()

            # For each dimension i, d[i] = {self.min_corner[i], self.max_corner[i]} plus
            # all the points of rectangle 'other' that fall inside of rectangle 'self'
            d = [{self.min_corner[i], self.max_corner[i]} for i in range(dimension)]

            # At maximum:
            # d[i] = {self.min_corner[i], self.max_corner[i], other.min_corner[i], other.max_corner[i]}
            for i in range(dimension):
                if self.min_corner[i] < other.min_corner[i] < self.max_corner[i]:
                    d[i].add(other.min_corner[i])
                if self.min_corner[i] < other.max_corner[i] < self.max_corner[i]:
                    d[i].add(other.max_corner[i])

            # elem[i] = pairwise(d[i])
            # if d[i] = {a, b, c, d} then
            # elem[i] = [(a, b), (b, c), (c, d)]
            elem = (pairwise(sorted(item)) for item in d)

            # Given:
            # elem[i] = [(a, b), (b, c)]
            # elem[j] = [(x, y), (y, z)]
            for vertex in product(*elem):
                # product[0] = ((a, b), (x, y))
                # product[1] = ((a, b), (y, z))
                # product[2] = ((b, c), (x, y))
                # product[3] = ((b, c), (y, z))
                #
                # vertex = ((a, b), (x, y))
                # minc = (a, x)
                # maxc = (b, y)
                minc = tuple(item[0] for item in vertex)
                maxc = tuple(item[1] for item in vertex)
                instance = Rectangle(minc, maxc)
                if instance != inter:
                    yield instance
            # At maximum, len(vertex) = product of len(elem[i]) for i in range(d) = 3**d
            # The maximum number of sub-cubes is 3**d - 1 because the intersection is removed

    def min_set_difference(self, other):
        # type: (Rectangle, Rectangle) -> list
        assert self.dim() == other.dim(), 'Rectangles should have the same dimension'
        return Rectangle.fusion_rectangles(self.difference(other))

    # __sub__ = difference
    __sub__ = min_set_difference

    # Domination
    def dominates_point(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        return less_equal(self.max_corner, xpoint)

    def is_dominated_by_point(self, xpoint):
        # type: (Rectangle, tuple) -> bool
        return less_equal(xpoint, self.min_corner)

    def dominates_rect(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return less_equal(self.max_corner, other.min_corner) # testing. Strict dominance and not overlap
        # return less_equal(self.min_corner, other.min_corner) and less_equal(self.max_corner, other.max_corner) # working

    def is_dominated_by_rect(self, other):
        # type: (Rectangle, Rectangle) -> bool
        return other.dominates_rect(self)

    # Matplot functions
    def plot_2D(self, c='red', xaxe=0, yaxe=1, opacity=1.0):
        # type: (Rectangle, str, int, int, float) -> patches.Rectangle
        assert (self.dim() >= 2), 'Dimension required >= 2'
        mc = (self.min_corner[xaxe], self.min_corner[yaxe],)
        width = self.diag_length()[xaxe]
        height = self.diag_length()[yaxe]
        return patches.Rectangle(
            mc,  # (x,y)
            width,  # width
            height,  # height
            # color = c, #color
            facecolor=c,  # face color
            edgecolor='black',  # edge color
            alpha=opacity
        )

    def plot_3D(self, c='red', xaxe=0, yaxe=1, zaxe=2, opacity=1.0):
        # type: (Rectangle, str, int, int, int, float) -> Poly3DCollection
        assert (self.dim() >= 3), 'Dimension required >= 3'

        minc = (self.min_corner[xaxe], self.min_corner[yaxe], self.min_corner[zaxe],)
        maxc = (self.max_corner[xaxe], self.max_corner[yaxe], self.max_corner[zaxe],)
        rect = Rectangle(minc, maxc)

        # sorted(vertices) =
        # [(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
        points = np.array(sorted(rect.vertices()))

        edges = [
            [points[0], points[1], points[3], points[2]],
            [points[2], points[3], points[7], points[6]],
            [points[6], points[4], points[5], points[7]],
            [points[4], points[5], points[1], points[0]],
            [points[0], points[4], points[6], points[2]],
            [points[1], points[5], points[7], points[3]]
        ]

        faces = Poly3DCollection(edges, linewidths=1, edgecolors='k')
        # faces.set_facecolor((0,0,1,0.1))
        # faces.set_facecolor('r')
        faces.set_alpha(opacity)
        faces.set_facecolor(c)
        return faces

    #####################
    # Auxiliary functions
    #####################

    # Concatenation of cubes in a list
    @staticmethod
    def fusion_rectangles(list_rect):
        # type: (iter) -> list

        # Copy list_rect
        list_out = list(list_rect)
        keep_merging = True
        while keep_merging:
            keep_merging = False
            i = 0
            while i < len(list_out):
                j = i + 1
                while j < len(list_out):
                    if list_out[i].is_concatenable(list_out[j]):
                        list_out[i].concatenate_update(list_out[j])
                        # list_out.remove(list_out[j])
                        list_out.pop(j)
                        keep_merging = True
                    else:
                        j = j + 1
                i = i + 1
        return list_out


    @staticmethod
    def fusion_rectangles_func(list_rect):
        # type: (iter) -> list

        # Copy list_rect
        list_out = list(list_rect)
        while True:
            concat_list = ((rect1, rect2) for rect1 in list_out for rect2 in list_out if
                           rect1 != rect2 and rect1.is_concatenable(rect2))
            try:
                rect1, rect2 = next(concat_list)
                rect1.concatenate_update(rect2)
                list_out.remove(rect2)
            except StopIteration:
                break
        return list_out

    # Difference of cubes in a list
    @staticmethod
    def difference_rectangles(rect, list_rect):
        # type: (Rectangle, list) -> list
        # Given a rectangle 'rect' and a list of rectangles 'list_rect', the algorithm computes
        # rect = rect - ri for every ri in list_rect

        new_rect = {rect}

        for b in list_rect:
            temp = set()
            for a in new_rect:
                # Add 'a' to the temporal set of cubes
                temp.add(a)
                if b.overlaps(a):
                    # Add the set of cubes 'a' - 'b'
                    temp = temp.union(a - b)
                    # Remove 'a'
                    temp.discard(a)
            new_rect = temp

        # return list(new_rect)
        return Rectangle.fusion_rectangles(new_rect)

    @staticmethod
    def difference_rectangles_func(rect, list_rect):
        # type: (Rectangle, list) -> list
        # Given a rectangle 'rect' and a list of rectangles 'list_rect', the algorithm computes
        # rect = rect - ri for every ri in list_rect

        new_rect = {rect}

        for b in list_rect:
            temp = set()
            for a in new_rect:
                if b.overlaps(a):
                    if b.intersection(a) != a:
                        # Add the set of cubes 'a' - 'b'
                        temp = temp.union(a - b)
                    # else: # b.intersection(a) == a:
                    # 'a' is fully contained inside 'b'
                    # No need to calculate the difference.
                    # Discard 'a'
                    temp.discard(a)
                else:
                    temp.add(a)
            new_rect = temp

        # return list(new_rect)
        return Rectangle.fusion_rectangles(new_rect)

##################
# Alpha generators
##################
# Set of functions for generating the 'alphas' that will rule the creation of comparable and incomparable cubes
# Alpha in [0,1]^n
def comp(d):
    # Set of comparable rectangles
    # Particular cases of alpha
    # zero = (0_1,...,0_d)
    zero = (0,) * d
    # one = (1_1,...,1_d)
    one = (1,) * d
    return [zero, one]


def incomp_expanded(d):
    # type: (int) -> list
    alphaprime = (range(2),) * d
    alpha = product(*alphaprime)

    # Set of comparable and incomparable rectangles
    comparable = comp(d)
    incomparable = list(set(alpha) - set(comparable))
    return incomparable


def E(d):
    # type: (int) -> list
    # Compressed version for a set of alpha indices representing incomparable rectangles
    if d == 3:
        return ["0*1", "10*", "*10"]
    elif d > 3:
        return ["*" + i for i in E(d - 1)] + ["0" + "1" * (d - 1), "1" + "0" * (d - 1)]


def incomp_compressed(d):
    # type: (int) -> list
    # Returns E(d) in alpha format
    lin = E(d)
    lout = []
    # Changes:
    # ["0*1", "10*", "*10"]
    # By:
    # ["021", "102", "210"]
    # And finally:
    # [(0, 2, 1), (1, 0, 2), (2, 1, 0)]
    for i in lin:
        lin_temp = i.replace("*", "2")
        alpha = tuple(int(li) for li in lin_temp)
        lout.append(alpha)
    return lout


def incomp(d, opt=True):
    # type: (int, bool) -> list
    # # Set of incomparable rectangles
    if opt and d >= 3:
        return incomp_compressed(d)
    else:
        return incomp_expanded(d)


#################
# Cube generators
#################
def cpoint(i, alphai, ypoint, xspace):
    # type: (int, int, tuple, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        # result_xspace.max_corner[i] = ypoint[i]
        result_xspace.max_corner = subt(i, xspace.max_corner, ypoint)
    elif alphai == 1:
        # result_xspace.min_corner[i] = ypoint[i]
        result_xspace.min_corner = subt(i, xspace.min_corner, ypoint)
    return result_xspace


def crect(i, alphai, yrectangle, xspace):
    # type: (int, int, Rectangle, Rectangle) -> Rectangle
    result_xspace = Rectangle(xspace.min_corner, xspace.max_corner)
    if alphai == 0:
        result_xspace = cpoint(i, alphai, yrectangle.max_corner, xspace)
    elif alphai == 1:
        result_xspace = cpoint(i, alphai, yrectangle.min_corner, xspace)
    return result_xspace


#########################################################################################
def bpoint(alpha, ypoint, xspace):
    # type: (tuple, tuple, Rectangle) -> Rectangle
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(ypoint)), \
        'xspace.min_corner and xpoint do not share the same dimension'
    # assert (dim(ypoint.max_corner) == dim(ypoint)), \
    #    'xspace.max_corner and ypoint do not share the same dimension'
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp = cpoint(i, alphai, ypoint, temp)
    return temp


def brect(alpha, yrectangle, xspace):
    # type: (tuple, Rectangle, Rectangle) -> Rectangle
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    assert (dim(alpha) == dim(yrectangle.min_corner)), \
        'alpha and xrectangle.min_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(yrectangle.min_corner)), \
        'xspace.min_corner and xrectangle.min_corner do not share the same dimension'
    # assert (dim(xspace.max_corner) == dim(yrectangle.max_corner)), \
    #    'xspace.max_corner and yrectangle.max_corner do not share the same dimension'
    temp = Rectangle(xspace.min_corner, xspace.max_corner)
    for i, alphai in enumerate(alpha):
        temp = crect(i, alphai, yrectangle, temp)
    return temp


#########################################################################################
def irect(alphaincomp, yrectangle, xspace):
    # type: (list, Rectangle, Rectangle) -> list
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    'alphaincomp_list and yrectangle.min_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    'alphaincomp_list and yrectangle.max_corner do not share the same dimension'
    return [brect(alphaincomp_i, yrectangle, xspace) for alphaincomp_i in alphaincomp]
