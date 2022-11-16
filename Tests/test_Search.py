import unittest

import time
import os
import numpy as np
import pytest

from ParetoLib.Search.Search import Search2D, Search3D, SearchND, SearchIntersectionND, SearchND_BMNN22
from ParetoLib.Search.ResultSet import ResultSet

from ParetoLib.Oracle.OracleFunction import OracleFunction, Condition
from ParetoLib.Oracle.OraclePoint import OraclePoint
from ParetoLib.Oracle.OracleSTL import OracleSTL
from ParetoLib.Oracle.OracleSTLe import OracleSTLe, OracleSTLeLib
from ParetoLib.Oracle.Oracle import Oracle

if 'DISPLAY' not in os.environ:
    SLEEP_TIME = 0.0
else:
    SLEEP_TIME = 5.1


class SearchIntersectionTestCase(unittest.TestCase):

    def setUp(self):
        # type: (SearchIntersectionTestCase) -> None

        # This test only considers Oracles (in *.txt format) that are located in the root
        # of folders Oracle/OracleXXX/[1|2|3|N]D

        self.oracle_1 = OracleFunction()
        self.oracle_2 = OracleFunction()

        cond_1 = Condition("x**2 + y**2", "<", "1")
        cond_2 = Condition("(x-1)**2 + (y-1)**2", "<", "1")
        self.oracle_1.add(cond_1)
        self.oracle_2.add(cond_2)

        # By default, use min_corner in 0.0 and max_corner in 2.0
        self.min_c = 0.0
        self.max_c = 2.0
        # Use N sample points for verifying that the result of the Pareto search is correct.
        # We compare the membership of a point to a ResultSet closure and the answer of the Oracle.
        self.numpoints_verify = 30

        # Configuring searching parameters
        self.EPS = 1e-5
        self.DELTA = 1e-5
        self.STEPS = 20

    #  Membership testing function used in verify2D, verify3D and verifyND
    def closureMembershipTest(self, fora_1, fora_2, rs, xpoint):
        # type: (SearchIntersectionTestCase, callable, callable, ResultSet, tuple) -> bool

        test1 = fora_1(xpoint) and fora_2(xpoint) and (rs.member_yup(xpoint) or rs.member_border(xpoint))
        test2 = (not fora_1(xpoint) or not fora_2(xpoint)) and (rs.member_ylow(xpoint) or rs.member_border(xpoint))

        print_string = 'Warning!\n'
        print_string += 'Testing {0}\n'.format(str(xpoint))
        print_string += '(inYup, inYlow, inBorder, inSpace): ({0}, {1}, {2}, {3})\n'.format(rs.member_yup(xpoint),
                                                                                            rs.member_ylow(xpoint),
                                                                                            rs.member_border(xpoint),
                                                                                            rs.member_space(xpoint))
        print_string += 'Expecting\n'
        print_string += '(inYup, inYlow): ({0}, {1})\n'.format(fora_1(xpoint), not fora_1(xpoint))
        print_string += '(test1, test2): ({0}, {1})\n'.format(test1, test2)

        self.assertTrue(test1 or test2, print_string)

        return test1 or test2

    # Auxiliar function for reporting ND results
    def verifyND(self,
                 fora_1,
                 fora_2,
                 rs,
                 list_test_points):
        # type: (SearchIntersectionTestCase, callable, callable, ResultSet, list) -> None

        # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]

        start = time.time()
        f1 = lambda p: 1 if rs.member_yup(p) else 0
        f2 = lambda p: 1 if rs.member_ylow(p) else 0
        f3 = lambda p: 1 if rs.member_border(p) else 0

        list_nYup = map(f1, list_test_points)
        list_nYlow = map(f2, list_test_points)
        list_nBorder = map(f3, list_test_points)

        nYup = sum(list_nYup)
        nYlow = sum(list_nYlow)
        nBorder = sum(list_nBorder)

        print('Membership query:')
        if all(self.closureMembershipTest(fora_1, fora_2, rs, tuple(p)) for p in list_test_points):
            print('Ok!\n')
        else:
            print('Not ok!\n')
            raise ValueError

        # Yup and ylow does not contain overlapping rectangles
        self.assertAlmostEqual(rs.overlapping_volume_yup(), 0)
        self.assertAlmostEqual(rs.overlapping_volume_ylow(), 0)

        # Volume is conserved
        # self.assertEqual(rs.volume_total(), rs.volume_border() + rs.volume_yup() + rs.volume_ylow())
        self.assertLessEqual(rs.volume_yup() + rs.volume_ylow(), rs.volume_total())

        end = time.time()
        time0 = end - start

        print(rs.volume_report())
        print('Report Ylow: {0}'.format(str(nYlow)))
        print('Report Yup: {0}'.format(str(nYup)))
        print('Report Border: {0}'.format(str(nBorder)))
        print('Time tests: {0}'.format(str(time0)))

    def search_verify_ND(self):
        # type: (SearchIntersectionTestCase) -> None

        for bool_val in (True, False):
            fora_1 = self.oracle_1.membership()
            fora_2 = self.oracle_1.membership()
            d1 = self.oracle_1.dim()
            d2 = self.oracle_2.dim()
            self.assertEqual(d1, d2)
            for opt_level in range(3):
                print('\nTesting SearchIntersection')
                print('Dimension {0}'.format(d1))
                print('Optimisation level {0}'.format(opt_level))
                print('Parallel search {0}'.format(bool_val))
                print('Logging {0}'.format(bool_val))
                print('Simplify {0}'.format(bool_val))

                rs = SearchIntersectionND(ora1=self.oracle_1,
                                          ora2=self.oracle_2,
                                          min_corner=self.min_c,
                                          max_corner=self.max_c,
                                          epsilon=self.EPS,
                                          delta=self.DELTA,
                                          max_step=self.STEPS,
                                          blocking=False,
                                          sleep=SLEEP_TIME,
                                          opt_level=opt_level,
                                          parallel=bool_val,
                                          logging=bool_val,
                                          simplify=bool_val)

                # Create numpoints_verify vectors of dimension d
                # Continuous uniform distribution over the stated interval.
                # To sample Unif[a, b), b > a
                # (b - a) * random_sample() + a
                print('Dimension {0}'.format(d1))
                list_test_points = (self.max_c - self.min_c) * np.random.random_sample((self.numpoints_verify, d1)) \
                                   + self.min_c
                print('Verifying SearchIntersection')
                self.verifyND(fora_1, fora_2, rs, list_test_points)

    def test_ND(self):
        # type: (SearchIntersectionTestCase) -> None
        self.search_verify_ND()


