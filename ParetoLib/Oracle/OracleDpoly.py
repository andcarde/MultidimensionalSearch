# -*- coding: utf-8 -*-
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleDpoly.

This function checks if a given point is located inside a decreasing
polytope.
Example:
constraints = [(1,2,3,8),(5,4,7,10)]
point is p.
Checks if: (1*p[0]+2*p[1]+3*p[2]<=8) and (5*p[0]+4*p[1]+7*p[2]<=10)
"""
from ParetoLib.Oracle.Oracle import Oracle


class OracleDpoly(Oracle):
    def __init__(self, constraints):
        # type: (OracleDpoly, list) -> None

        # super(OracleDpoly, self).__init__()
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
        assert all(ci > 0 for cons in constraints for ci in cons), "Coefficients should be non-negatives!!!"

        self.constraints = constraints

    def member(self, point):
        # type: (OracleDpoly, tuple) -> bool
        """
        See Oracle.member().
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

    def dim(self):
        # type: (OracleDpoly) -> int
        """
        See Oracle.dim().
        """
        if len(self.constraints) != 0:
            return len(self.constraints[0])-1
        else:
            return -1
