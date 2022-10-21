# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""OraclePoint.

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

import sys
import resource
import io
import pickle
import cython

from ParetoLib.Oracle.NDTree import NDTree
from ParetoLib.Oracle.Oracle import Oracle


# @cython.cclass
class OraclePoint(Oracle):
    cython.declare(oracle=object)

    @cython.locals(max_points=cython.ulong, min_children=cython.ushort)
    @cython.returns(cython.void)
    def __init__(self, max_points=2, min_children=2):
        # type: (OraclePoint, int, int) -> None
        # super(OraclePoint, self).__init__()
        Oracle.__init__(self)
        self.oracle = NDTree(max_points=max_points, min_children=min_children)

    # Printers
    @cython.returns(str)
    def __repr__(self):
        # type: (OraclePoint) -> str
        return self._to_str()

    @cython.returns(str)
    def __str__(self):
        # type: (OraclePoint) -> str
        return self._to_str()

    @cython.returns(str)
    def _to_str(self):
        # type: (OraclePoint) -> str
        return str(self.oracle)

    # Equality functions
    def __eq__(self, other):
        # type: (OraclePoint, OraclePoint) -> bool
        return self.oracle == other.oracle

    @cython.returns(cython.bint)
    def __ne__(self, other):
        # type: (OraclePoint, OraclePoint) -> bool
        return not self.__eq__(other)

    # Identity function (via hashing)
    @cython.returns(int)
    def __hash__(self):
        # type: (OraclePoint) -> int
        return hash(self.oracle)

    # Oracle operations
    @cython.locals(p=tuple)
    @cython.returns(cython.void)
    def add_point(self, p):
        # type: (OraclePoint, tuple) -> None
        """
        Addition of a new Point to the OraclePoint.

        Args:
            self (OraclePoint): The OraclePoint.
            p (tuple): The point.

        Returns:
            None: The point is added to OraclePoint

        Example:
        >>> x = (0,0,0)
        >>> ora = OraclePoint()
        >>> ora.add_point(x)
        """
        self.oracle.update_point(p)

    @cython.locals(setpoints=set, point=tuple)
    @cython.returns(cython.void)
    def add_points(self, setpoints):
        # type: (OraclePoint, set) -> None
        """
        Addition of a set of Point to the OraclePoint.

        Args:
            self (OraclePoint): The OraclePoint.
            setpoints (set): The set of points.

        Returns:
            None: The set of points is added to OraclePoint

        Example:
        >>> xset = {(0,0,0), (1,1,1)}
        >>> ora = OraclePoint()
        >>> ora.add_points(xset)
        """
        for point in setpoints:
            self.add_point(point)

    @cython.returns(set)
    def get_points(self):
        # type: (OraclePoint) -> set
        """
        Extraction of the set of points stored in the OraclePoint.

        Args:
            self (OraclePoint): The OraclePoint.
            setpoints (set): The set of points.

        Returns:
            None: The set of points is added to OraclePoint

        Example:
        >>> xset = {(0,0,0), (1,1,1)}
        >>> ora = OraclePoint()
        >>> ora.add_points(xset)
        >>> ora.get_points(()
        """
        return self.oracle.get_points()

    @cython.returns(cython.ushort)
    def dim(self):
        # type: (OraclePoint) -> int
        """
        Dimension of the space where the OraclePoint is working on.

        Args:
            self (OraclePoint): The OraclePoint.

        Returns:
            int: Dimension of the space.

        Example:
        >>> ora = OraclePoint()
        >>> ora.from_file("3d_space.txt")
        >>> ora.dim()
        >>> 3
        """
        return self.oracle.dim()

    @cython.returns(list)
    def get_var_names(self):
        # type: (OraclePoint) -> list
        """
        Name of the axes of the space where the OraclePoint is working on.

        Args:
            self (OraclePoint): The OraclePoint.

        Returns:
            list: List of names.

        Example:
        >>> ora = OraclePoint()
        >>> ora.from_file('3d_space.txt')
        >>> ora.get_var_names()
        >>> ['x', 'y', 'z']
        """
        # super(OraclePoint, self).get_var_names()
        return Oracle.get_var_names(self)

    # Membership functions
    @cython.returns(cython.bint)
    @cython.locals(p=tuple)
    def __contains__(self, p):
        # type: (OraclePoint, tuple) -> bool
        """
        Synonym of self.member(point)
        """
        # set_points = self.get_points()
        # return p in set_points
        return self.member(p)

    @cython.returns(cython.bint)
    @cython.locals(p=tuple)
    def member(self, p):
        # type: (OraclePoint, tuple) -> bool
        """
        Function answering whether a point belongs to the upward
        closure or not.

        Args:
            self (OraclePoint): The OraclePoint.
            point (tuple): The point of the space that we inspect.

        Returns:
            bool: True if the point belongs to the upward closure.

        Example:
        >>> x = (0.0, 0.0)
        >>> ora = OraclePoint()
        >>> ora.member(x)
        >>> False
        """
        # Returns 'True' if p belongs to the set of points stored in the Pareto archive
        return p in self.get_points()

    @cython.returns(object)
    def membership(self):
        # type: (OraclePoint) -> callable
        """
        Returns a function that answers membership queries.
        Later on, this function is used as input parameter of
        ParetoLib.Search algorithms for guiding the discovery of the
        Pareto front.

        Args:
            self (OraclePoint): The OraclePoint.

        Returns:
            callable: Function that answers whether a point belongs
                      to the upward closure or not.

        Example:
        >>> x = (0.0, 0.0)
        >>> ora = OraclePoint()
        >>> f = ora.membership()
        >>> f(x)
        >>> False
        """
        # Returns 'True' if p is dominated by any point stored in the Pareto archive
        return lambda p: self.oracle.dominates(p)

    # Read/Write file functions
    @cython.returns(cython.void)
    @cython.locals(finput=object)
    def from_file_binary(self, finput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        """
        Loading an OraclePoint from a binary file.

        Args:
            self (OraclePoint): The Oracle.
            finput (io.BinaryIO): The file where the OraclePoint is saved.

        Returns:
            None: The OraclePoint is loaded from finput.

        Example:
        >>> ora = OraclePoint()
        >>> infile = open('filename', 'rb')
        >>> ora.from_file_binary(infile)
        >>> infile.close()
        """
        assert (finput is not None), 'File object should not be null'
        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        self.oracle = pickle.load(finput)

    @cython.returns(cython.void)
    @cython.locals(point=tuple)
    def from_file_text(self, finput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        """
        Loading an OraclePoint from a text file.

        Args:
            self (OraclePoint): The OraclePoint.
            finput (io.BinaryIO): The file where the Oracle is saved.

        Returns:
            None: The OraclePoint is loaded from finput.

        Example:
        >>> ora = OraclePoint()
        >>> infile = open('filename', 'r')
        >>> ora.from_file_text(infile)
        >>> infile.close()
        """
        assert (finput is not None), 'File object should not be null'

        @cython.locals(inline=str)
        def _line2tuple(inline):
            # type: (str) -> tuple
            line = inline
            line = line.replace('(', '')
            line = line.replace(')', '')
            line = line.split(',')
            return tuple(float(pi) for pi in line)

        self.oracle = NDTree()

        point_list = (_line2tuple(line) for line in finput)
        for point in point_list:
            self.oracle.update_point(point)

    @cython.returns(cython.void)
    @cython.locals(foutput=object)
    def to_file_binary(self, foutput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        """
        Writing of an OraclePoint to a binary file.

        Args:
            self (OraclePoint): The Oracle.
            foutput (io.BinaryIO): The file where the OraclePoint will
                                   be saved.

        Returns:
            None: The Oracle is saved in foutput.

        Example:
        >>> ora = OraclePoint()
        >>> outfile = open('filename', 'wb')
        >>> ora.to_file_binary(outfile)
        >>> outfile.close()
        """
        assert (foutput is not None), 'File object should not be null'

        # Setting maximum recursion. It is required for the NDTree build
        # sys.getrecursionlimit()
        max_rec = 0x100000
        resource.setrlimit(resource.RLIMIT_STACK, [0x100 * max_rec, resource.RLIM_INFINITY])
        sys.setrecursionlimit(max_rec)

        pickle.dump(self.oracle, foutput, pickle.HIGHEST_PROTOCOL)

    @cython.returns(cython.void)
    @cython.locals(foutput=object)
    def to_file_text(self, foutput=None):
        # type: (OraclePoint, io.BinaryIO) -> None
        """
        Writing of an OraclePoint to a text file.

        Args:
            self (OraclePoint): The OraclePoint.
            foutput (io.BinaryIO): The file where the Oracle will
                                   be saved.

        Returns:
            None: The OraclePoint is saved in foutput.

        Example:
        >>> ora = OraclePoint()
        >>> outfile = open('filename', 'w')
        >>> ora.to_file_text(outfile)
        >>> outfile.close()
        """
        assert (foutput is not None), 'File object should not be null'

        setPoints = self.get_points()
        for point in setPoints:
            foutput.write(str(point))
            foutput.write('\n')