class SearchTestCase(unittest.TestCase):

    def setUp(self):
        # type: (SearchTestCase) -> None

        # This test only considers Oracles (in *.txt format) that are located in the root
        # of folders Oracle/OracleXXX/[1|2|3|N]D

        self.this_dir = 'Oracle'
        self.oracle = Oracle()

        # By default, use min_corner in 0.0 and max_corner in 1.0
        self.min_c = 0.0
        self.max_c = 1.0
        # Use N sample points for verifying that the result of the Pareto search is correct.
        # We compare the membership of a point to a ResultSet closure and the answer of the Oracle.
        self.numpoints_verify = 30
        # Number of examples that will execute
        self.numfiles_test = 1

        # Configuring searching parameters
        self.EPS = 1e-5
        self.DELTA = 1e-5
        self.STEPS = 20
        # Required for BMNN22
        self.P0 = 1e-2
        self.ALPHA = 5e-2
        self.NUMCELLS = 25

    #  Membership testing function used in verify2D, verify3D and verifyND
    def closureMembershipTest(self, fora, rs, xpoint):
        # type: (SearchTestCase, callable, ResultSet, tuple) -> bool

        test1 = fora(xpoint) and (rs.member_yup(xpoint) or rs.member_border(xpoint))
        test2 = (not fora(xpoint)) and (rs.member_ylow(xpoint) or rs.member_border(xpoint))

        print_string = 'Warning!\n'
        print_string += 'Testing {0}\n'.format(str(xpoint))
        print_string += '(inYup, inYlow, inBorder, inSpace): ({0}, {1}, {2}, {3})\n'.format(rs.member_yup(xpoint),
                                                                                            rs.member_ylow(xpoint),
                                                                                            rs.member_border(xpoint),
                                                                                            rs.member_space(xpoint))
        print_string += 'Expecting\n'
        print_string += '(inYup, inYlow): ({0}, {1})\n'.format(fora(xpoint), not fora(xpoint))
        print_string += '(test1, test2): ({0}, {1})\n'.format(test1, test2)

        self.assertTrue(test1 or test2, print_string)

        return test1 or test2

    # Auxiliar function for reporting ND results
    def verifyND(self,
                 fora,
                 rs,
                 list_test_points):
        # type: (SearchTestCase, callable, ResultSet, list) -> None

        # list_test_points = [(t1p, t2p, t3p) for t1p in t1 for t2p in t2 for t3p in t3]

        start = time.time()
        f1 = lambda p: 1 if rs.member_yup(p) else 0
        f2 = lambda p: 1 if rs.member_ylow(p) else 0
        f3 = lambda p: 1 if rs.member_border(p) else 0

        list_nYup = map(f1, list_test_points)
        list_nYlow = map(f2, list_test_points)
        list_nBorder = map(f3, list_test_points)

        nYup = sum(list_nYup)
        nYlow = sum(list_nYlow)
        nBorder = sum(list_nBorder)

        print('Membership query:')
        if all(self.closureMembershipTest(fora, rs, tuple(p)) for p in list_test_points):
            print('Ok!\n')
        else:
            print('Not ok!\n')
            raise ValueError

        # Yup and ylow does not contain overlapping rectangles
        self.assertAlmostEqual(rs.overlapping_volume_yup(), 0)
        self.assertAlmostEqual(rs.overlapping_volume_ylow(), 0)

        # Volume is conserved
        # self.assertEqual(rs.volume_total(), rs.volume_border() + rs.volume_yup() + rs.volume_ylow())
        self.assertLessEqual(rs.volume_yup() + rs.volume_ylow(), rs.volume_total())

        end = time.time()
        time0 = end - start

        print(rs.volume_report())
        print('Report Ylow: {0}'.format(str(nYlow)))
        print('Report Yup: {0}'.format(str(nYup)))
        print('Report Border: {0}'.format(str(nBorder)))
        print('Time tests: {0}'.format(str(time0)))

    def search_verify_ND(self, human_readable, list_test_files):
        # type: (SearchTestCase, bool, list) -> None

        for bool_val in (True, False):
            for test in list_test_files:
                self.assertTrue(os.path.isfile(test), test)
                self.oracle.from_file(test, human_readable)
                fora = self.oracle.membership()
                d = self.oracle.dim()
                for opt_level in range(3):
                    print('\nTesting {0}'.format(test))
                    print('Dimension {0}'.format(d))
                    print('Optimisation level {0}'.format(opt_level))
                    print('Parallel search {0}'.format(bool_val))
                    print('Logging {0}'.format(bool_val))
                    print('Simplify {0}'.format(bool_val))

                    rs = SearchND(ora=self.oracle,
                                  min_corner=self.min_c,
                                  max_corner=self.max_c,
                                  epsilon=self.EPS,
                                  delta=self.DELTA,
                                  max_step=self.STEPS,
                                  blocking=False,
                                  sleep=SLEEP_TIME,
                                  opt_level=opt_level,
                                  parallel=bool_val,
                                  logging=bool_val,
                                  simplify=bool_val)

                    # Create numpoints_verify vectors of dimension d
                    # Continuous uniform distribution over the stated interval.
                    # To sample Unif[a, b), b > a
                    # (b - a) * random_sample() + a
                    print('Dimension {0}'.format(d))
                    list_test_points = (self.max_c - self.min_c) * np.random.random_sample((self.numpoints_verify, d)) \
                                       + self.min_c
                    print('Verifying {0}'.format(test))
                    self.verifyND(fora, rs, list_test_points)

    def search_verify_ND_BMNN22(self, human_readable, list_test_files):
        # type: (SearchTestCase, bool, list) -> None

        for test in list_test_files:
            self.assertTrue(os.path.isfile(test), test)
            self.oracle.from_file(test, human_readable)
            fora = self.oracle.membership()
            d = self.oracle.dim()
            for opt_level in range(2):
                print('\nTesting {0}'.format(test))
                print('Dimension {0}'.format(d))
                print('Optimisation level {0}'.format(opt_level))
                print('Parallel search {0}'.format(False))

                rs = SearchND_BMNN22(ora_list=[self.oracle],
                                     min_corner=self.min_c,
                                     max_corner=self.max_c,
                                     p0=self.P0,
                                     alpha=self.ALPHA,
                                     num_cells=self.NUMCELLS,
                                     blocking=False,
                                     sleep=SLEEP_TIME,
                                     opt_level=opt_level,
                                     parallel=False,
                                     logging=False,
                                     simplify=False)

                print('Parallel search {0}'.format(True))

                rs_par = SearchND_BMNN22(ora_list=[self.oracle],
                                         min_corner=self.min_c,
                                         max_corner=self.max_c,
                                         p0=self.P0,
                                         alpha=self.ALPHA,
                                         num_cells=self.NUMCELLS,
                                         blocking=False,
                                         sleep=SLEEP_TIME,
                                         opt_level=opt_level,
                                         parallel=True,
                                         logging=False,
                                         simplify=False)

                # set(rs.yup) == set(rs_par.yup) ...
                self.assertSetEqual(set(rs.yup), set(rs_par.yup))
                self.assertSetEqual(set(rs.ylow), set(rs_par.ylow))
                self.assertSetEqual(set(rs.border), set(rs_par.border))


