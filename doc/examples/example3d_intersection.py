from ParetoLib.Oracle.Oracle import Oracle
from ParetoLib.Search.Search import SearchIntersection3D, EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet
import math


class OracleIntercept(Oracle):
    def __init__(self, line_intercept=0.0, num_points=7):
        # type: (OracleIntercept, float, int) -> None

        # super(OracleIntercept, self).__init__()
        Oracle.__init__(self)
        self.line_intercept = line_intercept
        self.num_points = num_points

    def member(self, point):
        # type: (OracleIntercept, tuple) -> bool
        """
        See Oracle.member().
        """
        if self.line_intercept != 0.0:
            return point[0] + point[1] < self.line_intercept
        else:
            # discretize = math.floor(point[0] * self.num_points)
            # return point[1] > (1 - 1 * discretize / self.num_points)
            discretize = math.floor(point[0] * self.num_points) / self.num_points
            return discretize + point[1] > 1.0

    def dim(self):
        # type: (OracleIntercept) -> int
        """
        See Oracle.dim().
        """
        return 3


if __name__ == "__main__":
    (min_x, min_y, min_z) = (0.0, 0.0, 0.0)
    (max_x, max_y, max_z) = (1.0, 1.0, 1.0)

    orac1 = OracleIntercept(num_points=10)
    orac2 = OracleIntercept(line_intercept=1.1)

    rs = SearchIntersection3D(ora1=orac1, ora2=orac2,
                              min_cornerx=min_x,
                              min_cornery=min_y,
                              min_cornerz=min_z,
                              max_cornerx=max_x,
                              max_cornery=max_y,
                              max_cornerz=max_z,
                              epsilon=0.0001,   # EPS
                              delta=0.01,       # DELTA
                              max_step=10000,   # STEPS
                              blocking=False,
                              sleep=0,
                              opt_level=2,
                              parallel=False,
                              logging=False,
                              simplify=False)

    intersection = rs.yup
    print('length of intersection:', len(intersection))
    intersect_region = []
    border = []
    rs = ResultSet(border=border, ylow=intersect_region, yup=intersection, xspace=rs.xspace)
    rs.plot_3D(opacity=0.1)
    rs.plot_2D_light(xaxe=0, yaxe=1, fig_title='Projection on (p1,p2) of intersection', var_names=['p1', 'p2', 'p3'])
    rs.plot_2D_light(xaxe=1, yaxe=2, fig_title='Projection on (p2,p3) of intersection', var_names=['p1', 'p2', 'p3'])
    rs.plot_2D_light(xaxe=0, yaxe=2, fig_title='Projection on (p1,p3) of intersection', var_names=['p1', 'p2', 'p3'])
