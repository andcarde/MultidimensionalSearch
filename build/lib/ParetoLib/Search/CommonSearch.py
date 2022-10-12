# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""CommontSearch.

This module instantiate the abstract interface Oracle.
The OraclePoint defines the boundary between the upper and lower
closures based on a discrete cloud of points. The cloud of points is
saved in a NDTree [1], a data structure that is optimised for storing
a Pareto front by removing redundant non-dominating points from the
surface. A point x that dominates every member of the Pareto front
belongs to the lower part of the monotone partition, while a point x
that is dominated by any element of the Pareto front will fall in the
upper part.

[1] Andrzej Jaszkiewicz and Thibaut Lust. ND-Tree-based update: a
fast algorithm for the dynamic non-dominance problem. IEEE Trans-
actions on Evolutionary Computation, 2018.
"""
import cython

from ParetoLib.Geometry.Point import add, subtract, less_equal, div
from ParetoLib.Geometry.Segment import Segment
import copy
from ParetoLib._py3k import max_integer_value

# EPS = sys.float_info.epsilon
# DELTA = sys.float_info.epsilon
# STEPS = 100

EPS = 1e-5
DELTA = 1e-5
STEPS = max_integer_value()  # float('inf')

P0 = 0.01
ALPHA = 0.05
NUMCELLS = 100

@cython.locals(x=object, error=tuple, i=cython.ushort, y=object, yval=tuple, dist=cython.double)
@cython.returns((object, cython.ushort))
def binary_search(x,
                  member,
                  error):
    # type: (Segment, callable, tuple) -> (Segment, int)
    i = 0
    y = x

    if member(y.low):
        # All the cube belongs to B1
        y.low = x.low
        y.high = x.low
    elif not member(y.high):
        # All the cube belongs to B0
        y.low = x.high
        y.high = x.high
    else:
        # We don't know. We search for a point in the diagonal
        # dist = subtract(y.high, y.low)
        dist = y.norm()
        # while not less_equal(dist, error):
        while dist > error[0]:
            i += 1
            # yval = div(add(y.low, y.high), 2.0)
            yval = y.center()
            # We need a oracle() for guiding the search
            if member(yval):
                y.high = yval
            else:
                y.low = yval
            # dist = subtract(y.high, y.low)
            dist = y.norm()
    return y, i


# No intersection: -2
# There exists an intersection: +1
# Don't know: -1
# The whole search space is in the intersection: 2
# There can be no intersection in the whole of the search space: -3
(INTERFULL, INTER, DKNOW, NO_INTER, INTERNULL) = (2, 1, -1, -2, -3)

@cython.locals(y1=object, y2=object)
@cython.returns((object, cython.short))
def determine_intersection(y1, y2):
    # type: (Segment, Segment) -> (Segment, int)
    if y2.high <= y1.low:
        return Segment(y1.high, y1.low), NO_INTER
    elif y1.high <= y2.low:
        return Segment(y1.high, y2.low), INTER
    else:
        return Segment(y1.low, y2.high), DKNOW


@cython.locals(x=object, list_constraints=list, low_allowed=cython.bint, high_allowed=cython.bint, #constraint=iter,
               left_sum=int, i=cython.ushort)
@cython.returns(cython.bint)
def intersection_empty_constrained(x, member1, member2, list_constraints):
    # type: (Segment, callable, callable, list) -> bool
    low_allowed = True
    high_allowed = True
    for constraint in list_constraints:
        left_sum = 0
        for i in range(len(x.low)):
            left_sum += x.low[i] * constraint[i]
        if left_sum > constraint[-1]:
            low_allowed = False
            break
        left_sum = 0
        for i in range(len(x.high)):
            left_sum += x.high[i] * constraint[i]
        if left_sum > constraint[-1]:
            high_allowed = False
            break

    return (low_allowed and not member2(x.low)) or \
           (high_allowed and not member1(x.high))


@cython.locals(x=object)
@cython.returns(cython.bint)
def intersection_empty(x, member1, member2):
    # type: (Segment, callable, callable) -> bool
    # The cube doesn't contain an intersection.
    return (not member1(x.high)) or (not member2(x.low))


@cython.locals(x=object, y=object, z=object, error=tuple, to_expand=cython.bint,
               i=cython.ushort, i1=cython.ushort, i2=cython.ushort,
               zgrek1=object, zgrek2=object, ygrek=object,
               intersect_indicator=cython.short, dist=cython.double, yval=tuple, result1=cython.bint,
               result2=cython.bint, yIn=object, yCover=object, eps_minus=tuple, eps_plus=tuple)
@cython.returns((object, object, cython.short, cython.ushort))
def intersection_expansion_search(x,
                                  member1, member2,
                                  error, to_expand):
    # type: (Segment, callable, callable, tuple, bool) -> (Segment, Segment, int, int)
    # member1 is the function whose truth value increases with x.
    # member2 is the function whose truth value decreases with x.

    # Try to find an intersection or a proof that there doesn't exist an intersection on the given segment.
    i = 0
    y = x
    intersect_indicator = DKNOW
    if member1(y.low) and member2(y.high):
        # All the cube belongs to B1
        intersect_indicator = INTERFULL
    elif (not member1(y.high)) or (not member2(y.low)):
        # All the cube belongs to B0
        y.low = x.high
        y.high = x.high
        intersect_indicator = INTERNULL
    else:
        # We don't know. We search for a point in the diagonal
        # dist = subtract(y.high, y.low)
        dist = y.norm()
        # while not less_equal(dist, error):
        while dist > error[0]:
            i += 2
            # yval = div(add(y.low, y.high), 2.0)
            yval = y.center()
            # We need a oracle() for guiding the search
            result1 = member1(yval)
            result2 = member2(yval)
            if result1 and result2:
                # assign
                z = copy.deepcopy(y)
                y.low = yval
                y.high = yval
                intersect_indicator = INTER
                break
            elif not (result1 or result2):
                # assign
                z = copy.deepcopy(y)
                y.low = yval
                y.high = yval
                intersect_indicator = NO_INTER
                break
            elif result1 and not result2:
                y.high = yval
            else:  # (not result1) and (result2)
                y.low = yval
            # dist = subtract(y.high, y.low)
            dist = y.norm()

    yIn = copy.deepcopy(y)
    yCover = copy.deepcopy(y)

    # Expansion step here.
    if intersect_indicator == NO_INTER and to_expand:
        eps_minus = z.center_eps(-error[0] / 2.0)
        eps_plus = z.center_eps(error[0] / 2.0)
        if not member2(eps_minus):
            # Try to expand on the lower side.
            zgrek1 = copy.deepcopy(z)
            zgrek1.high = eps_minus
            flip_member2 = lambda point: not member2(point)
            ygrek, i1 = binary_search(zgrek1, flip_member2, error)
            i += i1
            yCover.low = ygrek.low
            yIn.low = ygrek.high
        if not member1(eps_plus):
            # Try to expand on the upper side.
            zgrek2 = copy.deepcopy(z)
            zgrek2.low = eps_plus
            ygrek, i2 = binary_search(zgrek2, member1, error)
            i += i2
            yCover.high = ygrek.high
            yIn.high = ygrek.low
    elif intersect_indicator == INTER:
        eps_minus = z.center_eps(-error[0] / 2.0)
        eps_plus = z.center_eps(error[0] / 2.0)
        if member1(eps_minus):
            # Try to expand on the lower side.
            zgrek1 = copy.deepcopy(z)
            zgrek1.high = eps_minus
            ygrek, i1 = binary_search(zgrek1, member1, error)
            i += i1
            yCover.low = ygrek.low
            yIn.low = ygrek.high
        if member2(eps_plus):
            # Try to expand on the upper side.
            zgrek2 = copy.deepcopy(z)
            zgrek2.low = eps_plus
            flip_member2 = lambda point: not member2(point)
            ygrek, i2 = binary_search(zgrek2, flip_member2, error)
            i += i2
            yCover.high = ygrek.high
            yIn.high = ygrek.low

    return yIn, yCover, intersect_indicator, i