class SearchOracleFunctionTestCase(SearchTestCase):

    def setUp(self):
        # type: (SearchOracleFunctionTestCase) -> None

        super(SearchOracleFunctionTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleFunction'
        self.oracle = OracleFunction()
        # OracleFunction/[2|3]D/test3.txt contains '1/x', so x > 0
        self.min_c = 0.0001
        # OracleFunction/[2|3]D/test[3|4|5].txt requires max_c > 1.0 for reaching y_up
        self.max_c = 2.0

    def test_2D(self):
        # type: (SearchOracleFunctionTestCase) -> None

        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_3D(self):
        # type: (SearchOracleFunctionTestCase) -> None

        test_dir = os.path.join(self.this_dir, '3D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_ND(self):
        # type: (SearchOracleFunctionTestCase) -> None

        test_dir = os.path.join(self.this_dir, 'ND')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)


MATLAB_INSTALLED = True
try:
    from ParetoLib.Oracle.OracleMatlab import OracleMatlab
except ImportError:
    MATLAB_INSTALLED = False


@pytest.mark.skipif(
    not MATLAB_INSTALLED,
    reason='Matlab is not installed'
)
class SearchOracleMatlabTestCase(SearchOracleFunctionTestCase):

    def setUp(self):
        # type: (SearchOracleMatlabTestCase) -> None

        super(SearchOracleMatlabTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleMatlab'
        self.oracle = OracleMatlab()
        # OracleFunction/[2|3]D/test3.txt contains '1/x', so x > 0
        self.min_c = 0.0001
        # OracleFunction/[2|3]D/test[3|4|5].txt requires max_c > 1.0 for reaching y_up
        self.max_c = 2.0


class SearchOraclePointTestCase(SearchTestCase):

    def setUp(self):
        # type: (SearchOraclePointTestCase) -> None

        super(SearchOraclePointTestCase, self).setUp()
        self.this_dir = 'Oracle/OraclePoint'
        self.oracle = OraclePoint()

    def test_2D(self):
        # type: (SearchOraclePointTestCase) -> None

        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        # test-2d-12points provides the maximum interval: [-1024, 1024]
        self.min_c = -1024.0
        self.max_c = 1024.0
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_3D(self):
        # type: (SearchOraclePointTestCase) -> None

        test_dir = os.path.join(self.this_dir, '3D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        # test-3d-[1000|2000] are LIDAR points between 0.0 and 600.0 approx.
        self.min_c = 0.0
        self.max_c = 600.0
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_ND(self):
        # type: (SearchOraclePointTestCase) -> None

        test_dir = os.path.join(self.this_dir, 'ND')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        # test-4d and test-5d are random points in the interval [1.0, 2.0]
        self.min_c = 1.0
        self.max_c = 2.0
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)


class SearchOracleSTLTestCase(SearchTestCase):

    def setUp(self):
        # type: (SearchOracleSTLTestCase) -> None

        super(SearchOracleSTLTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleSTL'
        self.oracle = OracleSTL()

        # Run tests of the 'sincos' example.
        # The validity of the parametric domain is [-2.0, 2.0] (sin and cos signals has module 1.0)
        self.min_c = -2.0
        self.max_c = 2.0

        self.numpoints_verify = 2

        # Configuring searching parameters
        self.EPS = float("inf")
        self.DELTA = 1e-1
        self.STEPS = 1

    @pytest.mark.timeout(600, method='thread')
    def test_1D(self):
        # type: (SearchOracleSTLTestCase) -> None

        test_dir = os.path.join(self.this_dir, '1D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    @pytest.mark.timeout(600, method='thread')
    def test_2D(self):
        # type: (SearchOracleSTLTestCase) -> None

        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    # Currently, we only run OracleSTL tests for 1D and 2D because of the
    # complexity in verifying the results and the computational cost of
    # evaluating STL properties in the Test folder.

    # def test_3D(self):
    #     self.search_verify_3D(False)

    # def test_ND(self):
    #     self.search_verify_ND(False)


class SearchOracleSTLeTestCase(SearchTestCase):

    def setUp(self):
        # type: (SearchOracleSTLeTestCase) -> None

        super(SearchOracleSTLeTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleSTLe'
        self.oracle = OracleSTLe()

        # Run tests of the 'stabilization' example.
        # The validity of the parametric domain is [-1.0, 1.0]  for p1 (signal)
        self.min_c = -1.0
        self.max_c = 1.0

    def test_1D(self):
        # type: (SearchOracleSTLeTestCase) -> None

        test_dir = os.path.join(self.this_dir, '1D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_2D(self):
        # type: (SearchOracleSTLeTestCase) -> None

        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)


# class SearchOracleEpsSTLeTestCase(SearchOracleSTLeLibTestCase):

class SearchOracleSTLeLibTestCase(SearchTestCase):

    def setUp(self):
        # type: (SearchOracleSTLeLibTestCase) -> None

        super(SearchOracleSTLeLibTestCase, self).setUp()
        self.this_dir = 'Oracle/OracleSTLe'
        self.oracle = OracleSTLeLib()

        # Run tests of the 'stabilization' example.
        # The validity of the parametric domain is [-1.0, 1.0]  for p1 (signal)
        self.min_c = -1.0
        self.max_c = 1.0

    def test_1D(self):
        # type: (SearchOracleSTLeLibTestCase) -> None

        test_dir = os.path.join(self.this_dir, '1D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_1D_BMNN22(self):
        # type: (SearchOracleSTLeLibTestCase) -> None

        test_dir = os.path.join(self.this_dir, '1D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND_BMNN22(human_readable=True, list_test_files=list_test_files)

    def test_2D(self):
        # type: (SearchOracleSTLeLibTestCase) -> None

        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND(human_readable=True, list_test_files=list_test_files)

    def test_2D_BMNN22(self):
        # type: (SearchOracleSTLeLibTestCase) -> None

        test_dir = os.path.join(self.this_dir, '2D')
        files_path = os.listdir(test_dir)
        list_test_files = [os.path.join(test_dir, x) for x in files_path if x.endswith('.txt')]
        num_files_test = min(self.numfiles_test, len(list_test_files))
        list_test_files = sorted(list_test_files)[:num_files_test]
        self.search_verify_ND_BMNN22(human_readable=True, list_test_files=list_test_files)


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    unittest.main(testRunner=runner)
