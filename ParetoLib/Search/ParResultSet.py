# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""ParResultSet.

The result of the discovery process of the Pareto front is saved in
an object of the *ResultSet* class. This object is a data structure
composed of three elements: the upper closure (*X1*), the lower
closure (*X2*), and the gap between X1 and X2 representing the
precision error of the learning process.
The size of this gap depends on the accuracy of the learning process,
which can be tuned by the EPS and DELTA parameters during the
invocation of the learning method.

The ResultSet class provides functions for:
- Testing the membership of a new point *y* to any of the closures.
- Plotting 2D and 3D spaces
- Exporting/Importing the results to text and binary files.
"""

from typing import Tuple, List
from multiprocessing import Pool, cpu_count
from itertools import combinations
from scipy.spatial.distance import directed_hausdorff as dhf
import cython

from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Geometry.ParRectangle import pvertices, pinside, pvol
from ParetoLib.Search.ResultSet import ResultSet


# @cython.cclass
class ParResultSet(ResultSet):
    p = cython.declare(object, visibility='public')

    @cython.locals(border=list, ylow=list, yup=list, xspace=object)
    @cython.returns(cython.void)
    def __init__(self, border=list(), ylow=list(), yup=list(), xspace=Rectangle()):
        # type: (ParResultSet, iter, iter, iter, Rectangle) -> None
        super(ParResultSet, self).__init__(border, ylow, yup, xspace)
        # ResultSet.__init__(self, border, ylow, yup, xspace)

    # Vertex functions
    # @cython.ccall
    @cython.locals(vertices_list=list, vertices=set)
    @cython.returns(set)
    def vertices_yup(self):
        # type: (ParResultSet) -> set
        p = Pool(cpu_count())

        # vertices_list = (rect.vertices() for rect in self.yup)
        vertices_list = p.map(pvertices, self.yup)
        vertices = set()
        vertices = vertices.union(*vertices_list)

        p.close()
        p.join()
        return vertices

    # @cython.ccall
    @cython.locals(vertices_list=list, vertices=set)
    @cython.returns(set)
    def vertices_ylow(self):
        # type: (ParResultSet) -> set
        p = Pool(cpu_count())

        # vertices_list = (rect.vertices() for rect in self.ylow)
        vertices_list = p.map(pvertices, self.ylow)
        vertices = set()
        vertices = vertices.union(*vertices_list)

        p.close()
        p.join()
        return vertices

    # @cython.ccall
    @cython.locals(vertices_list=list, vertices=set)
    @cython.returns(set)
    def vertices_border(self):
        # type: (ParResultSet) -> set
        p = Pool(cpu_count())

        # vertices_list = (rect.vertices() for rect in self.border)
        vertices_list = p.map(pvertices, self.border)
        vertices = set()
        vertices = vertices.union(*vertices_list)

        p.close()
        p.join()
        return vertices

    # Volume functions
    @cython.returns(cython.double)
    def _overlapping_volume(self, pairs_of_rect):
        # type: (ParResultSet, iter) -> float
        p = Pool(cpu_count())

        # remove pairs (recti, recti) from previous list
        # pairs_of_rect_filt = (pair for pair in pairs_of_rect if pair[0] != pair[1])
        # overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect_filt)
        overlapping_rect = (r1.intersection(r2) for (r1, r2) in pairs_of_rect if r1.overlaps(r2))
        vol_overlapping_rect = p.imap_unordered(pvol, overlapping_rect)

        p.close()
        p.join()
        return sum(vol_overlapping_rect)

    # @cython.ccall
    @cython.returns(cython.double)
    def overlapping_volume_yup(self):
        # type: (ParResultSet) -> float
        # self.yup_2D = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.yup, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    # @cython.ccall
    @cython.returns(cython.double)
    def overlapping_volume_ylow(self):
        # type: (ParResultSet) -> float
        # self.ylow_2D = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.ylow, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    # @cython.ccall
    @cython.returns(cython.double)
    def overlapping_volume_border(self):
        # type: (ParResultSet) -> float
        # self.border_2D = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        pairs_of_rect = combinations(self.border, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    # @cython.ccall
    @cython.returns(cython.double)
    @cython.locals(total_rectangles=list)
    def overlapping_volume_total(self):
        # type: (ParResultSet) -> float
        # total_rectangles = [rect1, rect2,..., rectn]
        # pairs_of_rect = [(rect1, rect1), (rect1, rect2),..., (rectn, rectn)]
        total_rectangles = []
        total_rectangles.extend(self.border)
        total_rectangles.extend(self.yup)
        total_rectangles.extend(self.ylow)
        pairs_of_rect = combinations(total_rectangles, 2)
        return self._overlapping_volume(pairs_of_rect)
        # return ParResultSet._overlapping_volume(pairs_of_rect)

    # @cython.ccall
    @cython.returns(cython.double)
    @cython.locals(vol_list=list)
    def volume_yup(self):
        # type: (ParResultSet) -> float
        p = Pool(cpu_count())

        vol_list = p.imap_unordered(pvol, self.yup)
        # vol_list = (rect.volume() for rect in self.yup)

        p.close()
        p.join()
        return sum(vol_list)

    # @cython.ccall
    @cython.returns(cython.double)
    @cython.locals(vol_list=list)
    def volume_ylow(self):
        # type: (ParResultSet) -> float
        p = Pool(cpu_count())

        vol_list = p.imap_unordered(pvol, self.ylow)
        # vol_list = (rect.volume() for rect in self.ylow)

        p.close()
        p.join()
        return sum(vol_list)

    # @cython.ccall
    @cython.returns(cython.double)
    @cython.locals(vol_list=list)
    def volume_border_2(self):
        # type: (ParResultSet) -> float
        p = Pool(cpu_count())

        vol_list = p.imap_unordered(pvol, self.border)
        # vol_list = (rect.volume() for rect in self.border)

        p.close()
        p.join()
        return sum(vol_list) - self.overlapping_volume_total()

    # Membership functions
    @cython.returns(cython.bint)
    @cython.locals(isMember=list)
    def member_yup(self, xpoint):
        # type: (ParResultSet, tuple) -> bool
        p = Pool(cpu_count())

        # isMember = (rect.inside(xpoint) for rect in self.yup)
        args_member = ((rect, xpoint) for rect in self.yup)
        isMember = p.imap_unordered(pinside, args_member)

        p.close()
        p.join()
        return any(isMember)
        # return any(isMember) and not self.member_border(xpoint)

    @cython.returns(cython.bint)
    @cython.locals(isMember=list)
    def member_ylow(self, xpoint):
        # type: (ParResultSet, tuple) -> bool
        p = Pool(cpu_count())

        # isMember = (rect.inside(xpoint) for rect in self.ylow)
        args_member = ((rect, xpoint) for rect in self.ylow)
        isMember = p.imap_unordered(pinside, args_member)

        p.close()
        p.join()
        return any(isMember)
        # return any(isMember) and not self.member_border(xpoint)

    # @cython.ccall
    @cython.returns(cython.bint)
    @cython.locals(xpoint=tuple)
    def member_border(self, xpoint):
        # type: (ParResultSet, tuple) -> bool
        # isMember = (rect.inside(xpoint) for rect in self.border)
        # args_member = ((rect, xpoint) for rect in self.border)
        # p = Pool(cpu_count())
        # isMember = p.imap_unordered(pinside, args_member)
        # p.close()
        # p.join()
        # return any(isMember)
        return self.member_space(xpoint) and not self.member_yup(xpoint) and not self.member_ylow(xpoint)


@cython.locals(args=tuple, rs_list=list, rs=object, intersection=int)
def par_haussdorf_distance(args):
    # type: (Tuple[ResultSet, List[ResultSet]]) -> Tuple[float]
    current_rs, rs_list, intersection = args
    if intersection == 0:
        return current_rs.select_champion_no_intersection(rs_list)
    return current_rs.select_champion_intersection(rs_list)


@cython.locals(rs_list=list, intersection=bool, args=tuple, p=object, dist_list=list)
@cython.returns(list)
def champions_selection(rs_list, intersection=0):
    # type: (list[ParResultSet]) -> List[Tuple]
    args = ((rs, rs_list, intersection) for rs in rs_list)
    p = Pool(cpu_count())
    dist_list = p.map(par_haussdorf_distance, args)
    p.close()
    p.join()
    return dist_list
