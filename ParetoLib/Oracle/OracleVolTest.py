from ParetoLib.Oracle.Oracle import Oracle
import math


class OracleVolTest(Oracle):
    def __init__(self, lineIntercept=0, numPoints=7):
        # type: (OracleVolTest, int, int) -> None
        """
        An OracleVolTest is a set of Conditions.
        """
        # super(OracleVolTest, self).__init__()
        Oracle.__init__(self)
        self.lineIntercept = lineIntercept
        self.numPoints = numPoints

    def member(self, point):
        # type: (OracleVolTest, tuple) -> bool
        """
        See Oracle.member().
        A point belongs to the Oracle if it satisfies all the conditions.
        """
        if self.lineIntercept != 0:
            return point[0] + point[1] < self.lineIntercept
        discretize = math.floor(point[0] * self.numPoints)
        return point[1] > (1 - 1 * discretize / self.numPoints)

    def dim(self):
        # type: (OracleVolTest) -> int
        """
        See Oracle.dim().
        """
        return 3

    # def membership(self):
    #     # type: (OracleVolTest) -> callable
    #     """
    #     See Oracle.membership().
    #     """
    #     return lambda point: self.member(point)
