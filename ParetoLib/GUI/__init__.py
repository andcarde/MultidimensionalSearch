# -*- coding: utf-8 -*-
# Copyright (c) 2022 J.I. Requeno et al
#
# This file is part of the ParetoLib software tool and governed by the
# 'GNU License v3'. Please see the LICENSE file that should have been
# included as part of this software.
"""GUI package.

This package introduces a set of modules for manipulating the GUI.
"""

import logging
import sys
from decimal import getcontext

__name__ = 'GUI'
__all__ = ['Window']

# Logging configuration
# logging.basicConfig(format='%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create handlers
handler = logging.StreamHandler()

# Create formatter and add it to handler
form = logging.Formatter('%(message)s')
handler.setFormatter(form)

# Add handler to the logger
logger.addHandler(handler)
