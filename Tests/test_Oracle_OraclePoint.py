import os
import tempfile as tf
import copy
import unittest
import numpy as np

from ParetoLib.Oracle.OraclePoint import OraclePoint
from ParetoLib.Oracle.NDTree import NDTree


###############
# OraclePoint #
###############

class OraclePointTestCase(unittest.TestCase):
    def setUp(self):
        # type: (OraclePointTestCase) -> None
        self.files_to_clean = set()

    def tearDown(self):
        # type: (OraclePointTestCase) -> None
        for filename in self.files_to_clean:
            if os.path.isfile(filename):
                os.remove(filename)

    def add_file_to_clean(self, filename):
        # type: (OraclePointTestCase, str) -> None
        self.files_to_clean.add(filename)

    # Test ND-Tree structure
    def test_populating_NDTree(self,
                               min_corner=0.0,
                               max_corner=1.0):
        # type: (OraclePointTestCase, float, float) -> None

        def f1(x):
            return 1 / x if x > 0.0 else 1000

        def f2(x):
            return 0.1 + 1 / x if x > 0.0 else 1001

        def f3(x):
            return 0.2 + 1 / x if x > 0.0 else 1002

        xs = np.arange(min_corner, max_corner, 0.1)
        y1s = [f1(x) for x in xs]
        y2s = [f2(x) for x in xs]
        y3s = [f3(x) for x in xs]

        ND1 = NDTree()
        ND2 = NDTree()

        self.assertTrue(ND1.is_empty())
        self.assertEqual(ND1, ND2)

        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.update_point(point)
            ND2.update_point(point)

        self.assertEqual(ND1, ND2)

        # ND1 should remain constant when we insert the same point twice
        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.update_point(point)

        self.assertEqual(ND1, ND2)
        self.assertEqual(ND1.dim(), ND2.dim())
        self.assertEqual(ND1.get_points(), ND2.get_points())
        self.assertEqual(ND1.get_rectangle(), ND2.get_rectangle())

        # ND1 should change when we insert new dominanting points
        for x, y in zip(xs, y2s):
            point = (x, y)
            ND1.update_point(point)

        self.assertNotEqual(ND1, ND2)

        # ND1 should change when we insert new dominanting points
        for x, y in zip(xs, y1s):
            point = (x, y)
            ND1.update_point(point)

        self.assertNotEqual(ND1, ND2)

        oldND1 = copy.deepcopy(ND1)

        # ND1 should remain constant when we insert dominated points
        for x, y in zip(xs, y3s):
            point = (x, y)
            ND1.update_point(point)

        self.assertEqual(ND1, oldND1)
        self.assertNotEqual(ND1, ND2)

    def test_files_NDTree(self):
        # type: (OraclePointTestCase) -> None
        self.read_write_ndtree_files(read_human_readable=True, write_human_readable=True)
        self.read_write_ndtree_files(read_human_readable=False, write_human_readable=False)

    def read_write_ndtree_files(self,
                                min_corner=0.0,
                                max_corner=1.0,
                                read_human_readable=False,
                                write_human_readable=False):
        # type: (OraclePointTestCase, float, float, bool) -> None

        def f1(x):
            return 1 / x if x > 0.0 else 1000.0

        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        xs = np.arange(min_corner, max_corner, 0.1)
        y1s = [f1(x) for x in xs]

        ND1 = NDTree()
        ND2 = NDTree()

        for x, y in zip(xs, y1s):
            point = (x, y)
            ND1.update_point(point)

        # Read/Write NDTree from file
        print('Reading from {0}, human_readable: {1}'.format(nfile, read_human_readable))
        print('Writing to {0}, human_readable: {1}'.format(nfile, write_human_readable))

        ND1.to_file(nfile, append=False, human_readable=write_human_readable)
        ND2.from_file(nfile, human_readable=read_human_readable)

        print('NDTree 1: {0}'.format(ND1))
        print('NDTree 2: {0}'.format(ND2))

        self.assertEqual(ND1, ND2, 'Different NDTree')
        self.assertEqual(hash(ND1), hash(ND2), 'Different NDTree')

        del ND1
        del ND2

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)

    # Test OraclePoint
    def test_files_OraclePoint(self):
        # type: (OraclePointTestCase) -> None
        self.read_write_oracle_files(read_human_readable=True, write_human_readable=True)
        self.read_write_oracle_files(read_human_readable=False, write_human_readable=False)

    def read_write_oracle_files(self, min_corner=0.0,
                                max_corner=1.0,
                                read_human_readable=False,
                                write_human_readable=False):
        # type: (OraclePointTestCase, float, float, bool) -> None
        tmpfile = tf.NamedTemporaryFile(delete=False)
        nfile = tmpfile.name

        # Points
        def f1(x):
            return 1 / x if x > 0.0 else 1000.0

        def f2(x):
            return 0.1 + (1 / x) if x > 0.0 else 1000.1

        def f3(x):
            return -0.1 + (1 / x) if x > 0.0 else 999.9

        xs = np.arange(min_corner, max_corner, 0.1)
        y1s = [f1(x) for x in xs]
        y2s = [f2(x) for x in xs]
        y3s = [f3(x) for x in xs]

        p1 = list(zip(xs, y1s))
        p2 = list(zip(xs, y2s))
        p3 = list(zip(xs, y3s))

        # p1 = [(float(x), float(y)) for x, y in zip(xs, y1s)]
        # p2 = [(float(x), float(y)) for x, y in zip(xs, y2s)]
        # p3 = [(float(x), float(y)) for x, y in zip(xs, y3s)]

        p1 = sorted(p1)
        p2 = sorted(p2)
        p3 = sorted(p3)

        # Oracle
        ora1 = OraclePoint()
        for p in p1:
            ora1.add_point(p)

        ora2 = OraclePoint()
        ora2.add_points(set(p1))

        self.assertEqual(ora1, ora2)

        # Membership test
        fora1 = ora1.membership()

        for p in p1:
            self.assertTrue(fora1(p))
            self.assertTrue(p in ora1)

        for p in p2:
            self.assertTrue(fora1(p))

        for p in p3:
            self.assertFalse(fora1(p))
            self.assertFalse(p in ora1)

        # Read/Write Oracle from file
        print('Reading from {0}, human_readable: {1}'.format(nfile, read_human_readable))
        print('Writing to {0}, human_readable: {1}'.format(nfile, write_human_readable))

        ora1.to_file(nfile, append=False, human_readable=write_human_readable)
        ora2 = OraclePoint()
        ora2.from_file(nfile, human_readable=read_human_readable)

        print('Oracle 1: {0}'.format(ora1))
        print('Oracle 2: {0}'.format(ora2))

        param1 = ora1.get_var_names()
        param2 = ora2.get_var_names()

        self.assertNotEqual(param1, [])
        self.assertEqual(param1, param2)

        print('Oracle 1 Parameters: {0}'.format(param1))
        print('Oracle 2 Parameters: {0}'.format(param2))

        points1 = sorted(ora1.get_points())
        points2 = sorted(ora2.get_points())

        print('Oracle 1 Points: {0}'.format(points1))
        print('Oracle 2 Points: {0}'.format(points2))
        self.assertEqual(points1, points2, 'Different oracles')

        self.assertEqual(ora1, ora2, 'Different oracles')
        self.assertEqual(hash(ora1), hash(ora2), 'Different oracles')

        ora3 = copy.copy(ora1)
        self.assertEqual(ora1, ora3, 'Different oracles')
        self.assertEqual(hash(ora1), hash(ora3), 'Different oracles')

        ora3 = copy.deepcopy(ora1)
        self.assertEqual(ora1, ora3, 'Different oracles')
        self.assertEqual(hash(ora1), hash(ora3), 'Different oracles')

        del ora1
        del ora2
        del ora3

        # Remove tempfile
        # os.unlink(nfile)
        self.add_file_to_clean(nfile)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
