import unittest
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Oracle.NDTree import NDTree
from ParetoLib.Search.ResultSet import ResultSet


class TestResultSet(unittest.TestCase):

    def setUp(self):
        # Initial setup for the tests
        self.xspace = Rectangle((0.0, 0.0), (1.0, 1.0))
        self.ylow = [Rectangle((0.0, 0.0), (0.5, 0.5))]
        self.yup = [Rectangle((0.5, 0.5), (1.0, 1.0))]
        self.border = [Rectangle((0.0, 0.5), (0.5, 1.0)), Rectangle((0.5, 1.0), (1.0, 1.0))]
        self.result_set = ResultSet(self.border, self.ylow, self.yup, self.xspace)

    def test_initialization(self):
        # Test for correct initialization of ResultSet
        self.assertEqual(self.result_set.xspace, self.xspace)
        self.assertEqual(self.result_set.ylow, self.ylow)
        self.assertEqual(self.result_set.yup, self.yup)
        self.assertEqual(self.result_set.border, self.border)

    def test_setattr_updates_pareto(self):
        # Test to ensure that changing bounds reinitializes the Pareto trees
        new_ylow = [Rectangle((0.0, 0.0), (0.3, 0.3))]
        self.result_set.ylow = new_ylow
        self.assertIsInstance(self.result_set.ylow_pareto, NDTree)
        self.assertIsInstance(self.result_set.yup_pareto, NDTree)

    def test_str_representation(self):
        # Test for string representation
        expected_str = '<{}, {}, {}>'.format(self.yup, self.ylow, self.border)
        self.assertEqual(str(self.result_set), expected_str)

    def test_equality(self):
        # Test for equality of two ResultSets
        other_result_set = ResultSet(self.border, self.ylow, self.yup, self.xspace)
        self.assertEqual(self.result_set, other_result_set)

    def test_vertices_yup(self):
        # Test for the vertices_yup function
        vertices = self.result_set.vertices_yup()
        expected_vertices = {(0.5, 0.5), (1.0, 1.0)}
        self.assertEqual(vertices, expected_vertices)

    def test_volume_calculation(self):
        # Test for the volume calculation function
        self.assertEqual(self.result_set.volume_ylow(), 0.25)
        self.assertEqual(self.result_set.volume_yup(), 0.25)
        self.assertEqual(self.result_set.volume_border(), 0.5)
        self.assertEqual(self.result_set.volume_total(), 1.0)

    def test_membership_functions(self):
        # Test for the membership verification function
        self.assertTrue(self.result_set.member_yup((0.75, 0.75)))
        self.assertFalse(self.result_set.member_ylow((0.75, 0.75)))
        self.assertTrue(self.result_set.member_ylow((0.25, 0.25)))
        self.assertFalse(self.result_set.member_border((0.75, 0.75)))

    def test_simplify(self):
        # Test for the simplify function
        self.result_set.simplify()
        self.assertGreaterEqual(len(self.result_set.border), 1)
        self.assertGreaterEqual(len(self.result_set.ylow), 1)
        self.assertGreaterEqual(len(self.result_set.yup), 1)


if __name__ == '__main__':
    unittest.main()
