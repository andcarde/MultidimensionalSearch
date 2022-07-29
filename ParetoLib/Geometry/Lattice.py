# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Lattice.

This module introduces the Lattice class. It includes a set of
operations for creating and handling partial ordered sets.
"""

from sortedcontainers import SortedSet
from operator import getitem
import cython


@cython.cclass
class Lattice(object):
    key = cython.declare(object)
    list_of_sets = cython.declare(list)

    # cython.declare(low=tuple, high=tuple)

    @cython.locals(dim=cython.ushort)
    @cython.returns(cython.void)
    def __init__(self,
                 dim,
                 key=lambda x: x):
        # type: (Lattice, int, callable) -> None
        assert dim > 0
        self.key = key
        # self.list_of_lists = [SortedSet([], key=lambda x, j=i: self.key(x)[j]) for i in range(dim)]
        self.list_of_sets = [SortedSet([], key=lambda x, j=i: getitem(self.key(x), j)) for i in range(dim)]

    @cython.returns(str)
    def _to_str(self):
        # type: (Lattice) -> str
        """
        Printer.
        """
        return str(self.list_of_sets)

    @cython.returns(str)
    def __repr__(self):
        # type: (Lattice) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(str)
    def __str__(self):
        # type: (Lattice) -> str
        """
        Printer.
        """
        return self._to_str()

    @cython.returns(cython.bint)
    def __eq__(self, other):
        # type: (Lattice, Lattice) -> bool
        """
        self == other
        """
        return (other.list_of_lists == self.list_of_sets) and (other.key == self.key)

    @cython.returns(cython.bint)
    def __ne__(self, other):
        # type: (Lattice, Lattice) -> bool
        """
        self != other
        """
        return not self.__eq__(other)

    @cython.returns(int)
    def __hash__(self):
        # type: (Lattice) -> int
        """
        Identity function (via hashing).
        """
        return hash((tuple(self.list_of_sets), self.key))

    @cython.returns(int)
    def __len__(self):
        # type: (Lattice) -> int
        """
        len(self)
        """
        s = self.get_elements()
        return len(s)

    # Lattice properties
    @cython.ccall
    @cython.returns(cython.ushort)
    def dim(self):
        # type: (Lattice) -> int
        """
        Dimension of the Lattice.

        Args:
            self (Lattice): The Lattice.

        Returns:
            int: Dimension of the Lattice.

        Example:
        >>> x = (0,0,0)
        >>> l = Lattice(len(x))
        >>> l.dim()
        >>> 3
        """
        return len(self.list_of_sets)

    def get_elements(self):
        # type: (Lattice) -> iter
        return self.list_of_sets[0]

    def add(self, elem):
        # type: (Lattice, object) -> None
        for l in self.list_of_sets:
            l.add(elem)

    def add_list(self, lst):
        # type: (Lattice, iter) -> None
        for l in self.list_of_sets:
            l |= lst

    def remove(self, elem):
        # type: (Lattice, object) -> None
        for l in self.list_of_sets:
            l.discard(elem)

    def remove_list(self, lst):
        # type: (Lattice, iter) -> None
        for l in self.list_of_sets:
            l -= lst

    def less(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i < elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_sets:
            index = l.bisect_left(elem)
            s = s.intersection(l[:index])
        return s

    def less_equal(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i <= elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_sets:
            index = l.bisect_right(elem)
            s = s.intersection(l[:index])
        return s

    def greater(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i > elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_sets:
            index = l.bisect_right(elem)
            s = s.intersection(l[index:])
        return s

    def greater_equal(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i >= elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_sets:
            index = l.bisect_left(elem)
            s = s.intersection(l[index:])
        return s

    def equal(self, elem):
        # type: (Lattice, object) -> set
        """
        Elements 'x' of the Lattice having x_i == elem_i for all i with i in [1, dim(elem)].
        """
        s = self.get_elements()
        for l in self.list_of_sets:
            index1 = l.bisect_left(elem)
            index2 = l.bisect_right(elem)
            s = s.intersection(l[index1:index2])
        return s
