# -*- coding: utf-8 -*-
# Copyright (c) 2018 J. Alvarez-Jarreta and C.J. Brasher
#
# This file is part of the LipidFinder software tool and governed by the
# 'MIT License'. Please see the LICENSE file that should have been
# included as part of this software.
"""Python 3 compatibility tools.

The inclusion of this module provides full support for this tools in
Python 2.7 and Python 3.3 (or newer).

The contents are the same of _py3k.__init__ file from MEvoLib
[J. Alvarez-Jarreta et al. 2017].
"""

import os
import sys
import platform

if sys.version_info[0] >= 3:
    # Code for Python 3
    from builtins import open, zip, map, filter, range, input, round, max, min
    import codecs, io
    from functools import reduce

    def max_integer_value():
        return sys.maxsize

    def red(function, sequence):
        """Call 'reduce', which applies 'function' over all the elements of the sequence"""
        return reduce(function, sequence)

    def _is_int_or_long(value):
        """Return True if 'value' is an integer, False otherwise."""
        # There are no longs on Python 3
        return isinstance(value, int)


    def viewkeys(dictionary):
        """Return a view of the keys of 'dictionary'."""
        return dictionary.keys()


    def viewvalues(dictionary):
        """Return a view of the values of 'dictionary'."""
        return dictionary.values()


    def viewitems(dictionary):
        """Return a view of the items of 'dictionary'."""
        return dictionary.items()


    def get_stdout_matlab():
        """Return a Standard output stream for Matlab."""
        return io.StringIO()


    def get_stderr_matlab():
        """Return a Standard error stream for Matlab."""
        return io.StringIO()

    # On Python 3 urllib, urllib2, and urlparse were merged
    from urllib.request import urlopen, Request, urlretrieve, urlparse
    from urllib.parse import urlencode, quote
    from urllib.error import HTTPError, URLError
    # On Python 3 subprocess.DEVNULL exists
    from subprocess import DEVNULL
    # On Python 3, this will be a unicode StringIO
    from io import StringIO
    from tempfile import TemporaryDirectory
else:  # sys.version_info[0] < 3
    # Code for Python 2
    from __builtin__ import open, basestring, unicode, round, max, min, reduce
    # Import Python 3 like iterator functions:
    from future_builtins import zip, map, filter
    from __builtin__ import xrange as range
    from __builtin__ import raw_input as input
    import StringIO

    def max_integer_value():
        return sys.maxint

    def red(function, sequence):
        """Call 'reduce', which applies 'function' over all the elements of the sequence"""
        return reduce(function, sequence)

    def _is_int_or_long(value):
        """Return True if 'value' is an integer or long, False
        otherwise.
        """
        return isinstance(value, (int, long))


    def viewkeys(dictionary):
        """Return a view of the keys of 'dictionary'."""
        return dictionary.viewkeys()


    def viewvalues(dictionary):
        """Return a view of the values of 'dictionary'."""
        return dictionary.viewvalues()


    def viewitems(dictionary):
        """Return a view of the items of 'dictionary'."""
        return dictionary.viewitems()

    def get_stdout_matlab():
        """Return a Standard output stream for Matlab."""
        return StringIO.StringIO()

    def get_stderr_matlab():
        """Return a Standard error stream for Matlab."""
        return StringIO.StringIO()

    # Under urllib.request on Python 3:
    from urllib2 import urlopen, Request
    from urllib import urlretrieve
    from urlparse import urlparse
    # Under urllib.parse on Python 3:
    from urllib import urlencode, quote
    # Under urllib.error on Python 3:
    from urllib2 import HTTPError, URLError

    # On Python 2 subprocess.DEVNULL doesn't exist
    DEVNULL = open(os.path.devnull, 'w')
    # On Python 2 this will be a (bytes) string based handle.
    # Note this doesn't work as it is unicode based:
    # from io import StringIO
    # try:
    #     from cStringIO import StringIO
    # except ImportError:
    #     from StringIO import StringIO
    # try:
    #     input = raw_input
    # except NameError:
    #     pass
    # There is no TemporaryDirectory class in the temp library
    from TemporaryDirectory import TemporaryDirectory

# Required for limiting the recursion in NDTree.
# "resource" library is only available on linux/unix
if platform.system() == 'Linux' or platform.system() == 'Darwin':
    from resource import setrlimit, RLIMIT_STACK, RLIM_INFINITY

    def set_limit(max_rec):
        setrlimit(RLIMIT_STACK, [0x100 * max_rec, RLIM_INFINITY])

elif platform.system() == 'Windows':

    def set_limit(max_rec):
        None
else:
    raise RuntimeError('OS Platform \'{0}\' not compatible for "resource".\n'.format(platform.system()))


if sys.platform == "win32":
    # Can't use commands.getoutput on Python 2, Unix only/broken:
    # http://bugs.python.org/issue15073
    # Can't use subprocess.getoutput on Python 3, Unix only/broken:
    # http://bugs.python.org/issue10197
    def getoutput(cmd):
        import subprocess
        child = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True, shell=False)
        stdout, stderr = child.communicate()
        # Remove trailing "\n" to match the Unix function
        return stdout.rstrip("\n")
elif sys.version_info[0] >= 3:
    # Use subprocess.getoutput on Python 3
    from subprocess import getoutput
else:  # sys.version_info[0] <= 2
    # Use commands.getoutput on Python 2
    from commands import getoutput


def cmp_to_key(mycmp):
    """
    Convert a cmp= function (2 input parameters) into a key= function (1 input parameter).
    Useful for sorting functions (i.e., sorted(_, key=cmp_to_key())
    """
    class K:
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
