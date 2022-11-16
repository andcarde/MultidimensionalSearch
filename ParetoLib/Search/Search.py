# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""Search.

This module encapsulates the complexity of the learning process in
three functions (i.e., Search2D, Search3D and SearchND) depending on
the dimension of the space X. Those functions call to the algorithm
that implements the multidimensional search of the Pareto front.

The learning algorithm is compatible for any dimension N, and for any
Oracle defined according to the template ParetoLib.Oracle.Oracle.

The input parameters of the learning process are the following:
- xspace: the N-dimensional space that contains the upper and lower closures,
represented by a list of minimum and maximum possible values for each dimension
 (i.e., min_cornerx, max_cornerx, etc.).
- oracle: the external knowledge repository that guides the learning process.
- epsilon: a real representing the maximum desired distance between a point x
of the space and a point y of the Pareto front.
- delta: a real representing the maximum area/volume contained in the border
 that separates the upper and lower closures; delta is used as a stopping criterion
 for the learning algorithm (sum(volume(cube) for all cube in border) < delta).
- max_step: the maximum number of cubes in the border that the learning algorithm
will analyze, in case of the stopping condition *delta* is not reached yet.
- sleep: time in seconds that each intermediate 2D/3D graphic must be shown in the screen
(i.e, 0 for not showing intermediate results).
- blocking: boolean that specifies if the intermediate 2D/3D graphics must be explicitly
 closed by the user, or they are automatically closed after *sleep* seconds.
- simplify: boolean that specifies if the number of cubes in the 2D/3D graphics must
be minimized.
- opt_level: an integer specifying which version of the learning algorithm to use
 (i.e., 0, 1 or 2; use 2 for fast convergence).
- parallel: boolean that specifies if the user desire to take advantage of the
multithreading capabilities of the computer.
- logging: boolean that specifies if the algorithm must print traces for
debugging options.


As a result, the function returns an object of the class ResultSet with the distribution
of the space X in three subspaces: a lower closure, an upper closure and a border which
 contains the Pareto front.
