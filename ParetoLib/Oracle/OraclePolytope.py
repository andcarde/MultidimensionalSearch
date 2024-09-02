import cython

# import ParetoLib.Oracle as RootOracle
import ParetoLib.Oracle
from ParetoLib.Oracle.Oracle import Oracle

RootOracle = ParetoLib.Oracle


# @cython.cclass
class OracleMonotonicPolytope(Oracle):
    """
    A generic class for expressing a monotonic (increasing or decreasing) polytope.
    """
    cython.declare(constraints=list)

    @cython.locals(constraints=list, cons=tuple, d=cython.uint)
    @cython.returns(cython.void)
    def __init__(self, constraints):
        # type: (OracleMonotonicPolytope, list) -> None

        Oracle.__init__(self)

        # Constraints is a list of tuples with the same dimension:
        # constraints = [cons_1, cons_2, ..., cons_n]
        # p1 + p2 + 3*p3 <= 8
        # cons_1 = (1, 1, 3, 8)

        cons = constraints[0]
        d = len(cons)

        # Check if the constraints are all of same dimension
        assert all(len(cons) == d for cons in constraints), "All constraints need to have the same dimension!!!"

        # Check if all the coefficients are non-negative
        assert all(ci >= 0 for cons in constraints for ci in cons), "Coefficients should be non-negatives!!!"

        self.constraints = constraints

    @cython.returns(cython.int)
    def dim(self):
        # type: (OracleMonotonicPolytope) -> int
        """
        See Oracle.dim().
        """
        if len(self.constraints) != 0:
            return len(self.constraints[0]) - 1
        else:
            return -1


# @cython.cclass
class OracleIncreasingPolytope(OracleMonotonicPolytope):
    @cython.locals(point=tuple, res=bool, addition=cython.int)
    @cython.returns(cython.bint)
    def member(self, point):
        # type: (OracleIncreasingPolytope, tuple) -> bool
        """
        Checks if a given point is located inside an increasing polytope.
        Example:
        >>> constraints = [(1,2,3,8),(5,4,7,10)]
        >>> # point is p.
        >>> p = (1,1,2)
        >>> return (1*p[0] + 2*p[1] + 3*p[2] >= 8) and (5*p[0] + 4*p[1] + 7*p[2] >= 10)
        """

        # d = len(point)
        # d + 1 == len(cons)

        res = True
        for cons in self.constraints:
            pair = zip(cons, point)
            addition = sum(cons_i * point_i for (cons_i, point_i) in pair)

            # Last item of the cons tuple represents the boundary
            res = res and (addition >= cons[-1])
        return res


# @cython.cclass
class OracleDecreasingPolytope(OracleMonotonicPolytope):
    @cython.locals(point=tuple, res=bool, addition=cython.int)
    @cython.returns(cython.bint)
    def member(self, point):
        # type: (OracleDecreasingPolytope, tuple) -> bool
        """
        Checks if a given point is located inside an increasing polytope.
        Example:
        >>> constraints = [(1,2,3,8),(5,4,7,10)]
        >>> # point is p.
        >>> p = (1,1,2)
        >>> return (1*p[0] + 2*p[1] + 3*p[2] <= 8) and (5*p[0] + 4*p[1] + 7*p[2] <= 10)
        """

        # d = len(point)
        # d + 1 == len(cons)

        res = True
        for cons in self.constraints:
            pair = zip(cons, point)
            addition = sum(cons_i * point_i for (cons_i, point_i) in pair)

            # Last item of the cons tuple represents the boundary
            res = res and (addition <= cons[-1])
        return res
