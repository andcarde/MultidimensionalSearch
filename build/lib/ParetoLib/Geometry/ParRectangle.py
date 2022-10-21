# -*- coding: utf-8 -*-
# Copyright (c) 2018 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""ParRectangle.

This module introduces a set of operations for parallelizing
the creation of comparable and incomparable rectangles of the space.
"""
from multiprocessing import Pool, cpu_count
import cython

from ParetoLib.Geometry.Rectangle import Rectangle, brect
from ParetoLib.Geometry.Point import dim


############################################################################
# Parallel version for the computation of incomparable rectangles in a space
############################################################################

@cython.ccall
@cython.locals(alpha=tuple, yrectangle=object, xspace=object, rect=object)
@cython.returns(object)
def pbrect(args):
    # type: (iter) -> Rectangle
    """
    Synonym of Rectangle.brect(alpha, yrectangle, xspace)
    """
    alpha, yrectangle, xspace = args
    return brect(alpha, yrectangle, xspace)


@cython.locals(nproc=cython.ushort, pool=object)
def pirect(alphaincomp, yrectangle, xspace):
    # type: (list, Rectangle, Rectangle) -> iter
    """
    Synonym of Rectangle.irect(alphaincomp, yrectangle, xspace)
    """
    assert (dim(yrectangle.min_corner) == dim(yrectangle.max_corner)), \
        'xrectangle.min_corner and xrectangle.max_corner do not share the same dimension'
    assert (dim(xspace.min_corner) == dim(xspace.max_corner)), \
        'xspace.min_corner and xspace.max_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.min_corner)), \
    #    'alphaincomp_list and yrectangle.min_corner do not share the same dimension'
    # assert (dim(alphaincomp_list) == dim(yrectangle.max_corner)), \
    #    'alphaincomp_list and yrectangle.max_corner do not share the same dimension'

    nproc = cpu_count()
    pool = Pool(nproc)

    args_i = ((alphaincomp_i, yrectangle, xspace) for alphaincomp_i in alphaincomp)
    # parallel_results = pool.map(pbrect, args_i)
    parallel_results = pool.imap_unordered(pbrect, args_i)

    # Stop multiprocessing
    pool.close()
    pool.join()

    return parallel_results


#############################################################################################
# Wrappers for methods of the Rectangle class.
# The 'multiprocessing' library requires 'pickable' methods for the parallelization of tasks;
# i.e., these wrappers.
#############################################################################################

@cython.ccall
@cython.locals(rect=object)
@cython.returns(cython.double)
def pvol(rect):
    # type: (Rectangle) -> float
    """
    Synonym of Rectangle.volume()
    """
    return rect.volume()


@cython.ccall
@cython.returns(list)
def pvertices(rect):
    # type: (Rectangle) -> list
    """
    Synonym of Rectangle.vertices()
    """
    return rect.vertices()


@cython.ccall
@cython.locals(rect=object, xpoint=tuple)
@cython.returns(cython.bint)
def pinside(args):
    # type: (iter) -> bool
    """
    Synonym of Rectangle.inside(xpoint)
    """
    rect, xpoint = args
    return rect.inside(xpoint)
