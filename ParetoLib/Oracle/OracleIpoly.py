# -*- coding: utf-8 -*-
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OracleIpoly.

This function checks if a given point is located inside an increasing
polytope.
Example:
constraints = [(1,2,3,8),(5,4,7,10)]
point is p.
Checks if: (1*p[0]+2*p[1]+3*p[2]>=8) and (5*p[0]+4*p[1]+7*p[2]>=10)
"""
from ParetoLib.Oracle.Oracle import Oracle

class OracleIpoly(Oracle):
    def __init__(self, constraints):
        # type: (OracleIpoly, list) -> None

        # super(OracleIpoly, self).__init__()
        Oracle.__init__(self)

        # constraints is a list of tuples with the same dimension
        # First check if the constraints are all of same dimension
        d = 0
        for cons in constraints:
            if(d == 0):
                d = len(cons)
            else:
                if(len(cons)!=d):
                    # Throw error here
                    print("All constraints need to have the same dimension!!!")
                    exit(0)
        # Check if all the coefficients are non-negative
        for cons in constraints:
            for i in range(0,len(cons)-1):
                if(cons[i]<0):
                    print("Coefficients should be non-negatives!!!")
                    exit(0)

        self.constraints = constraints

    def member(self, point):
        # type: (OracleIpoly, tuple) -> bool
        """
        See Oracle.member().
        """
        res = True
        for cons in self.constraints:
            sum = 0
            for i in range(0,len(cons)-1):
                sum += cons[i]*point[i]
            res = res and (sum >= cons[-1])
        return res

    def dim(self):
        # type: (OracleIpoly) -> int
        """
        See Oracle.dim().
        """
        if (len(self.constraints)!= 0):
            return len(self.constraints[0])-1
        else:
            return -1