# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Segment.

This module introduces the Segment class. It includes a set of
operations for creating and handling segments, i.e., intervals
between two Cartesian points. For instance, the diagonal of a
Rectangle is considered as a Segment object.

This class is used for storing the result of a binary search
over the diagonal of a Rectangle, i.e., the interval where a
Pareto point is located.
"""

import math
import cython

from ParetoLib.Geometry.Point import maxi, mini, greater_equal, less_equal, div, mult, add, r
import ParetoLib.Geometry.Point as Point


@cython.cclass
class Segment(object):

    low = cython.declare(tuple, visibility='public')
    high = cython.declare(tuple, visibility='public')
    # cython.declare(low=tuple, high=tuple)

    @cython.locals(low=tuple, high=tuple)
    @cython.returns(cython.void)
    def __init__(self, low, high):
        # type: (Segment, tuple, tuple) -> None
        """
        A Segment is represented by a couple of Points (i.e., tuples)
        named self.low and self.high.

        Given two input Points, the attribute self.low contains
        the smallest one and self.high the greatest one.

        Points are stored as tuples of float numbers, which are
        automatically rounded to the maximal decimal precision
        specified by ParetoLib.Geometry.__numdigits__

        By using Segments as intermediate elements for initializing
        Rectangles, we guarantee that arithmetic issues caused by
        decimal precision are removed.

        Args:
            self (Segment): A Segment.
            low (tuple): A point.
            high (tuple): Another point.

        Returns:
            None

        Example:
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 7)
        >>> s = Segment(x, y)
        """

        self.low = mini(low, high)
        self.high = maxi(low, high)
        assert Point.dim(self.low) == Point.dim(self.high)
        assert greater_equal(self.high, self.low)

    # Membership function
    @cython.locals(xpoint=tuple)
    @cython.returns(cython.bint)
    def __contains__(self, xpoint):
        # type: (Segment, tuple) -> bool
        """
        Membership function that checks if a Point is located
        inside a Segment.

        Args:
            self (Segment): A Segment.
            xpoint (tuple): A point.

        Returns:
            bool: True if xpoint is inside the interval
            [self.low, self.high].

        Example:
        >>> p = (2, 4, 7)
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 8)
        >>> s = Segment(x, y)
        >>> p in s
        >>> True
        """
        return (greater_equal(xpoint, self.low) and
                less_equal(xpoint, self.high))

    # Legacy code __setattr__: used for rounding floating tuples when assigning them to .low/.high attributes
    # @cython.locals(name=str)
    # @cython.returns(cython.void)
    # def __setattr__(self, name, value):
    #     # type: (Segment, str, iter) -> None
    #     """
    #     Assignation of a value to a class attribute.
    #
    #     Args:
    #         self (Segment): The Segment.
    #         name (str): The attribute.
    #         value (None): The value
    #
    #     Returns:
    #         None: self.name = value.
    #
    #     Example:
    #     >>> x = (2, 4, 6)
    #     >>> y = (2, 4, 7)
    #     >>> s = Segment(x, y)
    #     >>> s.high = y
    #     """
    #     # Round the elements of 'value' when assigning them to self.low or self.high
    #     # value = tuple(r(vi) for vi in value)
    #     # self.__dict__[name] = val
    #     object.__setattr__(self, name, value)

    @cython.cfunc
    @cython.locals(_string=str)
    @cython.returns(str)
    def _to_str(self):
        # type: (Segment) -> str
        """
        Printer.
        """
        _string = '<{0}, {1}>'.format(self.low, self.high)
        return _string

    @cython.returns(str)
    def __repr__(self):
        # type: (Segment) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def __str__(self):
        # type: (Segment) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(cython.bint)
    def __eq__(self, other):
        # type: (Segment) -> bool
        """
        self == other
        """
        return (other.low == self.low) and (other.high == self.high)

    @cython.returns(cython.bint)
    def __ne__(self, other):
        # type: (Segment) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    @cython.returns(int)
    def __hash__(self):
        # type: (Segment) -> int
        """
        Identity function (via hashing).
        """
        return hash((self.low, self.high))

    # Segment properties
    @cython.ccall
    @cython.returns(cython.ushort)
    def dim(self):
        # type: (Segment) -> int
        """
        Dimension of the points stored in a Segment.

        Args:
            self (Segment): A Segment.

        Returns:
            int: len(self.low).

        Example:
        >>> x = (2, 4, 6)
        >>> y = (2, 4, 7)
        >>> s = Segment(x, y)
        >>> s.dim()
        >>> 3
        """
        return Point.dim(self.low)

    @cython.ccall
    @cython.returns(tuple)
    def diag(self):
        # type: (Segment) -> tuple
        """
        Diagonal of the Segment, i.e., vector going from the
        lower corner to the higher corner.

        Args:
            self (Segment): A Segment.

        Returns:
            tuple: substract(self.high, self.low).

        Example:
        >>> x = (0, 1, 2)
        >>> y = (3, 4, 5)
        >>> s = Segment(x, y)
        >>> s.diag()
        >>> (3.0, 3.0, 3.0)
        """
        return Point.subtract(self.high, self.low)

    @cython.ccall
    @cython.locals(diagonal=tuple)
    @cython.returns(cython.double)
    def norm(self):
        # type: (Segment) -> float
        """
        Norm of the Segment.diag().

        Args:
            self (Segment): A Segment.

        Returns:
            float: norm(self.diag()).

        Example:
        >>> x = (0, 1, 2)
        >>> y = (3, 4, 5)
        >>> s = Segment(x, y)
        >>> s.norm()
        >>> 5.196
        """
        diagonal = self.diag()
        return Point.norm(diagonal)

    @cython.ccall
    @cython.locals(offset=tuple, eps=cython.double)
    @cython.returns(tuple)
    def center_eps(self, eps):
        # type: (Segment, float) -> tuple
        """
        off by eps from the center of the Segment.

        Args:
            self (Segment): The Segment,
            eps: a float value.

        Returns:
            tuple: eps-center of the Segment.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> s = Segment(x,y)
        >>> s.center_eps(0.01)
        >>> (0.51,0.51)
        """
        offset = mult(self.diag(), eps)
        return add(self.center(), offset)

    @cython.ccall
    @cython.locals(offset=tuple)
    @cython.returns(tuple)
    def center(self):
        # type: (Segment) -> tuple
        """
        Center of the Segment.

        Args:
            self (Segment): The Segment.

        Returns:
            tuple: Center of the Segment.

        Example:
        >>> x = (0,0)
        >>> y = (1,1)
        >>> s = Segment(x,y)
        >>> s.center()
        >>> (0.5,0.5)
        """
        offset = div(self.diag(), 2.0)
        return add(self.low, offset)

    #@cython.ccall
    #@cython.locals(offset=tuple)
    @cython.returns(tuple)
    def center_round(self):
        # type: (Segment) -> tuple
        """
        Center of the Segment.

        Args:
            self (Segment): The Segment.

        Returns:
            tuple: rounded center of the Segment.

        Example:
        >>> x = (0,0)
        >>> y = (3,3)
        >>> s = Segment(x,y)
        >>> s.center_round()
        >>> (1, 1)
        """
        offset = div(self.diag(), 2.0)
        offset = tuple(math.floor(off_i) for off_i in offset)
        return add(self.low, offset)