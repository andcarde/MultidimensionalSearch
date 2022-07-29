# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""PPoint.

This module introduces a set of operations for managing
Cartesian points in n-dimensional spaces as vectors (i.e., tuples)
of n components.

This package uses external calls to Numpy library for
optimising vector operations.
"""

import numpy as np
from numpy import linalg as la
from numpy import array as point
import cython

import ParetoLib.Geometry
from ParetoLib._py3k import red


# Auxiliary functions for computing the algebraic properties
# of a vector (e.g., norm, distance, etc.)

@cython.ccall
@cython.returns(cython.double)
@cython.locals(i=cython.double)
def r(i):
    # type: (float) -> float
    """
    Rounds a float number with n decimals to a float number
    with m decimals, where m is the maximum arithmetic precision
    supported by our tool.

    The maximum number of decimals supported by our tool is
    specified by the following variable:

    ParetoLib.Geometry.__numdigits__

    Args:
        i (float): A float number.

    Returns:
        float: round(i).

    Example:
    >>> i = 0.500...01
    >>> r(i)
    >>> 0.5
    """
    return round(i, ParetoLib.Geometry.__numdigits__)

@cython.ccall
@cython.returns(cython.ushort)
def dim(x):
    # type: (point) -> int
    """
    Dimension of a Cartesian point.

    Args:
        x (point): A Cartesian point.

    Returns:
        int: len(x).

    Example:
    >>> x = (2, 4, 6)
    >>> dim(x)
    >>> 3
    """
    return len(x)

@cython.returns(cython.double)
def norm(x):
    # type: (point) -> float
    """
    Norm of a vector.

    Args:
        x (point): A vector.

    Returns:
        float: sqrt(sum(x[i]**2)) for i = 0..dim(x)-1.

    Example:
    >>> x = (2, 4, 6)
    >>> norm(x)
    >>> 7.48
    """
    return la.norm(x)

@cython.ccall
@cython.returns(cython.double)
def distance(x, xprime):
    # type: (point, point) -> float
    """
    Euclidean distance between two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        float: norm(x - xprime).

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> distance(x, xprime)
    >>> 7.48
    """
    temp = subtract(x, xprime)
    return norm(temp)


@cython.returns(cython.double)
@cython.locals(_sum=cython.double)
def hamming_distance(x, xprime):
    # type: (point, point) -> float
    """
    Hamming distance between two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        float: sum(x[i] - xprime[i]) for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> distance(x, xprime)
    >>> 12.0
    """
    temp = subtract(x, xprime)
    _sum = red(lambda si, sj: abs(si) + abs(sj), temp)
    return _sum


# Arithmetic operations between two Cartesian points or between
# a Cartesian point and a scale factor.

def subtract(x, xprime):
    # type: (point, point) -> point
    """
    Component wise subtraction of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        point: x[i] - xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> subtract(x, xprime)
    >>> (2, 4, 6)
    """
    return x - xprime


def add(x, xprime):
    # type: (point, point) -> point
    """
    Component wise addition of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        point: x[i] + xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> add(x, xprime)
    >>> (8, 8, 8)
    """
    return x + xprime


# Cythonizing 'mult' produce (0.0, ..., 0.0) as output, even though i != 0
# @cython.returns(tuple)
@cython.locals(i=cython.double)
def mult(x, i):
    # type: (point, float) -> point
    """
    Multiplication of a Cartesian point by a scale factor.

    Args:
        x (point): A Cartesian point.
        i (float): The scale factor.

    Returns:
        point: x[j]*i for j = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> i = 2.0
    >>> mult(x, i)
    >>> (10.0, 12.0, 14.0)
    """
    return x * i


# Cythonizing 'div' produce 'Division by zero' error, even though i != 0
# @cython.returns(tuple)
# @cython.locals(i=cython.double)
def div(x, i):
    # type: (point, float) -> point
    """
    Division of a Cartesian point by a scale factor.

    Args:
        x (point): A Cartesian point.
        i (float): The scale factor.

    Returns:
        point: x[j]/i for j = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> i = 2.0
    >>> div(x, i)
    >>> (2.5, 3.0, 3.5)
    """
    return x / i


# Comparison of two points
@cython.returns(cython.bint)
def greater(x, xprime):
    # type: (point, point) -> bool
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        bool: x[i] > xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> greater(x, xprime)
    >>> True
    """
    return all(x > xprime)


@cython.returns(cython.bint)
def greater_equal(x, xprime):
    # type: (point, point) -> bool
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        bool: x[i] >= xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> greater_equal(x, xprime)
    >>> True
    """
    return all(x >= xprime)


@cython.returns(cython.bint)
def less(x, xprime):
    # type: (point, point) -> bool
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        bool: x[i] < xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> less(x, xprime)
    >>> False
    """
    return all(x < xprime)


@cython.returns(cython.bint)
def less_equal(x, xprime):
    # type: (point, point) -> bool
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        bool: x[i] <= xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> less_equal(x, xprime)
    >>> False
    """
    return all(x <= xprime)


@cython.ccall
@cython.returns(cython.bint)
def equal(x, xprime):
    # type: (point, point) -> bool
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        bool: x[i] == xprime[i] for i = 0..dim(x)-1.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> equal(x, xprime)
    >>> False
    """
    return all(x == xprime)