"""
import time
from math import ceil, log
from typing import List, Tuple
import cython

from ParetoLib.Geometry.Rectangle import Rectangle

import ParetoLib.Search.SeqSearch as SeqSearch
import ParetoLib.Search.ParSearch as ParSearch
# import ParetoLib.Search as RootSearch
import ParetoLib.Search

RootSearch = ParetoLib.Search

from ParetoLib.Search.CommonSearch import EPS, DELTA, STEPS, ALPHA, P0, NUMCELLS
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Oracle.Oracle import Oracle


# Auxiliar functions used in 2D, 3D and ND
# Creation of Spaces
@cython.returns(object)
@cython.locals(minx=cython.double, miny=cython.double, maxx=cython.double, maxy=cython.double,
               minc=(cython.double, cython.double), maxc=(cython.double, cython.double), xyspace=object,
               start=cython.double, end=cython.double, time0=cython.double)
def create_2D_space(minx, miny, maxx, maxy):
    # type: (float, float, float, float) -> Rectangle
    RootSearch.logger.debug('Creating Space')
    start = time.time()
    minc = (minx, miny)
    maxc = (maxx, maxy)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    RootSearch.logger.debug('Time creating Space: {0}'.format(str(time0)))
    return xyspace


@cython.returns(object)
@cython.locals(minx=cython.double, miny=cython.double, maxx=cython.double, maxy=cython.double,
               minc=(cython.double, cython.double, cython.double), maxc=(cython.double, cython.double, cython.double),
               xyspace=object,
               start=cython.double, end=cython.double, time0=cython.double)
def create_3D_space(minx, miny, minz, maxx, maxy, maxz):
    # type: (float, float, float, float, float, float) -> Rectangle
    RootSearch.logger.debug('Creating Space')
    start = time.time()
    minc = (minx, miny, minz)
    maxc = (maxx, maxy, maxz)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    RootSearch.logger.debug('Time creating Space: {0}'.format(str(time0)))
    return xyspace


@cython.returns(object)
@cython.locals(minc=tuple, maxc=tuple, xyspace=object,
               start=cython.double, end=cython.double, time0=cython.double)
def create_ND_space(args):
    # type: (iter) -> Rectangle
    # args = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    RootSearch.logger.debug('Creating Space')
    start = time.time()
    minc = tuple(minx for minx, _ in args)
    maxc = tuple(maxx for _, maxx in args)
    xyspace = Rectangle(minc, maxc)
    end = time.time()
    time0 = end - start
    RootSearch.logger.debug('Time creating Space: {0}'.format(str(time0)))
    return xyspace


# Dimensional tests
@cython.ccall
@cython.returns(object)
@cython.locals(ora=object, min_cornerx=cython.double, min_cornery=cython.double, max_cornerx=cython.double,
               max_cornery=cython.double, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
               blocking=cython.bint,
               sleep=cython.double, opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, xspace=object, rs=object)
def Search2D(ora,
             min_cornerx=0.0,
             min_cornery=0.0,
             max_cornerx=1.0,
             max_cornery=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0,
             opt_level=2,
             parallel=False,
             logging=True,
             simplify=True):
    # type: (Oracle, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    xyspace = create_2D_space(min_cornerx, min_cornery, max_cornerx, max_cornery)
    if parallel:
        rs = ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    # n = int((max_cornerx - min_cornerx) / 0.1)
    # points = rs.get_points_border(n)

    # print('Points ', points)
    # xs = [point[0] for point in points]
    # ys = [point[1] for point in points]

    if simplify:
        rs.simplify()
        rs.fusion()

    # rs.plot_2D(targetx=xs, targety=ys, blocking=True, var_names=ora.get_var_names())
    # rs.plot_2D_light(targetx=xs, targety=ys, blocking=True, var_names=ora.get_var_names())
    rs.plot_2D_light(blocking=True, var_names=ora.get_var_names())
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora=object, min_cornerx=cython.double, min_cornery=cython.double, min_cornerz=cython.double,
               max_cornerx=cython.double, max_cornery=cython.double, max_cornerz=cython.double, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               opt_level=cython.uint, parallel=cython.bint, logging=cython.bint, simplify=cython.bint, xspace=object,
               rs=object)
def Search3D(ora,
             min_cornerx=0.0,
             min_cornery=0.0,
             min_cornerz=0.0,
             max_cornerx=1.0,
             max_cornery=1.0,
             max_cornerz=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0,
             opt_level=2,
             parallel=False,
             logging=True,
             simplify=True):
    # type: (Oracle, float, float, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    xyspace = create_3D_space(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)

    if parallel:
        rs = ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    # Explicitly print a set of n points in the Pareto boundary for emphasizing the front
    # n = int((max_cornerx - min_cornerx) / 0.1)
    # points = rs.get_points_border(n)

    # print('Points ', points)
    # xs = [point[0] for point in points]
    # ys = [point[1] for point in points]
    # zs = [point[2] for point in points]

    if simplify:
        rs.simplify()
        rs.fusion()

    # rs.plot_3D(targetx=xs, targety=ys, targetz=zs, blocking=True, var_names=ora.get_var_names())
    # rs.plot_3D_light(targetx=xs, targety=ys, targetz=zs, blocking=True, var_names=ora.get_var_names())
    rs.plot_3D_light(blocking=True, var_names=ora.get_var_names())
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora=object, min_corner=cython.double, max_corner=cython.double, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, xspace=object, rs=object)
def SearchND(ora,
             min_corner=0.0,
             max_corner=1.0,
             epsilon=EPS,
             delta=DELTA,
             max_step=STEPS,
             blocking=False,
             sleep=0.0,
             opt_level=2,
             parallel=False,
             logging=True,
             simplify=True):
    # type: (Oracle, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    d = ora.dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)

    if parallel:
        rs = ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    if simplify:
        rs.simplify()
        rs.fusion()
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora=object, list_intervals=list,
               epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint,
               sleep=cython.double, opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, xspace=object, rs=object)
def SearchND_2(ora,
               list_intervals,
               epsilon=EPS,
               delta=DELTA,
               max_step=STEPS,
               blocking=False,
               sleep=0.0,
               opt_level=2,
               parallel=False,
               logging=True,
               simplify=True):
    # type: (Oracle, list, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet

    # list_intervals = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    xyspace = create_ND_space(list_intervals)

    if parallel:
        rs = ParSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    else:
        rs = SeqSearch.multidim_search(xyspace, ora, epsilon, delta, max_step,
                                       blocking, sleep, opt_level, logging)
    if simplify:
        rs.simplify()
        rs.fusion()
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora1=object, ora2=object, min_cornerx=cython.double, min_cornery=cython.double,
               max_cornerx=cython.double, max_cornery=cython.double, epsilon=cython.double, delta=cython.double,
               max_step=cython.ulonglong, blocking=cython.bint,
               sleep=cython.double, opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, xspace=object, intersection_result=object)
def SearchIntersection2D(ora1, ora2,
                         min_cornerx=0.0,
                         min_cornery=0.0,
                         max_cornerx=1.0,
                         max_cornery=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         max_step=STEPS,
                         blocking=False,
                         sleep=0.0,
                         opt_level=1,
                         parallel=False,
                         logging=True,
                         simplify=True):
    # type: (Oracle, Oracle, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (ora1.dim() == ora1.dim()), 'Oracle 1 and Oracle 2 have different dimensions'

    xyspace = create_2D_space(min_cornerx, min_cornery, max_cornerx, max_cornery)

    if parallel:
        intersection_result = ParSearch.multidim_intersection_search(xyspace, [], ora1, ora2, epsilon, delta, max_step,
                                                                     blocking, sleep, opt_level, logging)
    else:
        intersection_result = SeqSearch.multidim_intersection_search(xyspace, [], ora1, ora2, epsilon, delta, max_step,
                                                                     blocking, sleep, opt_level, logging)
    if simplify:
        intersection_result.simplify()
        intersection_result.fusion()
    return intersection_result


@cython.ccall
@cython.returns(object)
@cython.locals(ora1=object, ora2=object, min_cornerx=cython.double, min_cornery=cython.double,
               min_cornerz=cython.double, max_cornerx=cython.double, max_cornery=cython.double,
               max_cornerz=cython.double, epsilon=cython.double, delta=cython.double,
               max_step=cython.ulonglong, blocking=cython.bint,
               sleep=cython.double, opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, xspace=object, intersection_result=object)
def SearchIntersection3D(ora1, ora2,
                         min_cornerx=0.0,
                         min_cornery=0.0,
                         min_cornerz=0.0,
                         max_cornerx=1.0,
                         max_cornery=1.0,
                         max_cornerz=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         max_step=STEPS,
                         blocking=False,
                         sleep=0.0,
                         opt_level=1,
                         parallel=False,
                         logging=True,
                         simplify=True):
    # type: (Oracle, Oracle, float, float, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (ora1.dim() == ora1.dim()), 'Oracle 1 and Oracle 2 have different dimensions'

    xyspace = create_3D_space(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)
    if parallel:
        intersection_result = ParSearch.multidim_intersection_search(xyspace, [], ora1, ora2, epsilon, delta, max_step,
                                                                     blocking, sleep, opt_level, logging)
    else:
        intersection_result = SeqSearch.multidim_intersection_search(xyspace, [], ora1, ora2, epsilon, delta, max_step,
                                                                     blocking, sleep, opt_level, logging)
    if simplify:
        intersection_result.simplify()
        intersection_result.fusion()
    return intersection_result


@cython.ccall
@cython.returns(object)
@cython.locals(ora1=object, ora2=object, min_corner=cython.double, max_corner=cython.double, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, d=cython.uint, minc=tuple, maxc=tuple, xspace=object, intersection_result=object)
def SearchIntersectionND(ora1, ora2,
                         min_corner=0.0,
                         max_corner=1.0,
                         epsilon=EPS,
                         delta=DELTA,
                         max_step=STEPS,
                         blocking=False,
                         sleep=0.0,
                         opt_level=2,
                         parallel=False,
                         logging=True,
                         simplify=True):
    # type: (Oracle, Oracle, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (ora1.dim() == ora2.dim()), 'Oracle 1 and Oracle 2 have different dimensions'

    d = ora1.dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)

    if parallel:
        intersection_result = ParSearch.multidim_intersection_search(xyspace, [], ora1, ora2, epsilon, delta, max_step,
                                                                     blocking, sleep, opt_level, logging)
    else:
        intersection_result = SeqSearch.multidim_intersection_search(xyspace, [], ora1, ora2, epsilon, delta, max_step,
                                                                     blocking, sleep, opt_level, logging)
    if simplify:
        intersection_result.simplify()
        intersection_result.fusion()
    return intersection_result


@cython.ccall
@cython.returns(object)
@cython.locals(ora1=object, ora2=object, list_intervals=list, list_constraints=list, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               opt_level=cython.uint, parallel=cython.bint, logging=cython.bint,
               simplify=cython.bint, xspace=object, intersection_result=object)
def SearchIntersectionND_2(ora1, ora2,
                           list_intervals,
                           list_constraints=[],
                           epsilon=EPS,
                           delta=DELTA,
                           max_step=STEPS,
                           blocking=False,
                           sleep=0.0,
                           opt_level=2,
                           parallel=False,
                           logging=True,
                           simplify=True):
    # type: (Oracle, Oracle, list, list, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (ora1.dim() == ora1.dim()), 'Oracle 1 and Oracle 2 have different dimensions'

    # list_intervals = [(minx, maxx), (miny, maxy),..., (minz, maxz)]
    xyspace = create_ND_space(list_intervals)

    if parallel:
        intersection_result = ParSearch.multidim_intersection_search(xyspace, list_constraints, ora1, ora2, epsilon,
                                                                     delta, max_step, blocking, sleep, opt_level,
                                                                     logging)
    else:
        intersection_result = SeqSearch.multidim_intersection_search(xyspace, list_constraints, ora1, ora2, epsilon,
                                                                     delta, max_step, blocking, sleep, opt_level,
                                                                     logging)
    if simplify:
        intersection_result.simplify()
        intersection_result.fusion()
    return intersection_result


# TODO: We can ommit Search_BMN22. SearchND_2_BMNN22 will replace Search_BMN22 in GUI, and hence,
#  we can uncomment lines: "rs.plot_XD_light" at the end of Search2D_BMNN22 and Search3D_BMNN22
@cython.ccall
@cython.returns(object)
@cython.locals(oralist=list, list_intervals=list, blocking=cython.bint, sleep=cython.double,
               parallel=cython.bint, logging=cython.bint, simplify=cython.bint, dyn_cell_creation=cython.bint,
               mining_result=object)
def Search_BMNN22(ora_list: List[Oracle],
                  intervals: List,
                  blocking=False,
                  sleep=0.0,
                  opt_level=int,
                  parallel=bool,
                  logging=True,
                  simplify=True,
                  dyn_cell_creation=False):
    assert (len(ora_list) > 0, "Oracle list can't be empty")
    assert (all(orac.dim() == ora_list[0].dim() for orac in ora_list), "Every oracle in list must have the same diemension")

    if ora_list[0].dim() == 2:
        rs = Search2D_BMNN22(ora_list, intervals[0][0], intervals[0][1],
                             intervals[1][0], intervals[1][1], blocking, sleep, opt_level, parallel, logging, simplify)
    elif ora_list[0].dim() == 3:
        rs = Search3D_BMNN22(ora_list, intervals[0][0], intervals[0][1], intervals[0][2],
                             intervals[1][0], intervals[1][1], intervals[1][2], blocking, sleep, opt_level, parallel,
                             logging, simplify)
    elif ora_list[0].dim() > 3:
        rs = SearchND_BMNN22(ora_list, intervals, blocking, sleep, opt_level, parallel, logging, simplify)
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora_list=list, min_cornerx=cython.double, min_cornery=cython.double, max_cornerx=cython.double,
               max_cornery=cython.double, p0=cython.double, alpha=cython.double, num_cells=cython.int,
               blocking=cython.bint, sleep=cython.double, opt_level=cython.int, parallel=cython.bint,
               logging=cython.bint, simplify=cython.bint, rs=object)
def Search2D_BMNN22(ora_list,
                    min_cornerx=0.0,
                    min_cornery=0.0,
                    max_cornerx=1.0,
                    max_cornery=1.0,
                    p0=P0,
                    alpha=ALPHA,
                    num_cells=NUMCELLS,
                    blocking=False,
                    sleep=0.0,
                    opt_level=0,
                    parallel=False,
                    logging=True,
                    simplify=True):
    # type: (list[Oracle], float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (len(ora_list) > 0, "Oracle list can't be empty")
    assert (all(orac.dim() == 2 for orac in ora_list), "Oracles in list must have dimension 2")

    xyspace = create_2D_space(min_cornerx, min_cornery, max_cornerx, max_cornery)
    num_samples = ceil(log(alpha, 1.0 - p0))

    # if parallel:
    # rs = ParSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells)
    if not parallel:
        rs = SeqSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, blocking, sleep, opt_level,
                                              logging)

    if simplify:
        rs.simplify()
        rs.fusion()

    rs.plot_2D_light(blocking=True, var_names=ora_list[0].get_var_names())
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora_list=list, list_intervals=list, min_cornerx=cython.double, min_cornery=cython.double,
               min_cornerz=cython.double, max_cornerx=cython.double, max_cornery=cython.double,
               max_cornerz=cython.double, p0=cython.double, alpha=cython.double, num_cells=cython.int,
               blocking=cython.bint, sleep=cython.double, opt_level=cython.int, parallel=cython.bint,
               logging=cython.bint, simplify=cython.bint, rs=object)
def Search3D_BMNN22(ora_list,
                    min_cornerx=0.0,
                    min_cornery=0.0,
                    min_cornerz=0.0,
                    max_cornerx=1.0,
                    max_cornery=1.0,
                    max_cornerz=1.0,
                    p0=P0,
                    alpha=ALPHA,
                    num_cells=NUMCELLS,
                    blocking=False,
                    sleep=0.0,
                    opt_level=0,
                    parallel=False,
                    logging=True,
                    simplify=True):
    # type: (list[Oracle], float, float, float, float, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (len(ora_list) > 0, "Oracle list can't be empty")
    assert (all(orac.dim() == 3 for orac in ora_list), "Oracles in list must have dimension 3")

    xyspace = create_3D_space(min_cornerx, min_cornery, min_cornerz, max_cornerx, max_cornery, max_cornerz)
    num_samples = ceil(log(alpha, 1.0 - p0))

    if parallel:
        rs = ParSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, num_cells, blocking, sleep, opt_level,
                                              logging)
    else:
        rs = SeqSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, blocking, sleep, opt_level,
                                              logging)

    if simplify:
        rs.simplify()
        rs.fusion()

    rs.plot_3D_light(blocking=True, var_names=ora_list[0].get_var_names())
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(ora_list=list, min_corner=cython.double, max_corner=cython.double, p0=cython.double, alpha=cython.double,
               num_cells=cython.int, blocking=cython.bint, sleep=cython.double, opt_level=cython.int,
               parallel=cython.bint, logging=cython.bint, simplify=cython.bint, rs=object)
def SearchND_BMNN22(ora_list,
                    min_corner=0.0,
                    max_corner=1.0,
                    p0=P0,
                    alpha=ALPHA,
                    num_cells=NUMCELLS,
                    blocking=False,
                    sleep=0.0,
                    opt_level=0,
                    parallel=False,
                    logging=True,
                    simplify=True):
    # type: (list, float, float, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert (len(ora_list) > 0, "Oracle list can't be empty")
    assert (all(orac.dim() == ora_list[0].dim() for orac in ora_list), "Every oracle in list must have the same diemension")
    d = ora_list[0].dim()

    minc = (min_corner,) * d
    maxc = (max_corner,) * d
    xyspace = Rectangle(minc, maxc)

    num_samples = ceil(log(alpha, 1.0 - p0))

    if parallel:
        rs = ParSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, blocking, sleep, opt_level,
                                              logging)
    else:
        rs = SeqSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, blocking, sleep, opt_level,
                                              logging)

    if simplify:
        rs.simplify()
        rs.fusion()
    return rs


@cython.ccall
@cython.returns(object)
@cython.locals(oralist=list, list_intervals=list, p0=cython.double, alpha=cython.double, num_cells=cython.int,
               blocking=cython.bint, sleep=cython.double, opt_level=cython.int, parallel=cython.bint,
               logging=cython.bint, simplify=cython.bint, rs=object)
def SearchND_2_BMNN22(ora_list,
                      list_intervals,
                      p0=P0,
                      alpha=ALPHA,
                      num_cells=NUMCELLS,
                      blocking=False,
                      sleep=0.0,
                      opt_level=int,
                      parallel=bool,
                      logging=True,
                      simplify=True):
    # type: (list[Oracle], list, float, float, int, bool, float, int, bool, bool, bool) -> ResultSet
    assert len(ora_list) > 0, "Oracle list can't be empty"
    assert all(orac.dim() == ora_list[0].dim() for orac in ora_list), "Every oracle in list must have the same diemension"

    xyspace = create_ND_space(list_intervals)

    assert ora_list[0].dim() == xyspace.dim(), "The oracles and the space must have the same dimension"

    num_samples = ceil(log(alpha, 1.0 - p0))
    if parallel:
        rs = ParSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, blocking, sleep, opt_level,
                                              logging)
    else:
        rs = SeqSearch.multidim_search_BMNN22(xyspace, ora_list, num_samples, num_cells, blocking, sleep, opt_level,
                                              logging)

    if simplify:
        rs.simplify()
        rs.fusion()
    return rs
