# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""ParSearch.

This module implements a multithreading version of the learning
algorithms described in [1] for searching the Pareto front.

[1] Learning Monotone Partitions of Partially-Ordered Domains,
Nicolas Basset, Oded Maler, J.I Requeno, in
doc/article.pdf.
"""

import os
import copy
import time
import tempfile
import itertools
import multiprocessing as mp
import numpy as np
import cython

from multiprocessing import Manager, Pool, cpu_count
from sortedcontainers import SortedSet, SortedListWithKey

# import ParetoLib.Search as RootSearch
import ParetoLib.Search

RootSearch = ParetoLib.Search

from ParetoLib.Search.CommonSearch import EPS, DELTA, STEPS, INTERFULL, INTERNULL, INTER, NO_INTER, \
    binary_search, intersection_empty, intersection_empty_constrained, intersection_expansion_search
from ParetoLib.Search.SeqSearch import pos_neg_box_gen, pos_overlap_box_gen, bound_box_with_constraints
from ParetoLib.Search.ParResultSet import ParResultSet

from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Geometry.Rectangle import Rectangle, irect, idwc, iuwc, comp, incomp, incomp_segment, incomp_segmentpos, \
    incomp_segment_neg_remove_down, incomp_segment_neg_remove_up, interirect
from ParetoLib.Geometry.ParRectangle import pvol
from ParetoLib.Geometry.Lattice import Lattice
from ParetoLib.Geometry.Point import less_equal


@cython.locals(xrectangle=object, epsilon=cython.double, n=cython.ushort, error=tuple, y=object,
               steps_binsearch=cython.ushort)
@cython.returns(object)
def pbin_search_ser(args):
    xrectangle, f, epsilon, n = args
    RootSearch.logger.debug('Executing serial binary search')
    RootSearch.logger.debug('xrectangle, epsilon, n: {0}, {1}, {2}'.format(xrectangle, epsilon, n))
    error = (epsilon,) * n
    y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
    RootSearch.logger.debug('End serial binary search')
    RootSearch.logger.debug('y, steps_binsearch: {0}, {1}'.format(y, steps_binsearch))
    return y


# dict_man=dict
@cython.locals(xrectangle=object, epsilon=cython.double, n=cython.ushort, ora=object, error=tuple,
               y=object, steps_binsearch=cython.ushort)
@cython.returns(object)
def pbin_search(args):
    xrectangle, dict_man, epsilon, n = args
    RootSearch.logger.debug('Executing parallel binary search')
    RootSearch.logger.debug('xrectangle, epsilon, n: {0}, {1}, {2}'.format(xrectangle, epsilon, n))
    RootSearch.logger.debug('dict_man[{0}]: {1}'.format(mp.current_process().name, dict_man[mp.current_process().name]))
    ora = dict_man[mp.current_process().name]
    f = ora.membership()
    RootSearch.logger.debug('f = {0}'.format(f))
    error = (epsilon,) * n
    y, steps_binsearch = binary_search(xrectangle.diag(), f, error)
    RootSearch.logger.debug('End parallel binary search')
    RootSearch.logger.debug('y, steps_binsearch: {0}, {1}'.format(y, steps_binsearch))
    return y


# @cython.locals(args=(object, object), xrectangle=object, y=object)
@cython.locals(xrectangle=object, y=object)
@cython.returns(object)
def pb0(args):
    # b0 = Rectangle(xspace.min_corner, y.low)
    xrectangle, y = args
    return Rectangle(xrectangle.min_corner, y.low)


# @cython.locals(args=(object, object), xrectangle=object, y=object)
@cython.locals(xrectangle=object, y=object)
@cython.returns(object)
def pb1(args):
    # b1 = Rectangle(y.high, xspace.max_corner)
    xrectangle, y = args
    return Rectangle(y.high, xrectangle.max_corner)


# @cython.locals(args=(list, object, object), incomparable=list, y=object, xrectangle=object)
@cython.locals(incomparable=list, y=object, xrectangle=object)
@cython.returns(list)
def pborder(args):
    # border = irect(incomparable, yrectangle, xrectangle)
    incomparable, y, xrectangle = args
    yrectangle = Rectangle(y.low, y.high)
    return irect(incomparable, yrectangle, xrectangle)


# @cython.locals(args=(object, object), bi_extended=object, rect=object)
@cython.locals(bi_extended=object, rect=object)
@cython.returns(object)
def pborder_dominatedby_bi(args):
    bi_extended, rect = args
    return rect.intersection(bi_extended)


# @cython.locals(args=(object, object), rect=object, bi_extended=object)
@cython.locals(rect=object, bi_extended=object)
@cython.returns(list)
def pborder_nondominatedby_bi(args):
    rect, bi_extended = args
    return rect - bi_extended


# @cython.locals(args=(object, object), b0_extended=object, rect=object)
@cython.locals(b0_extended=object, rect=object)
@cython.returns(list)
def pborder_nondominatedby_b0(args):
    b0_extended, rect = args
    return idwc(b0_extended, rect)


# @cython.locals(args=(object, object), b1_extended=object, rect=object)
@cython.locals(b1_extended=object, rect=object)
@cython.returns(list)
def pborder_nondominatedby_b1(args):
    b1_extended, rect = args
    return iuwc(b1_extended, rect)


# Multidimensional search
# The search returns a set of Rectangles in Yup, Ylow and Border
@cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, oracle=object, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
               blocking=cython.bint, sleep=cython.double, opt_level=cython.uint, logging=cython.bint, md_search=list,
               start=cython.double, end=cython.double, time0=cython.double, rs=object)
def multidim_search(xspace,
                    oracle,
                    epsilon=EPS,
                    delta=DELTA,
                    max_step=STEPS,
                    blocking=False,
                    sleep=0.0,
                    opt_level=2,
                    logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, int, bool) -> ParResultSet
    md_search = [multidim_search_deep_first_opt_0,
                 multidim_search_deep_first_opt_1,
                 multidim_search_deep_first_opt_2,
                 multidim_search_deep_first_opt_3]

    RootSearch.logger.info('Starting multidimensional search')
    start = time.time()
    rs = md_search[opt_level](xspace,
                              oracle,
                              epsilon=epsilon,
                              delta=delta,
                              max_step=max_step,
                              blocking=blocking,
                              sleep=sleep,
                              logging=logging)
    end = time.time()
    time0 = end - start
    RootSearch.logger.info('Time multidim search: ' + str(time0))

    return rs


##############################
# opt_3 = Equivalent to opt_2 but using a Lattice for detecting dominated cubes in the boundary
# opt_2 = Equivalent to opt_1 but involving less computations
# opt_1 = Maximum optimisation
# opt_0 = No optimisation
##############################

########################################################################################################################
# Multidimensional search prioritizing the analysis of rectangles with highest volume
@cython.returns(object)
@cython.locals(xspace=object, oracle=object, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
               blocking=cython.bint, sleep=cython.double, logging=cython.bint, n=cython.ushort, comparable=list,
               incomparable=list, border=object, lattice_border_ylow=object, lattice_border_yup=object, ylow=list,
               yup=list, ylow_minimal=list, yup_minimal=list, vol_total=cython.double, vol_yup=cython.double,
               vol_ylow=cython.double, vol_border=cython.double, step=cython.ulonglong,
               remaining_steps=cython.ulonglong, args_pborder=list, args_pbin_search=object, num_proc=cython.ushort,
               p=object, man=object, proc=object, tempdir=str, chunk=cython.ulonglong, y_list=list, y_segment=object,
               yl=tuple, yu=tuple, b0_extended=object, b1_extended=object, ylow_rectangle=object,
               border_overlapping_b0=set, args_pborder_nondominatedby_b0=list, border_nondominatedby_b0=set,
               yup_rectangle=object, border_overlapping_b1=set, args_pborder_nondominatedby_b1=list,
               border_nondominatedby_b1=set, db0=list, db1=list, boxes_null_vol=list, name=str, rs=object)
# @cython.locals(xspace=object, oracle=object, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
#                blocking=cython.bint, sleep=cython.double, logging=cython.bint, n=cython.ushort, comparable=list,
#                incomparable=list, border=object, lattice_border_ylow=object, lattice_border_yup=object, ylow=list,
#                yup=list, ylow_minimal=list, yup_minimal=list, vol_total=cython.double, vol_yup=cython.double,
#                vol_ylow=cython.double, vol_border=cython.double, step=cython.ulonglong,
#                remaining_steps=cython.ulonglong, args_pbin_search=object,num_proc=cython.ushort, p=object,
#                man=object, dict_man=dict, proc=object, tempdir=str, chunk=cython.ulonglong, slice_border=list,
#                y_list=list, y_segment=object, yl=tuple, yu=tuple, b0_extended=object, b1_extended=object,
#                ylow_rectangle=object, border_overlapping_b0=set, args_pborder_nondominatedby_b0=list,
#                border_nondominatedby_b0=set, yup_rectangle=object, border_overlapping_b1=set,
#                args_pborder_nondominatedby_b1=list, border_nondominatedby_b1=set, db0=list, db1=list,
#                boxes_null_vol=list, name=str, rs=object)
def multidim_search_deep_first_opt_3(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.volume)

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    lattice_border_ylow = Lattice(dim=xspace.dim(), key=lambda x: x.min_corner)
    lattice_border_yup = Lattice(dim=xspace.dim(), key=lambda x: x.max_corner)

    lattice_border_ylow.add(xspace)
    lattice_border_yup.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    # x_minimal = points from 'x' that are strictly incomparable (Pareto optimal)
    ylow_minimal = []
    yup_minimal = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc.name: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle))
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        border -= slice_border

        lattice_border_ylow.remove_list(slice_border)
        lattice_border_yup.remove_list(slice_border)

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        # b0_list = p.map(pb0, zip(slice_border, y_list))
        # b1_list = p.map(pb1, zip(slice_border, y_list))
        #
        # ylow.extend(b0_list)
        # yup.extend(b1_list)
        #
        # vol_b0_list = p.imap_unordered(pvol, b0_list)
        # vol_b1_list = p.imap_unordered(pvol, b1_list)
        #
        # vol_ylow += sum(vol_b0_list)
        # vol_yup += sum(vol_b1_list)

        ################################
        for y_segment in y_list:
            yl, yh = y_segment.low, y_segment.high
            # Every Border rectangle that dominates B0 is included in Ylow
            # Every Border rectangle that is dominated by B1 is included in Yup
            b0_extended = Rectangle(xspace.min_corner, yl)
            b1_extended = Rectangle(yh, xspace.max_corner)

            # Warning: Be aware of the overlapping areas of the cubes in the border.
            ylow_rectangle = Rectangle(yl, yl)
            border_overlapping_b0 = lattice_border_ylow.less_equal(ylow_rectangle)
            # border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]

            # for rect in border_overlapping_b0:
            #     border |= list(rect - b0_extended)
            # border -= border_overlapping_b0

            # Use [] (list, static) instead of () (iterator, dynamic) for preventing interleaving and racing conditions
            # of copy.deepcopy when running in parallel
            # args_pborder_nondominatedby_b0 = [(rect, copy.deepcopy(b0_extended)) for rect in border_overlapping_b0]
            # border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b0)
            args_pborder_nondominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_b0, args_pborder_nondominatedby_b0)

            # Flatten list
            border_nondominatedby_b0 = set(itertools.chain.from_iterable(border_nondominatedby_b0_list))

            # args_pborder_dominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            # border_dominatedby_b0 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b0)
            # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]

            border |= border_nondominatedby_b0
            border -= border_overlapping_b0

            lattice_border_ylow.add_list(border_nondominatedby_b0)
            lattice_border_ylow.remove_list(border_overlapping_b0)

            lattice_border_yup.add_list(border_nondominatedby_b0)
            lattice_border_yup.remove_list(border_overlapping_b0)

            yup_rectangle = Rectangle(yh, yh)
            border_overlapping_b1 = lattice_border_yup.greater_equal(yup_rectangle)
            # border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
            # for rect in border_overlapping_b1:
            #     border |= list(rect - b1_extended)
            # border -= border_overlapping_b1

            # args_pborder_nondominatedby_b1 = [(rect, copy.deepcopy(b1_extended)) for rect in border_overlapping_b1]
            # border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b1)
            args_pborder_nondominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_b1, args_pborder_nondominatedby_b1)

            # Flatten list
            border_nondominatedby_b1 = set(itertools.chain.from_iterable(border_nondominatedby_b1_list))

            # args_pborder_dominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            # border_dominatedby_b1 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b1)
            # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

            border |= border_nondominatedby_b1
            border -= border_overlapping_b1

            lattice_border_ylow.add_list(border_nondominatedby_b1)
            lattice_border_ylow.remove_list(border_overlapping_b1)

            lattice_border_yup.add_list(border_nondominatedby_b1)
            lattice_border_yup.remove_list(border_overlapping_b1)

            db0 = Rectangle.difference_rectangles(b0_extended, ylow_minimal)
            db1 = Rectangle.difference_rectangles(b1_extended, yup_minimal)

            ylow.extend(db0)
            yup.extend(db1)

            ylow_minimal.append(b0_extended)
            yup_minimal.append(b1_extended)

            vol_b0_list = p.imap_unordered(pvol, db0)
            vol_b1_list = p.imap_unordered(pvol, db1)

            vol_ylow += sum(vol_b0_list)
            vol_yup += sum(vol_b1_list)

        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        lattice_border_ylow.add_list(list(new_incomp_rects))
        lattice_border_yup.add_list(list(new_incomp_rects))

        # Remove boxes in the boundary with volume 0
        boxes_null_vol = border[:border.bisect_key_left(0.0)]
        border -= boxes_null_vol
        lattice_border_ylow.remove_list(boxes_null_vol)
        lattice_border_yup.remove_list(boxes_null_vol)

        ################################
        # Every rectangle in 'new_incomp_rects' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'new_incomp_rects' is incomparable for current B1 and for all B1 included in Yup
        ################################

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


@cython.returns(object)
@cython.locals(xspace=object, oracle=object, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
               blocking=cython.bint, sleep=cython.double, logging=cython.bint, n=cython.ushort, comparable=list,
               incomparable=list, border=object, lattice_border_ylow=object, lattice_border_yup=object, ylow=list,
               yup=list, ylow_minimal=list, yup_minimal=list, vol_total=cython.double, vol_yup=cython.double,
               vol_ylow=cython.double, vol_border=cython.double, step=cython.ulonglong,
               remaining_steps=cython.ulonglong, args_pborder=list, args_pbin_search=object, num_proc=cython.ushort,
               p=object, man=object, proc=object, tempdir=str, chunk=cython.ulonglong, y_list=list, y_segment=object,
               yl=tuple, yu=tuple, b0_extended=object, b1_extended=object, ylow_rectangle=object,
               border_overlapping_b0=set, args_pborder_nondominatedby_b0=list, border_nondominatedby_b0=set,
               yup_rectangle=object, border_overlapping_b1=set, args_pborder_nondominatedby_b1=list,
               border_nondominatedby_b1=set, db0=list, db1=list, boxes_null_vol=list, name=str, rs=object)
def multidim_search_deep_first_opt_2(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # xspace is a particular case of maximal rectangle
    # xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.volume)

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    # x_minimal = points from 'x' that are strictly incomparable (Pareto optimal)
    ylow_minimal = []
    yup_minimal = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc.name: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle))
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        # b0_list = p.map(pb0, zip(slice_border, y_list))
        # b1_list = p.map(pb1, zip(slice_border, y_list))
        #
        # ylow.extend(b0_list)
        # yup.extend(b1_list)
        #
        # vol_b0_list = p.imap_unordered(pvol, b0_list)
        # vol_b1_list = p.imap_unordered(pvol, b1_list)
        #
        # vol_ylow += sum(vol_b0_list)
        # vol_yup += sum(vol_b1_list)

        ################################
        for y_segment in y_list:
            yl, yh = y_segment.low, y_segment.high
            # Every Border rectangle that dominates B0 is included in Ylow
            # Every Border rectangle that is dominated by B1 is included in Yup
            b0_extended = Rectangle(xspace.min_corner, yl)
            b1_extended = Rectangle(yh, xspace.max_corner)

            # Warning: Be aware of the overlapping areas of the cubes in the border.
            border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]
            # for rect in border_overlapping_b0:
            #     border |= list(rect - b0_extended)
            # border -= border_overlapping_b0

            # Use [] (list, static) instead of () (iterator, dynamic) for preventing interleaving and racing conditions
            # of copy.deepcopy when running in parallel
            # args_pborder_nondominatedby_b0 = [(rect, copy.deepcopy(b0_extended)) for rect in border_overlapping_b0]
            # border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b0)
            args_pborder_nondominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            border_nondominatedby_b0_list = p.imap_unordered(pborder_nondominatedby_b0, args_pborder_nondominatedby_b0)

            # Flatten list
            border_nondominatedby_b0 = set(itertools.chain.from_iterable(border_nondominatedby_b0_list))

            # args_pborder_dominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            # border_dominatedby_b0 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b0)
            # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]

            border |= border_nondominatedby_b0
            border -= border_overlapping_b0

            border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
            # for rect in border_overlapping_b1:
            #     border |= list(rect - b1_extended)
            # border -= border_overlapping_b1

            # args_pborder_nondominatedby_b1 = [(rect, copy.deepcopy(b1_extended)) for rect in border_overlapping_b1]
            # border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_bi, args_pborder_nondominatedby_b1)
            args_pborder_nondominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            border_nondominatedby_b1_list = p.imap_unordered(pborder_nondominatedby_b1, args_pborder_nondominatedby_b1)

            # Flatten list
            border_nondominatedby_b1 = set(itertools.chain.from_iterable(border_nondominatedby_b1_list))

            # args_pborder_dominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]
            # border_dominatedby_b1 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b1)
            # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

            border |= border_nondominatedby_b1
            border -= border_overlapping_b1

            db0 = Rectangle.difference_rectangles(b0_extended, ylow_minimal)
            db1 = Rectangle.difference_rectangles(b1_extended, yup_minimal)

            ylow.extend(db0)
            yup.extend(db1)

            ylow_minimal.append(b0_extended)
            yup_minimal.append(b1_extended)

            vol_b0_list = p.imap_unordered(pvol, db0)
            vol_b1_list = p.imap_unordered(pvol, db1)

            vol_ylow += sum(vol_b0_list)
            vol_yup += sum(vol_b1_list)

        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        # Remove boxes in the boundary with volume 0
        border -= border[:border.bisect_key_left(0.0)]

        ################################
        # Every rectangle in 'new_incomp_rects' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'new_incomp_rects' is incomparable for current B1 and for all B1 included in Yup
        ################################

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


@cython.returns(object)
@cython.locals(xspace=object, oracle=object, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
               blocking=cython.bint, sleep=cython.double, logging=cython.bint, n=cython.ushort, comparable=list,
               incomparable=list, border=object, lattice_border_ylow=object, lattice_border_yup=object, ylow=list,
               yup=list, ylow_minimal=list, yup_minimal=list, vol_total=cython.double, vol_yup=cython.double,
               vol_ylow=cython.double, vol_border=cython.double, step=cython.ulonglong,
               remaining_steps=cython.ulonglong, args_pbin_search=object, num_proc=cython.ushort, p=object, man=object,
               proc=object, tempdir=str, chunk=cython.ulonglong, y_list=list, y_segment=object,
               yl=tuple, yu=tuple, b0_extended=object, b1_extended=object, ylow_rectangle=object,
               border_overlapping_b0=set, args_pborder_nondominatedby_b0=list, border_nondominatedby_b0=set,
               yup_rectangle=object, border_overlapping_b1=set, args_pborder_nondominatedby_b1=list,
               border_nondominatedby_b1=set, db0=list, db1=list, boxes_null_vol=list, name=str, rs=object)
def multidim_search_deep_first_opt_1(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.volume)

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc.name: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle))
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        b0_list = p.map(pb0, zip(slice_border, y_list))
        b1_list = p.map(pb1, zip(slice_border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.imap_unordered(pvol, b0_list)
        vol_b1_list = p.imap_unordered(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        ################################
        for y_segment in y_list:
            yl, yh = y_segment.low, y_segment.high
            # Every Border rectangle that dominates B0 is included in Ylow
            # Every Border rectangle that is dominated by B1 is included in Yup
            b0_extended = Rectangle(xspace.min_corner, yl)
            b1_extended = Rectangle(yh, xspace.max_corner)

            # Every cube in the boundary overlaps another cube in the boundary
            # When cubes from the boundary are moved to ylow or yup, they may still have a complementary cube
            # remaining in the boundary with a non-empty intersection.
            border_overlapping_ylow = [r for r in ylow if r.overlaps(b0_extended)]
            border_overlapping_yup = [r for r in yup if r.overlaps(b1_extended)]

            border_overlapping_b0 = [rect for rect in border if b0_extended.overlaps(rect)]
            for rect in border_overlapping_b0:
                border |= list(rect - b0_extended)
            border -= border_overlapping_b0

            border_overlapping_b1 = [rect for rect in border if b1_extended.overlaps(rect)]
            for rect in border_overlapping_b1:
                border |= list(rect - b1_extended)
            border -= border_overlapping_b1

            # border_dominatedby_b0 = [rect.intersection(b0_extended) for rect in border_overlapping_b0]
            # border_dominatedby_b1 = [rect.intersection(b1_extended) for rect in border_overlapping_b1]

            # Use [] (list, static) instead of () (iterator, dynamic) for preventing interleaving and racing conditions
            # of copy.deepcopy when running in parallel
            # args_pborder_dominatedby_b0 = [(copy.deepcopy(b0_extended), rect) for rect in border_overlapping_b0]
            # args_pborder_dominatedby_b1 = [(copy.deepcopy(b1_extended), rect) for rect in border_overlapping_b1]

            # border_dominatedby_b0 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b0)
            # border_dominatedby_b1 = p.map(pborder_dominatedby_bi, args_pborder_dominatedby_b1)

            # Warning: Be aware of the overlapping areas of the cubes in the border.
            # If we calculate the intersection of b{0|1}_extended with all the cubes in the frontier, and two cubes
            # 'a' and 'b' partially overlaps, then the volume of this overlapping portion will be considered twice
            # Solution: Project the 'shadow' of the cubes in the border over b{0|1}_extended.

            border_dominatedby_b0_shadow = Rectangle.difference_rectangles(b0_extended, border_overlapping_b0)
            border_dominatedby_b1_shadow = Rectangle.difference_rectangles(b1_extended, border_overlapping_b1)

            # The negative of this image returns a set of cubes in the boundary without overlapping.
            # border_dominatedby_b{0|1} will be appended to yup/ylow.
            # Remove the portion of the negative that overlaps any cube is already appended to yup/ylow

            border_dominatedby_b0 = Rectangle.difference_rectangles(b0_extended,
                                                                    border_dominatedby_b0_shadow + border_overlapping_ylow)  # ylow
            border_dominatedby_b1 = Rectangle.difference_rectangles(b1_extended,
                                                                    border_dominatedby_b1_shadow + border_overlapping_yup)  # yup

            ylow.extend(border_dominatedby_b0)
            yup.extend(border_dominatedby_b1)

            vol_b0_list = p.imap_unordered(pvol, border_dominatedby_b0)
            vol_b1_list = p.imap_unordered(pvol, border_dominatedby_b1)

            vol_ylow += sum(vol_b0_list)
            vol_yup += sum(vol_b1_list)
        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        # Remove boxes in the boundary with volume 0
        border -= border[:border.bisect_key_left(0.0)]

        ################################
        # Every rectangle in 'new_incomp_rects' is incomparable for current B0 and for all B0 included in Ylow
        # Every rectangle in 'new_incomp_rects' is incomparable for current B1 and for all B1 included in Yup
        ################################

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


# Opt_inf is not applicable: it does not improve the convergence of opt_0 because it cannot preemptively remove cubes.
# Cubes from the boundary are partially dominated by Pareto points in Ylow/Ylup, while opt_inf searches for
# cubes that are fully dominated.
def multidim_search_deep_first_opt_inf(xspace,
                                       oracle,
                                       epsilon=EPS,
                                       delta=DELTA,
                                       max_step=STEPS,
                                       blocking=False,
                                       sleep=0.0,
                                       logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.volume)

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step - step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc.name: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle))
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        b0_list = p.map(pb0, zip(slice_border, y_list))
        b1_list = p.map(pb1, zip(slice_border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.imap_unordered(pvol, b0_list)
        vol_b1_list = p.imap_unordered(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        ################################
        # Every Border rectangle that dominates B0 is included in Ylow
        # Every Border rectangle that is dominated by B1 is included in Yup
        ylow_candidates = [rect for rect in border if any(rect.dominates_rect(b0) for b0 in b0_list)]
        yup_candidates = [rect for rect in border if any(rect.is_dominated_by_rect(b1) for b1 in b1_list)]

        ylow.extend(ylow_candidates)
        yup.extend(yup_candidates)

        vol_ylow_opt_list = p.imap_unordered(pvol, ylow_candidates)
        vol_yup_opt_list = p.imap_unordered(pvol, yup_candidates)

        vol_ylow += sum(vol_ylow_opt_list)
        vol_yup += sum(vol_yup_opt_list)

        border -= ylow_candidates
        border -= yup_candidates
        ################################

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        ################################
        # Every Incomparable rectangle that dominates B0 is included in Ylow
        # Every Incomparable rectangle that is dominated by B1 is included in Yup
        ylow_candidates = [inc for inc in new_incomp_rects if any(inc.dominates_rect(b0) for b0 in ylow)]
        yup_candidates = [inc for inc in new_incomp_rects if any(inc.is_dominated_by_rect(b1) for b1 in yup)]

        ylow.extend(ylow_candidates)
        yup.extend(yup_candidates)

        vol_ylow_opt_list = p.imap_unordered(pvol, ylow_candidates)
        vol_yup_opt_list = p.imap_unordered(pvol, yup_candidates)

        vol_ylow += sum(vol_ylow_opt_list)
        vol_yup += sum(vol_yup_opt_list)

        new_incomp_rects = new_incomp_rects.difference(ylow_candidates)
        new_incomp_rects = new_incomp_rects.difference(yup_candidates)
        ################################

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        # Remove boxes in the boundary with volume 0
        border -= border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


@cython.returns(object)
@cython.locals(xspace=object, oracle=object, epsilon=cython.double, delta=cython.double, max_step=cython.ulonglong,
               blocking=cython.bint, sleep=cython.double, logging=cython.bint, n=cython.ushort, comparable=list,
               incomparable=list, border=object, ylow=list, yup=list, vol_total=cython.double, vol_yup=cython.double,
               vol_ylow=cython.double, vol_border=cython.double, step=cython.ulonglong,
               remaining_steps=cython.ulonglong, args_pbin_search=object, num_proc=cython.ushort, p=object, man=object,
               proc=object, tempdir=str, chunk=cython.ulonglong, y_list=list, b0_list=list,
               b1_list=list, args_pborder=list, new_incomp_rects=set, name=str, rs=object)
def multidim_search_deep_first_opt_0(xspace,
                                     oracle,
                                     epsilon=EPS,
                                     delta=DELTA,
                                     max_step=STEPS,
                                     blocking=False,
                                     sleep=0.0,
                                     logging=True):
    # type: (Rectangle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.volume)

    border = SortedSet([], key=Rectangle.volume)
    border.add(xspace)

    # Upper and lower clausure
    ylow = []
    yup = []

    vol_total = xspace.volume()
    vol_yup = 0
    vol_ylow = 0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    # f = oracle.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process

    # dict_man = {proc.name: copy.deepcopy(oracle) for proc in mp.active_children()}
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle))
        dict_man[proc.name] = copy.deepcopy(oracle)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= delta) and (remaining_steps > 0) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached
        # border = border[:remaining_steps] if (remaining_steps <= len(border)) else border
        # step += len(border)
        # remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        # args_pbin_search = [(xrectangle, dict_man, epsilon, n) for xrectangle in slice_border]
        args_pbin_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pbin_search, args_pbin_search)

        # Compute comparable rectangles b0 and b1
        b0_list = p.map(pb0, zip(slice_border, y_list))
        b1_list = p.map(pb1, zip(slice_border, y_list))

        ylow.extend(b0_list)
        yup.extend(b1_list)

        vol_b0_list = p.imap_unordered(pvol, b0_list)
        vol_b1_list = p.imap_unordered(pvol, b1_list)

        vol_ylow += sum(vol_b0_list)
        vol_yup += sum(vol_b1_list)

        # Compute incomparable rectangles
        # copy 'incomparable' list for avoiding racing conditions when running p.map in parallel
        # args_pborder = ((incomparable, y, xrectangle) for xrectangle, y in zip(slice_border, y_list))
        args_pborder = [(copy.deepcopy(incomparable), y, xrectangle) for xrectangle, y in zip(slice_border, y_list)]
        new_incomp_rects_iter = p.imap_unordered(pborder, args_pborder)

        # Flatten list
        new_incomp_rects = set(itertools.chain.from_iterable(new_incomp_rects_iter))

        # Add new incomparable rectangles to the border
        border |= new_incomp_rects

        # Remove boxes in the boundary with volume 0
        border -= border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_yup - vol_ylow

        RootSearch.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'
                               .format(step, vol_ylow, vol_yup, vol_border, vol_total, len(ylow), len(yup),
                                       len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, ylow, yup, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, ylow, yup, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, ylow, yup, xspace)


################################
######## EPSILON METHOD ########
################################
# @cython.ccall
@cython.returns(object)
@cython.locals(dict_man=object, epsilon=cython.double, n=cython.ushort, list_constraints=list,
               incomparable=list, incomparable_segment=list, ora1=object, ora2=object, error=tuple,
               local_vol_xrest=cython.double, local_border=list, intersect_box=list, intersection_region=list,
               min_bound=cython.double, max_bound=cython.double, rect_diag=object, intersect_indicator=cython.short,
               inside_bound=cython.bint, end_min=tuple, end_max=tuple, mod_rectangle=object, y_in=object,
               y_cover=object, steps_binsearch=cython.ushort, yrectangle=object, i=list, lower_rect=object,
               upper_rect=object, b0=object, b1=object, rect=object)
def pintersection_search_opt_0(args):
    xrectangle, dict_man, epsilon, n = args

    ora1, ora2, list_constraints, incomparable, incomparable_segment = dict_man[mp.current_process().name]
    f1, f2 = ora1.membership(), ora2.membership()

    RootSearch.logger.debug('f1 = {0}'.format(f1))
    RootSearch.logger.debug('f2 = {0}'.format(f2))
    error = (epsilon,) * n

    local_vol_xrest, local_border, intersect_box, intersect_region = 0.0, [], None, None

    min_bound, max_bound = bound_box_with_constraints(xrectangle, list_constraints)
    rect_diag = xrectangle.diag()
    if (max_bound < 0.0) or (min_bound > 1.0) or (min_bound > max_bound) or (min_bound + (epsilon / 100.0) > max_bound):
        intersect_indicator = INTERNULL
        return local_vol_xrest, local_border, intersect_box, intersect_region
    else:
        min_bound = max(0.0, min_bound)
        max_bound = min(1.0, max_bound)
        inside_bound = min_bound > 0.0 or max_bound < 1.0
        if inside_bound:
            min_bound += (epsilon / 100.0)
            max_bound -= (epsilon / 100.0)
            end_min = tuple(i + (j - i) * min_bound for i, j in zip(xrectangle.min_corner, xrectangle.max_corner))
            end_max = tuple(i + (j - i) * max_bound for i, j in zip(xrectangle.min_corner, xrectangle.max_corner))
            mod_rectangle = Rectangle(end_min, end_max)
            rect_diag = mod_rectangle.diag()
            y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(rect_diag, f1, f2,
                                                                                                error, False)
        else:
            y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(rect_diag, f1, f2,
                                                                                                error, False)
        RootSearch.logger.debug('y_in: {0}'.format(y_in))
        RootSearch.logger.debug('y_cover: {0}'.format(y_cover))

    if intersect_indicator >= INTER:
        intersect_box = [Rectangle(y_in.low, y_in.high)]
        intersect_region = [xrectangle]
    elif intersect_indicator == INTERNULL:
        if inside_bound:  # (min_bound > 0 and max_bound < 1):
            yrectangle = Rectangle(rect_diag.low, rect_diag.high)
            i = interirect(incomparable_segment, yrectangle, xrectangle)
            lower_rect = Rectangle(xrectangle.min_corner, yrectangle.max_corner)
            upper_rect = Rectangle(yrectangle.min_corner, xrectangle.max_corner)
            local_vol_xrest += lower_rect.volume() + upper_rect.volume() - yrectangle.volume()
        else:
            local_vol_xrest += xrectangle.volume()  # Temporary hack. Must purge the implementation of the algo.
            return local_vol_xrest, local_border, intersect_box, intersect_region
    else:
        b0 = Rectangle(xrectangle.min_corner, y_cover.low)
        local_vol_xrest += b0.volume()

        RootSearch.logger.debug('b0: {0}'.format(b0))

        b1 = Rectangle(y_cover.high, xrectangle.max_corner)
        local_vol_xrest += b1.volume()

        RootSearch.logger.debug('b1: {0}'.format(b1))

        yrectangle = Rectangle(y_cover.low, y_cover.high)
        i = irect(incomparable, yrectangle, xrectangle)

    for rect in i:
        if intersection_empty_constrained(rect.diag(), f1, f2, list_constraints):
            local_vol_xrest += rect.volume()
        else:
            local_border.append(rect)

    return local_vol_xrest, local_border, intersect_box, intersect_region


# @cython.ccall
@cython.returns(object)
@cython.locals(xrectangle=object, dict_man=object, epsilon=cython.double, n=cython.ushort, incomparable=list,
               incomparable_segment=list, ora1=object, ora2=object, error=tuple, local_vol_xrest=cython.double,
               local_vol_boxes=cython.double, local_border=list, intersect_box=list, intersection_region=list,
               current_privilege=cython.double, want_to_expand=cython.bint, y_in=object, y_cover=object,
               intersect_indicator=cython.short, steps_binsearch=cython.ushort, y=object, yrectangle=object,
               pos_box=object, neg_box1=object, neg_box2=object, i=list, lower_rect=object, upper_rect=object,
               b0=object, b1=object, rect=object)
def pintersection_search_opt_1(args):
    xrectangle, dict_man, epsilon, n = args

    ora1, ora2, incomparable, incomparable_segment, incomp_pos, incomp_neg_down, incomp_neg_up = dict_man[
        mp.current_process().name]
    f1, f2 = ora1.membership(), ora2.membership()

    RootSearch.logger.debug('f1 = {0}'.format(f1))
    RootSearch.logger.debug('f2 = {0}'.format(f2))
    error = (epsilon,) * n

    local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region = 0.0, 0.0, [], [], []

    current_privilege = xrectangle.privilege
    # local_vol_boxes -= xrectangle.volume()

    want_to_expand = True
    y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(xrectangle.diag(), f1, f2,
                                                                                        error, want_to_expand)

    if intersect_indicator == NO_INTER:
        y = y_in
    else:
        y = y_cover

    yrectangle = Rectangle(y.low, y.high)
    RootSearch.logger.debug('y: {0}'.format(y))

    if intersect_indicator == INTERFULL:
        intersect_box.append(Rectangle(y.low, y.high))
        local_vol_xrest += xrectangle.volume()

        return local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region
    elif intersect_indicator == INTER:
        pos_box = Rectangle(y_in.low, y_in.high)
        neg_box1 = Rectangle(xrectangle.min_corner, y_cover.low)
        neg_box2 = Rectangle(y_cover.high, xrectangle.max_corner)
        intersect_box.append(pos_box)
        intersect_region.append(xrectangle)

        i = pos_neg_box_gen(incomp_pos, incomp_neg_down, incomp_neg_up, y_in, y_cover, xrectangle)

        local_vol_xrest += pos_box.volume() + neg_box1.volume() + neg_box2.volume()
    elif intersect_indicator == NO_INTER:
        i = interirect(incomparable_segment, yrectangle, xrectangle)
        lower_rect = Rectangle(xrectangle.min_corner, yrectangle.max_corner)
        upper_rect = Rectangle(yrectangle.min_corner, xrectangle.max_corner)
        local_vol_xrest += lower_rect.volume() + upper_rect.volume() - yrectangle.volume()
    elif intersect_indicator == INTERNULL:
        local_vol_xrest += xrectangle.volume()

        return local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region
    else:
        b0 = Rectangle(xrectangle.min_corner, y.low)
        local_vol_xrest += b0.volume()
        RootSearch.logger.debug('b0: {0}'.format(b0))

        b1 = Rectangle(y.high, xrectangle.max_corner)
        local_vol_xrest += b1.volume()
        RootSearch.logger.debug('b1: {0}'.format(b1))

        i = irect(incomparable, yrectangle, xrectangle)

    for rect in i:
        if intersection_empty(rect.diag(), f1, f2):
            local_vol_xrest += rect.volume()
        else:
            rect.privilege = current_privilege + 1.0
            local_border.append(rect)
            local_vol_boxes += rect.volume()

    return local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region


# @cython.ccall
@cython.returns(object)
@cython.locals(xrectangle=object, dict_man=object, epsilon=cython.double, n=cython.ushort, incomparable=list,
               incomparable_segment=list, ora1=object, ora2=object, error=tuple, local_vol_xrest=cython.double,
               local_vol_boxes=cython.double, local_border=list, intersect_box=list, intersection_region=list,
               current_privilege=cython.double, want_to_expand=cython.bint, y_in=object, y_cover=object,
               intersect_indicator=cython.short, steps_binsearch=cython.ushort, y=object, yrectangle=object,
               pos_box=object, neg_box1=object, neg_box2=object, i=list, lower_rect=object, upper_rect=object,
               b0=object, b1=object, rect=object)
def pintersection_search_opt_2(args):
    xrectangle, dict_man, epsilon, n = args

    ora1, ora2, incomparable, incomparable_segment = dict_man[mp.current_process().name]
    f1, f2 = ora1.membership(), ora2.membership()

    RootSearch.logger.debug('f1 = {0}'.format(f1))
    RootSearch.logger.debug('f2 = {0}'.format(f2))
    error = (epsilon,) * n

    local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region = 0.0, 0.0, [], [], []

    current_privilege = xrectangle.privilege
    # local_vol_boxes -= xrectangle.volume()

    want_to_expand = True
    y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(xrectangle.diag(), f1, f2,
                                                                                        error, want_to_expand)
    if intersect_indicator == NO_INTER:
        y = y_in
    else:
        y = y_cover
    yrectangle = Rectangle(y.low, y.high)
    RootSearch.logger.debug('y: {0}'.format(y))

    if intersect_indicator == INTERFULL:
        intersect_box.append(Rectangle(y.low, y.high))
        local_vol_xrest += xrectangle.volume()

        return local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region
    elif intersect_indicator == INTER:
        pos_box = Rectangle(y_in.low, y_in.high)
        neg_box1 = Rectangle(xrectangle.min_corner, y_cover.low)
        neg_box2 = Rectangle(y_cover.high, xrectangle.max_corner)
        intersect_box.append(pos_box)
        intersect_region.append(xrectangle)

        i = pos_overlap_box_gen(incomparable, incomparable_segment, y_in, y_cover, xrectangle)

        local_vol_xrest += pos_box.volume() + neg_box1.volume() + neg_box2.volume()
    elif intersect_indicator == NO_INTER:
        i = interirect(incomparable_segment, yrectangle, xrectangle)
        lower_rect = Rectangle(xrectangle.min_corner, yrectangle.max_corner)
        upper_rect = Rectangle(yrectangle.min_corner, xrectangle.max_corner)
        local_vol_xrest += lower_rect.volume() + upper_rect.volume() - yrectangle.volume()
    elif intersect_indicator == INTERNULL:
        local_vol_xrest += xrectangle.volume()
        return local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region
    else:
        b0 = Rectangle(xrectangle.min_corner, y.low)
        local_vol_xrest += b0.volume()
        RootSearch.logger.debug('b0: {0}'.format(b0))

        b1 = Rectangle(y.high, xrectangle.max_corner)
        local_vol_xrest += b1.volume()
        RootSearch.logger.debug('b1: {0}'.format(b1))

        i = irect(incomparable, yrectangle, xrectangle)

    for rect in i:
        if intersection_empty(rect.diag(), f1, f2):
            local_vol_xrest += rect.volume()
        else:
            rect.privilege = current_privilege + 1.0
            local_border.append(rect)
            local_vol_boxes += rect.volume()

    return local_vol_xrest, local_vol_boxes, local_border, intersect_box, intersect_region


# @cython.ccall
@cython.returns(tuple)
@cython.locals(args=tuple, xrectangle=object, current_privilege=cython.double, vol=cython.double,
               intersects=cython.bint)
def pintersection_empty_constrained(args):
    xrectangle, dict_man, list_constraints = args
    RootSearch.logger.debug('Executing parallel intersection empty constrained search')
    RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
    RootSearch.logger.debug('dict_man[{0}]: {1}'.format(mp.current_process().name, dict_man[mp.current_process().name]))

    ora1, ora2 = dict_man[mp.current_process().name]
    f1 = ora1.membership()
    f2 = ora2.membership()

    RootSearch.logger.debug('f1 = {0}'.format(f1))
    RootSearch.logger.debug('f2 = {0}'.format(f2))

    intersects = intersection_empty_constrained(xrectangle.diag(), f1, f2, list_constraints)
    vol = xrectangle.volume()

    return (xrectangle, intersects, vol,)


# @cython.ccall
@cython.returns(tuple)
@cython.locals(args=tuple, xrectangle=object, current_privilege=cython.double, vol=cython.double,
               intersects=cython.bint)
def pintersection_empty(args):
    xrectangle, dict_man, current_privilege = args
    RootSearch.logger.debug('Executing parallel intersection empty search')
    RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
    RootSearch.logger.debug('dict_man[{0}]: {1}'.format(mp.current_process().name, dict_man[mp.current_process().name]))

    ora1, ora2 = dict_man[mp.current_process().name]
    f1 = ora1.membership()
    f2 = ora2.membership()

    RootSearch.logger.debug('f1 = {0}'.format(f1))
    RootSearch.logger.debug('f2 = {0}'.format(f2))

    intersects = intersection_empty(xrectangle.diag(), f1, f2)
    vol = xrectangle.volume()

    if not intersects:
        xrectangle.privilege = current_privilege + 1.0

    return (xrectangle, intersects, vol,)


@cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, list_constraints=list, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               opt_level=cython.uint, logging=cython.bint, md_inter_search=list, start=cython.double, end=cython.double,
               time0=cython.double, intersect_result=object)
def multidim_intersection_search(xspace, listconstraints,
                                 oracle1,
                                 oracle2,
                                 epsilon=EPS,
                                 delta=DELTA,
                                 max_step=STEPS,
                                 blocking=False,
                                 sleep=0.0,
                                 opt_level=2,
                                 logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, int, bool, float, int, bool) -> ParResultSet
    md_inter_search = [multidim_intersection_search_opt_0,
                       multidim_intersection_search_opt_1,
                       multidim_intersection_search_opt_2]

    RootSearch.logger.info('Starting multidimensional intersection search')
    start = time.time()
    rs = md_inter_search[opt_level](xspace, listconstraints,
                                    oracle1, oracle2,
                                    epsilon=epsilon,
                                    delta=delta,
                                    max_step=max_step,
                                    blocking=blocking,
                                    sleep=sleep,
                                    logging=logging)
    end = time.time()
    time0 = end - start
    RootSearch.logger.info('Time multidim intersection search: ' + str(time0))

    return rs


# @cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, list_constraints=list, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               logging=cython.bint, n=cython.ushort, comparable=list, incomparable=list, incomparable_segment=list,
               border=object, error=tuple, vol_total=cython.double, vol_xrest=cython.double, vol_border=cython.double,
               step=cython.ulonglong, intersect_box=list, intersect_region=list, min_bound=cython.double,
               max_bound=cython.double, inside_bound=cython.bint, rect_diag=object, intersect_indicator=cython.short,
               end_min=tuple, end_max=tuple, mod_rectangle=object, y=object, y_in=object, y_cover=object,
               steps_binsearch=cython.ushort, tempdir=str, b0=object, b1=object, yrectangle=object,
               i=list, lower_rect=object, upper_rect=object, rect=object, rs=object, name=str)
def multidim_intersection_search_opt_0(xspace, list_constraints,
                                       oracle1, oracle2,
                                       epsilon=EPS,
                                       delta=DELTA,
                                       max_step=STEPS,
                                       blocking=False,
                                       sleep=0.0,
                                       logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    incomparable_segment = incomp_segment(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    border = SortedListWithKey(key=Rectangle.adjusted_volume)
    # border = SortedSet(key=Rectangle.volume)
    border.add(xspace)

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_xrest = 0.0
    vol_border = vol_total
    step = 0
    remaining_steps = max_step

    # intersection
    intersect_box = None
    intersect_region = None

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    f1 = oracle1.membership()
    f2 = oracle2.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle1))
        RootSearch.logger.debug('cloning: {0}'.format(oracle2))
        dict_man[proc.name] = (copy.deepcopy(oracle1), copy.deepcopy(oracle2), copy.deepcopy(list_constraints),
                               copy.deepcopy(incomparable), copy.deepcopy(incomparable_segment))

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder')
    while (vol_border >= vol_total * delta) and (step <= max_step) and (len(border) > 0) and (intersect_box is not None) \
            and (intersect_region is not None):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        # Process the 'border' until the number of maximum steps is reached
        step += chunk
        remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        args_pintersect_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pintersection_search_opt_0, args_pintersect_search)

        vol_xrest_list = (vol_xrest for (vol_xrest, _, _, _) in y_list)
        vol_xrest += sum(vol_xrest_list)

        for (_, local_border, local_intersect_box, local_intersect_region) in y_list:
            border.update(local_border)
            if local_intersect_box is not None:
                intersect_box = local_intersect_box
            if local_intersect_region is not None:
                intersect_region = local_intersect_region

        # Remove boxes in the boundary with volume 0
        # border = border[border.bisect_key_right(0.0):]
        del border[:border.bisect_key_left(0.0)]
        vol_border = vol_total - vol_xrest

        RootSearch.logger.info('{0}, {1}, {2}, {3}'.format(step, vol_border, vol_total, len(border)))

        if sleep > 0.0:
            rs = ParResultSet(border, [], intersect_region, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, [], intersect_region, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    RootSearch.logger.info('For pareto front intersection finding algorithm:')
    RootSearch.logger.info('remaining volume: {0}'.format(vol_border))
    RootSearch.logger.info('total volume: {0}'.format(vol_total))
    RootSearch.logger.info('percentage unexplored: {0}'.format((100.0 * vol_border) / vol_total))

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, intersect_region, intersect_box, xspace)


# @cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               logging=cython.bint, n=cython.ushort, comparable=list, incomparable=list, incomparable_segment=list,
               border=object, error=tuple, vol_total=cython.double, vol_xrest=cython.double, vol_border=cython.double,
               step=cython.ulonglong, intersect_box=list, intersect_region=list, min_bound=cython.double,
               max_bound=cython.double, inside_bound=cython.bint, rect_diag=object, intersect_indicator=cython.short,
               end_min=tuple, end_max=tuple, mod_rectangle=object, y=object, y_in=object, y_cover=object,
               steps_binsearch=cython.ushort, tempdir=str, b0=object, b1=object, yrectangle=object,
               lower_rect=object, upper_rect=object, rect=object, rs=object, name=str)
def multidim_intersection_search_opt_0_partial(xspace, list_constraints,
                                               oracle1, oracle2,
                                               epsilon=EPS,
                                               delta=DELTA,
                                               max_step=STEPS,
                                               blocking=False,
                                               sleep=0.0,
                                               logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, float, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    incomparable_segment = incomp_segment(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    border = SortedListWithKey(key=Rectangle.adjusted_volume)
    # border = SortedSet(key=Rectangle.volume)
    border.add(xspace)

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_xrest = 0.0
    vol_border = vol_total
    step = 0

    # intersection
    intersect_box = []
    intersect_region = []

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    f1 = oracle1.membership()
    f2 = oracle2.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle1))
        RootSearch.logger.debug('cloning: {0}'.format(oracle2))
        dict_man[proc.name] = (copy.deepcopy(oracle1), copy.deepcopy(oracle2),)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Ylow, Yup, Border, Total, nYlow, nYup, nBorder, BinSearch')
    while (vol_border >= vol_total * delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1

        xrectangle = border.pop()

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        min_bound, max_bound = bound_box_with_constraints(xrectangle, list_constraints)
        inside_bound = False
        rect_diag = xrectangle.diag()
        if (max_bound < 0.0) or (min_bound > 1.0) or (min_bound > max_bound) or (
                min_bound + (epsilon / 100.0) > max_bound):
            intersect_indicator = INTERNULL
            continue
        else:
            min_bound = max(0.0, min_bound)
            max_bound = min(1.0, max_bound)
            inside_bound = min_bound > 0.0 or max_bound < 1.0
            if inside_bound:
                min_bound += (epsilon / 100.0)
                max_bound -= (epsilon / 100.0)
                end_min = tuple(i + (j - i) * min_bound for i, j in zip(xrectangle.min_corner, xrectangle.max_corner))
                end_max = tuple(i + (j - i) * max_bound for i, j in zip(xrectangle.min_corner, xrectangle.max_corner))
                mod_rectangle = Rectangle(end_min, end_max)
                rect_diag = mod_rectangle.diag()
                y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(rect_diag, f1, f2,
                                                                                                    error, False)
            else:
                y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(rect_diag, f1, f2,
                                                                                                    error, False)
            RootSearch.logger.debug('y_in: {0}'.format(y_in))
            RootSearch.logger.debug('y_cover: {0}'.format(y_cover))

        if intersect_indicator >= INTER:
            intersect_box = [Rectangle(y_in.low, y_in.high)]
            intersect_region = [xrectangle]
            break
        elif intersect_indicator == INTERNULL:
            if inside_bound:  # (min_bound > 0 and max_bound < 1):
                yrectangle = Rectangle(rect_diag.low, rect_diag.high)
                i = interirect(incomparable_segment, yrectangle, xrectangle)
                lower_rect = Rectangle(xrectangle.min_corner, yrectangle.max_corner)
                upper_rect = Rectangle(yrectangle.min_corner, xrectangle.max_corner)
                vol_xrest += lower_rect.volume() + upper_rect.volume() - yrectangle.volume()
            else:
                vol_xrest += xrectangle.volume()  # Temporary hack. Must purge the implementation of the algo.
                continue
        else:
            b0 = Rectangle(xrectangle.min_corner, y_cover.low)
            vol_xrest += b0.volume()

            RootSearch.logger.debug('b0: {0}'.format(b0))

            b1 = Rectangle(y_cover.high, xrectangle.max_corner)
            vol_xrest += b1.volume()

            RootSearch.logger.debug('b1: {0}'.format(b1))

            yrectangle = Rectangle(y_cover.low, y_cover.high)
            i = irect(incomparable, yrectangle, xrectangle)

        args_pinter_empty_constr = ((rect, dict_man, copy.deepcopy(list_constraints)) for rect in i)
        inter_empty_constr = p.map(pintersection_empty_constrained, args_pinter_empty_constr)

        vols = (v for (_, inter, v) in inter_empty_constr if inter)
        vol_xrest += sum(vols)

        rect_filt = (r for (r, inter, _) in inter_empty_constr if not inter)
        border.update(rect_filt)

        RootSearch.logger.debug('irect: {0}'.format(i))

        # Remove boxes in the boundary with volume 0
        # border = border[border.bisect_key_right(0.0):]
        del border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_xrest

        RootSearch.logger.info(
            '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_total,
                                             len(border),
                                             steps_binsearch))
        if sleep > 0.0:
            rs = ParResultSet(border, [], intersect_region, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, [], intersect_region, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    RootSearch.logger.info('For pareto front intersection finding algorithm:')
    RootSearch.logger.info('remaining volume: {0}'.format(vol_border))
    RootSearch.logger.info('total volume: {0}'.format(vol_total))
    RootSearch.logger.info('percentage unexplored: {0}'.format((100.0 * vol_border) / vol_total))

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, intersect_region, intersect_box, xspace)


# @cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, list_constraints=list, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               logging=cython.bint, n=cython.ushort, comparable=list, incomparable=list, incomparable_segment=list,
               incomp_pos=list, incomp_neg_down=list, incomp_neg_up=list, border=object, error=tuple,
               vol_total=cython.double, vol_xrest=cython.double, vol_border=cython.double, vol_boxes=cython.double,
               step=cython.ulonglong, intersect_box=list, intersect_region=list, tempdir=str, xrectangle=object,
               current_privilege=cython.double, want_to_expand=cython.bint, y_in=object, y_cover=object,
               intersect_indicator=cython.short, steps_binsearch=cython.ushort, y=object, yrectangle=object,
               pos_box=object, neg_box1=object, neg_box2=object, i=list, lower_rect=object, upper_rect=object,
               b0=object, b1=object, rect=object, rs=object, name=str)
def multidim_intersection_search_opt_1(xspace, list_constraints,
                                       oracle1, oracle2,
                                       epsilon=EPS,
                                       delta=DELTA,
                                       max_step=STEPS,
                                       blocking=False,
                                       sleep=0.0,
                                       logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, int, bool, float, bool) -> ParResultSet
    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    incomparable_segment = incomp_segment(n)
    incomp_pos = incomp_segmentpos(n)
    incomp_neg_down = incomp_segment_neg_remove_down(n)
    incomp_neg_up = incomp_segment_neg_remove_up(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    border = SortedListWithKey(key=Rectangle.adjusted_volume)
    border.add(xspace)

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_xrest = 0.0
    vol_border = vol_total
    vol_boxes = vol_border
    step = 0
    remaining_steps = max_step

    # intersection
    intersect_box = []
    intersect_region = []

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    f1 = oracle1.membership()
    f2 = oracle2.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle1))
        RootSearch.logger.debug('cloning: {0}'.format(oracle2))
        dict_man[proc.name] = (copy.deepcopy(oracle1), copy.deepcopy(oracle2),
                               copy.deepcopy(incomparable), copy.deepcopy(incomparable_segment),
                               copy.deepcopy(incomp_pos), copy.deepcopy(incomp_neg_down), copy.deepcopy(incomp_neg_up))

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Border, Total, nBorder, BinSearch')
    while (vol_border >= vol_total * delta) and (step <= max_step) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        step += chunk
        remaining_steps = max_step - step

        # Process the 'border' until the number of maximum steps is reached

        # Search the intersection point of the Pareto front and the diagonal
        vol_boxes -= sum(xrectangle.volume() for xrectangle in slice_border)
        args_pintersect_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pintersection_search_opt_1, args_pintersect_search)

        # vol_xrest, vol_boxes, local_border, intersect_box, intersect_region
        vol_xrest_list = (vxrest for (vxrest, _, _, _, _) in y_list)
        vol_xrest += sum(vol_xrest_list)

        vol_boxes_list = (vboxes for (_, vboxes, _, _, _) in y_list)
        vol_boxes += sum(vol_boxes_list)

        for (_, _, local_border, local_intersect_box, local_intersect_region) in y_list:
            border.update(local_border)
            intersect_box.extend(local_intersect_box)
            intersect_region.extend(local_intersect_region)

        # Remove boxes in the boundary with volume 0
        # border = border[border.bisect_key_right(0.0):]
        del border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_xrest

        RootSearch.logger.info(
            '{0}, {1}, {2}, {3}'.format(step, vol_border, vol_boxes + vol_xrest, len(border)))
        if sleep > 0.0:
            rs = ParResultSet(border, [], intersect_region, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, [], intersect_region, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    RootSearch.logger.info('For pareto front intersection exploring algorithm (with holes):')
    RootSearch.logger.info('remaining volume: {0}'.format(vol_border))
    RootSearch.logger.info('total volume: {0}'.format(vol_total))
    RootSearch.logger.info('percentage unexplored: {0}'.format((100.0 * vol_border) / vol_total))

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, intersect_region, intersect_box, xspace)


# @cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, list_constraints=list, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               logging=cython.bint, n=cython.ushort, comparable=list, incomparable=list, incomparable_segment=list,
               incomp_pos=list, incomp_neg_down=list, incomp_neg_up=list, border=object, error=tuple,
               vol_total=cython.double, vol_xrest=cython.double, vol_border=cython.double, vol_boxes=cython.double,
               step=cython.ulonglong, intersect_box=list, intersect_region=list, tempdir=str, xrectangle=object,
               current_privilege=cython.double, want_to_expand=cython.bint, y_in=object, y_cover=object,
               intersect_indicator=cython.short, steps_binsearch=cython.ushort, y=object, yrectangle=object,
               pos_box=object, neg_box1=object, neg_box2=object, lower_rect=object, upper_rect=object,
               b0=object, b1=object, rect=object, rs=object, name=str)
def multidim_intersection_search_opt_1_partial(xspace, list_constraints,
                                               oracle1, oracle2,
                                               epsilon=EPS,
                                               delta=DELTA,
                                               max_step=STEPS,
                                               blocking=False,
                                               sleep=0.0,
                                               logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, float, bool, float, bool) -> ParResultSet
    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    comparable = comp(n)
    incomparable = incomp(n)
    incomparable_segment = incomp_segment(n)
    incomp_pos = incomp_segmentpos(n)
    incomp_neg_down = incomp_segment_neg_remove_down(n)
    incomp_neg_up = incomp_segment_neg_remove_up(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    border = SortedListWithKey(key=Rectangle.adjusted_volume)
    border.add(xspace)

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_xrest = 0.0
    vol_border = vol_total
    vol_boxes = vol_border
    step = 0

    # intersection
    intersect_box = []
    intersect_region = []

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    f1 = oracle1.membership()
    f2 = oracle2.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle1))
        RootSearch.logger.debug('cloning: {0}'.format(oracle2))
        dict_man[proc.name] = (copy.deepcopy(oracle1), copy.deepcopy(oracle2),)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))
    RootSearch.logger.debug('comparable: {0}'.format(comparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Border, Total, nBorder, BinSearch')
    while (vol_border >= vol_total * delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1

        xrectangle = border.pop()
        vol_boxes -= xrectangle.volume()

        current_privilege = xrectangle.privilege

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        want_to_expand = True
        y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(xrectangle.diag(), f1, f2,
                                                                                            error, want_to_expand)

        if intersect_indicator == NO_INTER:
            y = y_in
        else:
            y = y_cover

        yrectangle = Rectangle(y.low, y.high)
        RootSearch.logger.debug('y: {0}'.format(y))

        if intersect_indicator == INTERFULL:
            intersect_box.append(Rectangle(y.low, y.high))
            vol_xrest += xrectangle.volume()
            vol_border = vol_total - vol_xrest
            RootSearch.logger.info(
                '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_xrest + vol_boxes, len(border), steps_binsearch))
            continue
        elif intersect_indicator == INTER:
            pos_box = Rectangle(y_in.low, y_in.high)
            neg_box1 = Rectangle(xrectangle.min_corner, y_cover.low)
            neg_box2 = Rectangle(y_cover.high, xrectangle.max_corner)
            intersect_box.append(pos_box)
            intersect_region.append(xrectangle)

            i = pos_neg_box_gen(incomp_pos, incomp_neg_down, incomp_neg_up, y_in, y_cover, xrectangle)

            vol_xrest += pos_box.volume() + neg_box1.volume() + neg_box2.volume()
        elif intersect_indicator == NO_INTER:
            i = interirect(incomparable_segment, yrectangle, xrectangle)
            lower_rect = Rectangle(xrectangle.min_corner, yrectangle.max_corner)
            upper_rect = Rectangle(yrectangle.min_corner, xrectangle.max_corner)
            vol_xrest += lower_rect.volume() + upper_rect.volume() - yrectangle.volume()
        elif intersect_indicator == INTERNULL:
            vol_xrest += xrectangle.volume()
            vol_border = vol_total - vol_xrest
            RootSearch.logger.info(
                '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_boxes + vol_xrest, len(border), steps_binsearch))
            continue
        else:
            b0 = Rectangle(xrectangle.min_corner, y.low)
            vol_xrest += b0.volume()
            RootSearch.logger.debug('b0: {0}'.format(b0))

            b1 = Rectangle(y.high, xrectangle.max_corner)
            vol_xrest += b1.volume()
            RootSearch.logger.debug('b1: {0}'.format(b1))

            i = irect(incomparable, yrectangle, xrectangle)

        args_pinter_empty = ((xrectangle, dict_man, current_privilege) for xrectangle in i)
        inter_empty = p.map(pintersection_empty, args_pinter_empty)

        vols = (v for (_, inter, v) in inter_empty if inter)
        vol_xrest += sum(vols)

        vols = (v for (_, inter, v) in inter_empty if not inter)
        vol_boxes += sum(vols)

        rect_filt = (r for (r, inter, _) in inter_empty if not inter)
        border.update(rect_filt)

        RootSearch.logger.debug('irect: {0}'.format(i))

        # Remove boxes in the boundary with volume 0
        # border = border[border.bisect_key_right(0.0):]
        del border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_xrest

        RootSearch.logger.info(
            '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_boxes + vol_xrest, len(border), steps_binsearch))
        if sleep > 0.0:
            rs = ParResultSet(border, [], intersect_region, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, [], intersect_region, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    RootSearch.logger.info('For pareto front intersection exploring algorithm (with holes):')
    RootSearch.logger.info('remaining volume: {0}'.format(vol_border))
    RootSearch.logger.info('total volume: {0}'.format(vol_total))
    RootSearch.logger.info('percentage unexplored: {0}'.format((100.0 * vol_border) / vol_total))

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, intersect_region, intersect_box, xspace)


# @cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, list_constraints=list, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               logging=cython.bint, n=cython.ushort, incomparable=list, incomparable_segment=list,
               border=object, error=tuple, vol_total=cython.double, vol_xrest=cython.double, vol_border=cython.double,
               vol_boxes=cython.double, step=cython.ulonglong, remaining_steps=cython.ulonglong, intersect_box=list,
               intersect_region=list, num_proc=cython.ushort, p=object, man=object, tempdir=str,
               chunk=cython.ushort, rs=object, name=str)
def multidim_intersection_search_opt_2(xspace, list_constraints,
                                       oracle1, oracle2,
                                       epsilon=EPS,
                                       delta=DELTA,
                                       max_step=STEPS,
                                       blocking=False,
                                       sleep=0.0,
                                       logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, int, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    incomparable = incomp(n)
    incomparable_segment = incomp_segment(n)
    # comparable = comp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    # border = SortedListWithKey(key=Rectangle.adjusted_volume)
    border = SortedSet(key=Rectangle.adjusted_volume)
    border.add(xspace)

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_xrest = 0.0
    vol_border = vol_total
    vol_boxes = vol_border
    step = 0
    remaining_steps = max_step

    # intersection
    intersect_box = []
    intersect_region = []

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    f1 = oracle1.membership()
    f2 = oracle2.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle1))
        RootSearch.logger.debug('cloning: {0}'.format(oracle2))
        dict_man[proc.name] = (copy.deepcopy(oracle1), copy.deepcopy(oracle2),
                               copy.deepcopy(incomparable), copy.deepcopy(incomparable_segment))

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Border, Total, nBorder')
    while (vol_border >= vol_total * delta) and (step <= max_step) and (len(border) > 0):
        # Divide the list of incomparable rectangles in chunks of 'num_proc' elements.
        # We get the 'num_proc' elements with highest volume.

        chunk = min(num_proc, remaining_steps)
        chunk = min(chunk, len(border))

        # Take the rectangles with highest volume
        slice_border = border[-chunk:]

        # Remove elements of the slice_border from the original border
        # border = list(set(border).difference(set(slice_border)))
        border -= slice_border

        # Process the 'border' until the number of maximum steps is reached
        step += chunk
        remaining_steps = max_step - step

        # Search the intersection point of the Pareto front and the diagonal
        vol_boxes -= sum(xrectangle.volume() for xrectangle in slice_border)
        args_pintersect_search = ((xrectangle, dict_man, epsilon, n) for xrectangle in slice_border)
        y_list = p.map(pintersection_search_opt_2, args_pintersect_search)

        # vol_xrest, vol_boxes, local_border, intersect_box, intersect_region
        vol_xrest_list = (vxrest for (vxrest, _, _, _, _) in y_list)
        vol_xrest += sum(vol_xrest_list)

        vol_boxes_list = (vboxes for (_, vboxes, _, _, _) in y_list)
        vol_boxes += sum(vol_boxes_list)

        for (_, _, local_border, local_intersect_box, local_intersect_region) in y_list:
            border.update(local_border)
            intersect_box.extend(local_intersect_box)
            intersect_region.extend(local_intersect_region)

        # Remove boxes in the boundary with volume 0
        # border = border[border.bisect_key_right(0.0):]
        del border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_xrest

        RootSearch.logger.info('{0}, {1}, {2}, {3}'.format(step, vol_border, vol_xrest + vol_boxes, len(border)))
        if sleep > 0.0:
            rs = ParResultSet(border, [], intersect_region, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, [], intersect_region, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    RootSearch.logger.info('For pareto front intersection exploring algorithm (with overlap):')
    RootSearch.logger.info('remaining volume: {0}'.format(vol_border))
    RootSearch.logger.info('total volume: {0}'.format(vol_total))
    RootSearch.logger.info('percentage unexplored: {0}'.format((100.0 * vol_border) / vol_total))

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, intersect_region, intersect_box, xspace)


# @cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, list_constraints=list, oracle1=object, oracle2=object, epsilon=cython.double,
               delta=cython.double, max_step=cython.ulonglong, blocking=cython.bint, sleep=cython.double,
               logging=cython.bint, n=cython.ushort, incomparable=list, incomparable_segment=list,
               border=object, error=tuple, vol_total=cython.double, vol_xrest=cython.double, vol_border=cython.double,
               vol_boxes=cython.double, step=cython.ulonglong, intersect_box=list, intersect_region=list,
               num_proc=cython.ushort, p=object, man=object, proc=object, tempdir=str, current_privilege=cython.double,
               want_to_expand=cython.bint, y_in=object, y_cover=object, intersect_indicator=cython.short,
               steps_binsearch=cython.ushort, y=object, yrectangle=object, pos_box=object, neg_box1=object,
               neg_box2=object, lower_rect=object, upper_rect=object, b0=object, b1=object, rect=object,
               rs=object, name=str)
def multidim_intersection_search_opt_2_partial(xspace, list_constraints,
                                               oracle1, oracle2,
                                               epsilon=EPS,
                                               delta=DELTA,
                                               max_step=STEPS,
                                               blocking=False,
                                               sleep=0.0,
                                               logging=True):
    # type: (Rectangle, list, Oracle, Oracle, float, float, float, bool, float, bool) -> ParResultSet

    # Xspace is a particular case of maximal rectangle
    # Xspace = [min_corner, max_corner]^n = [0, 1]^n
    # xspace.min_corner = (0,) * n
    # xspace.max_corner = (1,) * n

    # Dimension
    n = xspace.dim()

    # Set of comparable and incomparable rectangles, represented by 'alpha' indices
    incomparable = incomp(n)
    incomparable_segment = incomp_segment(n)
    # comparable = comp(n)
    # comparable = [zero, one]
    # incomparable = list(set(alpha) - set(comparable))
    # with:
    # zero = (0_1,...,0_n)
    # one = (1_1,...,1_n)

    # List of incomparable rectangles
    # border = [xspace]
    border = SortedListWithKey(key=Rectangle.adjusted_volume)
    border.add(xspace)

    error = (epsilon,) * n
    vol_total = xspace.volume()
    vol_xrest = 0.0
    vol_border = vol_total
    vol_boxes = vol_border
    step = 0

    # intersection
    intersect_box = []
    intersect_region = []

    num_proc = cpu_count()
    p = Pool(num_proc)

    # oracle function
    f1 = oracle1.membership()
    f2 = oracle2.membership()

    man = Manager()
    dict_man = man.dict()

    # 'f = oracle.membership()' is not thread safe!
    # Create a copy of 'oracle' for each concurrent process
    for proc in mp.active_children():
        RootSearch.logger.debug('cloning: {0}'.format(oracle1))
        RootSearch.logger.debug('cloning: {0}'.format(oracle2))
        dict_man[proc.name] = (copy.deepcopy(oracle1), copy.deepcopy(oracle2),)

    RootSearch.logger.debug('xspace: {0}'.format(xspace))
    RootSearch.logger.debug('vol_border: {0}'.format(vol_border))
    RootSearch.logger.debug('delta: {0}'.format(delta))
    RootSearch.logger.debug('step: {0}'.format(step))
    RootSearch.logger.debug('incomparable: {0}'.format(incomparable))

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()

    RootSearch.logger.info('Report\nStep, Border, Total, nBorder, BinSearch')
    while (vol_border >= vol_total * delta) and (step <= max_step) and (len(border) > 0):
        step = step + 1

        xrectangle = border.pop()
        vol_boxes -= xrectangle.volume()

        current_privilege = xrectangle.privilege

        RootSearch.logger.debug('xrectangle: {0}'.format(xrectangle))
        RootSearch.logger.debug('xrectangle.volume: {0}'.format(xrectangle.volume()))
        RootSearch.logger.debug('xrectangle.norm: {0}'.format(xrectangle.norm()))

        want_to_expand = True
        y_in, y_cover, intersect_indicator, steps_binsearch = intersection_expansion_search(xrectangle.diag(), f1, f2,
                                                                                            error, want_to_expand)
        if intersect_indicator == NO_INTER:
            y = y_in
        else:
            y = y_cover
        yrectangle = Rectangle(y.low, y.high)
        RootSearch.logger.debug('y: {0}'.format(y))

        if intersect_indicator == INTERFULL:
            intersect_box.append(Rectangle(y.low, y.high))
            vol_xrest += xrectangle.volume()
            vol_border = vol_total - vol_xrest
            RootSearch.logger.info(
                '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_xrest + vol_boxes,
                                                 len(border),
                                                 steps_binsearch))
            continue
        elif intersect_indicator == INTER:
            pos_box = Rectangle(y_in.low, y_in.high)
            neg_box1 = Rectangle(xrectangle.min_corner, y_cover.low)
            neg_box2 = Rectangle(y_cover.high, xrectangle.max_corner)
            intersect_box.append(pos_box)
            intersect_region.append(xrectangle)

            i = pos_overlap_box_gen(incomparable, incomparable_segment, y_in, y_cover, xrectangle)

            vol_xrest += pos_box.volume() + neg_box1.volume() + neg_box2.volume()
        elif intersect_indicator == NO_INTER:
            i = interirect(incomparable_segment, yrectangle, xrectangle)
            lower_rect = Rectangle(xrectangle.min_corner, yrectangle.max_corner)
            upper_rect = Rectangle(yrectangle.min_corner, xrectangle.max_corner)
            vol_xrest += lower_rect.volume() + upper_rect.volume() - yrectangle.volume()
        elif intersect_indicator == INTERNULL:
            vol_xrest += xrectangle.volume()
            vol_border = vol_total - vol_xrest
            RootSearch.logger.info(
                '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_boxes + vol_xrest,
                                                 len(border),
                                                 steps_binsearch))
            continue
        else:
            b0 = Rectangle(xrectangle.min_corner, y.low)
            vol_xrest += b0.volume()
            RootSearch.logger.debug('b0: {0}'.format(b0))

            b1 = Rectangle(y.high, xrectangle.max_corner)
            vol_xrest += b1.volume()
            RootSearch.logger.debug('b1: {0}'.format(b1))

            i = irect(incomparable, yrectangle, xrectangle)

        args_pinter_empty = ((rect, dict_man, current_privilege) for rect in i)
        # inter_empty = p.map(pintersection_empty, args_pinter_empty)
        #
        # vols = (v for (_, inter, v) in inter_empty if inter)
        # vol_xrest += sum(vols)
        #
        # vols = (v for (_, inter, v) in inter_empty if not inter)
        # vol_boxes += sum(vols)
        #
        # rect_filt = [r for (r, inter, _) in inter_empty if not inter]
        # border.update(rect_filt)
        inter_empty = p.imap_unordered(pintersection_empty, args_pinter_empty)

        for rect, inter, v in inter_empty:
            if inter:
                vol_xrest += v
            else:
                vol_boxes += v
                border.add(rect)

        RootSearch.logger.debug('irect: {0}'.format(i))

        # Remove boxes in the boundary with volume 0
        # border = border[border.bisect_key_right(0.0):]
        del border[:border.bisect_key_left(0.0)]

        vol_border = vol_total - vol_xrest

        RootSearch.logger.info(
            '{0}, {1}, {2}, {3}, {4}'.format(step, vol_border, vol_boxes + vol_xrest,
                                             len(border),
                                             steps_binsearch))
        if sleep > 0.0:
            rs = ParResultSet(border, [], intersect_region, xspace)
            if n == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif n == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, [], intersect_region, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    RootSearch.logger.info('For pareto front intersection exploring algorithm (with overlap):')
    RootSearch.logger.info('remaining volume: {0}'.format(vol_border))
    RootSearch.logger.info('total volume: {0}'.format(vol_total))
    RootSearch.logger.info('percentage unexplored: {0}'.format((100.0 * vol_border) / vol_total))

    # Stop multiprocessing
    p.close()
    p.join()

    return ParResultSet(border, intersect_region, intersect_box, xspace)


########################################
######## ADVANCED METHOD: BMNN22 #######
########################################

##############################
# opt_1 = Dynamic size cell method
# opt_0 = Fixed size cell method
##############################

@cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, oracles=list, num_samples=cython.int, num_cells=cython.int, blocking=cython.bint,
               sleep=cython.double, opt_level=cython.uint, logging=cython.bint, md_search=list, start=cython.double,
               end=cython.double, time0=cython.double, rs=object)
def multidim_search_BMNN22(xspace,
                           oracles,
                           num_samples,
                           num_cells,
                           blocking=False,
                           sleep=0.0,
                           opt_level=0,
                           logging=True):
    # type: (Rectangle, list[Oracle], int, int, bool, float, int, bool) -> ResultSet

    RootSearch.logger.info('Starting multidimensional search (BMNN22)')
    start = time.time()
    if opt_level == 0:  # Fixed cell creation
        rs = multidim_search_BMNN22_opt_0(xspace,
                                          oracles,
                                          num_samples=num_samples,
                                          num_cells=num_cells,
                                          blocking=blocking,
                                          sleep=sleep,
                                          logging=logging)
    else:  # Dinamyc cell creation
        ps = 0.95
        g = np.multiply(xspace.diag_vector(), 1 / 10)
        rs = multidim_search_BMNN22_opt_1(xspace,
                                          oracles,
                                          num_samples=num_samples,
                                          blocking=blocking,
                                          sleep=sleep,
                                          logging=logging,
                                          ps=ps,
                                          g=tuple(g))
    end = time.time()
    time0 = end - start
    RootSearch.logger.info('Time multidim search (Pareto front): ' + str(time0))

    return rs


########################################################################################################################

# Fixed size cell method
def process_fix(args: tuple[Rectangle,
                            list[OracleSTLeLib],
                            int,
                            int]) -> bool:
    cell, oracles, num_samples, d = args

    fs = [ora.membership() for ora in oracles]

    # Take num_samples uniformly between cell.min_corner and cell.max_corner
    samples = cell.uniform_sampling(num_samples)
    # Call the oracle with the current sample
    res = any(all(f(sample) for f in fs) for sample in samples)

    return res


@cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, oracles=list, num_samples=cython.uint, num_cells=cython.uint,
               blocking=cython.bint, sleep=cython.double, logging=cython.bint, cells=list,
               border=list, green=list, red=list, d=cython.uint, p=object, args=tuple, green_cells=list,
               step=cython.uint, vol_green=cython.uint, vol_red=cython.uint, vol_border=cython.uint,
               tempdir=cython.basestring,
               rs=object)
def multidim_search_BMNN22_opt_0(xspace: Rectangle,
                                 oracles: list[Oracle],
                                 num_samples: int,
                                 num_cells: int,
                                 blocking: bool = False,
                                 sleep: float = 0.0,
                                 logging: bool = True) -> ParResultSet:
    cells = xspace.cell_partition(num_cells)
    border = list()
    green = list()
    red = list()
    d = xspace.dim()
    step = 0

    p = Pool(cpu_count())
    args = ((cell, copy.deepcopy(oracles), num_samples, d) for cell in cells)
    green_cells = p.map(process_fix, args)
    step = step + 1
    vol_green, vol_red, vol_border = 0.0, 0.0, 0.0  # Area of all the regions for debugging purposess
    tempdir = tempfile.mkdtemp()
    RootSearch.logger.info('Report\nStep, Red, Green, Border, Total, nRed, nGreen, nBorder')
    RootSearch.logger.info(
        '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(step, vol_red, vol_green, vol_border, xspace.volume(), len(red),
                                                        len(green), len(border)))  # 0th step
    for i, cell in enumerate(cells):
        if green_cells[i]:
            green.append(cell)
            vol_green = vol_green + cell.volume()
        else:
            red.append(cell)
            vol_red = vol_red + cell.volume()
            RootSearch.logger.info(
                '{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}'.format(step, vol_red, vol_green, vol_border, xspace.volume(),
                                                            len(red), len(green), len(border)))
        # Visualization
        if sleep > 0.0:
            rs = ParResultSet(border, red, green, xspace)
            if d == 2:
                rs.plot_2D_light(blocking=blocking, sec=sleep, opacity=0.7)
            elif d == 3:
                rs.plot_3D_light(blocking=blocking, sec=sleep, opacity=0.7)

        if logging:
            rs = ParResultSet(border, red, green, xspace)
            name = os.path.join(tempdir, str(step))
            rs.to_file(name)

    p.close()
    p.join()
    return ParResultSet(border=border, ylow=red, yup=green, xspace=xspace)


# Dynamic size cell method
def process_dyn(args: tuple[Rectangle,
                            list[OracleSTLeLib],
                            int,
                            int,
                            float,
                            tuple[float]]) -> tuple[Rectangle, bool | None]:
    cell, oracles, num_samples, d, ps, g = args

    fs = [ora.membership() for ora in oracles]

    # Take num_samples uniformly between cell.min_corner and cell.max_corner
    samples = cell.uniform_sampling(num_samples)
    all_fs_in_sample = (all(f(s) for f in fs) for s in samples)
    counter = sum(all_fs_in_sample)
    if counter == 0:
        return cell, False
    elif counter / num_samples >= ps or less_equal(cell.diag_vector(), g):
        return cell, True
    return cell, None


@cython.ccall
@cython.returns(object)
@cython.locals(xspace=object, oracles=list, num_samples=cython.uint, num_cells=cython.uint, g=tuple,
               blocking=cython.bint, sleep=cython.double, logging=cython.bint, ps=cython.double, m=cython.uint,
               args=tuple, cols_list=list, green=list, red=list, border=list, step=cython.uint,
               tempdir=cython.basestring)
def multidim_search_BMNN22_opt_1(xspace: Rectangle,
                                 oracles: list[Oracle],
                                 num_samples: int,
                                 g: tuple[float],
                                 blocking: bool = False,
                                 sleep: float = 0.0,
                                 logging: bool = True,
                                 ps: float = 0.95) -> ParResultSet:
    # type: (Rectangle, list, int, tuple, bool, float, bool, float) -> ParResultSet

    green = list()
    red = list()
    border = list()
    step = 0
    d = xspace.dim()
    p = Pool(cpu_count())

    # Create temporary directory for storing the result of each step
    tempdir = tempfile.mkdtemp()
    cell_list = [xspace]

    while len(cell_list) > 0:
        args = ((cell, copy.deepcopy(oracles), num_samples, d, ps, g) for cell in cell_list)
        cols_list = p.map(process_dyn, args)
        cell_list = list()
        for (cell, is_green) in cols_list:
            if is_green is None:
                n = pow(2, d)
                cell_list = cell_list + cell.cell_partition_bin(n)
            elif is_green:
                green.append(cell)
            else:
                red.append(cell)

    if logging:
        rs = ParResultSet(border, red, green, xspace)
        name = os.path.join(tempdir, str(step))
        rs.to_file(name)
    
    p.close()
    p.join()
    return ParResultSet(border, red, green, xspace)