@cython.ccall
@cython.returns(cython.bint)
def incomparables(x, xprime):
    # type: (point, point) -> bool
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        bool: (not greater_equal(x, xprime)) and
              (not greater_equal(xprime, x))

        Equivalently,
        for i = 0..j-1,j+1..dim(x)-1: x[i] <= xprime[i]
        and for some j: x[j] > xprime[j].

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 8, 1)
    >>> incomparables(x, xprime)
    >>> True
    """

    return (not greater_equal(x, xprime)) and (not greater_equal(xprime, x))


def maxi(x, xprime):
    # type: (point, point) -> point
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        point: x if x[i] > xprime[i] for i = 0..dim(x)-1, else xprime.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> maxi(x, xprime)
    >>> (5, 6, 7)
    """
    if greater_equal(x, xprime):
        return x
    else:
        return xprime


def mini(x, xprime):
    # type: (point, point) -> point
    """
    Component wise comparison of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        point: x if x[i] < xprime[i] for i = 0..dim(x)-1, else xprime.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (3, 2, 1)
    >>> mini(x, xprime)
    >>> (3, 2, 1)
    """
    if less_equal(x, xprime):
        return x
    else:
        return xprime


def maximum(x, xprime):
    # type: (point, point) -> point
    """
    Component wise maximum of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        point: max(x[i], xprime[i]) for i = 0..dim(x)-1

    Example:
    >>> x = (1, 2, 3)
    >>> xprime = (3, 2, 1)
    >>> maximum(x, xprime)
    >>> (3, 2, 3)
    """
    return np.maximum(x, xprime)


def minimum(x, xprime):
    # type: (point, point) -> point
    """
    Component wise minimum of two Cartesian points.

    Args:
        x (point): The first point.
        xprime (point): The second point.

    Returns:
        point: min(x[i], xprime[i]) for i = 0..dim(x)-1

    Example:
    >>> x = (1, 2, 3)
    >>> xprime = (3, 2, 1)
    >>> minimum(x, xprime)
    >>> (1, 2, 1)
    """
    return np.minimum(x, xprime)


@cython.ccall
@cython.locals(i=cython.ushort,
               n=cython.ushort, m=cython.ushort)
def subt(i, x, xprime):
    # type: (int, point, point) -> point
    """
    Substitution of the i-th component of a Cartesian point
    by the i-th component of another Cartesian point.

    Args:
        i (int): Index
        x (point): The first point.
        xprime (point): The second point.

    Return:
        point: (x[0],...,x[i-1], xprime[i], x[i+1],..., x[dim(x)-1]).

    Example:
    >>> i = 3
    >>> x = (5, 6, 7)
    >>> xprime = (0, 0, 1)
    >>> subt(i, x, xprime)
    >>> (5, 6, 1)
    """
    n = len(x)
    m = len(xprime)
    assert ((0 <= i) and (i < n) and (i < m)), 'index out of range'
    out = point(x)
    out[i] = xprime[i]
    return out


@cython.locals(n=cython.ushort, m=cython.ushort)
def select(x, xprime):
    # type: (point, point) -> point
    """
    Selection of components from a Cartesian point
    according to an index vector.

    Args:
        x (point): A Cartesian point.
        xprime (point): An index vector.

    Return:
        point: Components of x selected by xprime.

    Example:
    >>> x = (5, 6, 7)
    >>> xprime = (0, 0, 1)
    >>> select(x, xprime)
    >>> (0, 0, 7)
    """
    n = len(x)
    m = len(xprime)
    assert (n == m), 'index out of range'
    return x * xprime


# Integer to binary notation
@cython.ccall
@cython.returns(list)
@cython.locals(x=cython.ulonglong, pad=cython.ushort, pad_temp=cython.ushort, i=str, temp1=list, temp2=list)
def int_to_bin_list(x, pad=0):
    # type: (int, int) -> list
    """
    Conversion of a integer number to binary notation.
    The result is stored as a list of digits [0,1].
    Args:
        x (int): A Cartesian point.
        pad (int): Length of the result list.
                   By default, 0 (i.e., no need of padding).

    Return:
        list: Representation of x as a list of binary digits.

    Example:
    >>> x = 4
    >>> int_to_bin_list(x, 0)
    >>> [1, 0, 0]
    >>> int_to_bin_list(x, 4)
    >>> [0, 1, 0, 0]
    """
    temp1 = [int(i) for i in bin(x)[2:]]
    pad_temp = pad if pad > 0 else len(temp1)
    temp2 = [0] * (pad_temp - len(temp1)) + temp1
    return temp2


@cython.ccall
@cython.locals(x=cython.ulonglong, pad=cython.ushort)
def int_to_bin_tuple(x, pad=0):
    # type: (int, int) -> point
    """ Equivalent to int_to_bin_list(x, pad=0).
    Returns a point instead of a list.

    Args:
        x (int): A Cartesian point.
        pad (int): Length of the result list.
                   By default, 0 (i.e., no need of padding).

    Return:
        point: Representation of x as a point of binary digits.

    Example:
    >>> x = 4
    >>> int_to_bin_tuple(x, 0)
    >>> (1, 0, 0)
    >>> int_to_bin_tuple(x, 4)
    >>> (0, 1, 0, 0)
    """
    return tuple(int_to_bin_list(x, pad))


# Domination
@cython.ccall
@cython.returns(cython.bint)
def dominates(x, xprime):
    # type: (point, point) -> bool
    """
    Synonym of less_equal(x, xprime).
    """
    return less_equal(x, xprime)


@cython.ccall
@cython.returns(cython.bint)
def is_dominated(x, xprime):
    # type: (point, point) -> bool
    """
    Synonym of less_equal(xprime, x).
    """
    return less_equal(xprime, x)
