from ParetoLib.Oracle.OracleVolTest import OracleVolTest
from ParetoLib.Search.Search import SearchIntersection2D, SearchIntersection3D, Search3D, EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet



(min_x, min_y, min_z) = (0.0, 0.0, 0.0)
(max_x, max_y, max_z) = (1.0, 1.0, 1.0)

orac1 = OracleVolTest(numPoints=10)
orac2 = OracleVolTest(lineIntercept=1.1)

rs = SearchIntersection3D(oracle1=orac1, oracle2=orac2,
                                        min_cornerx=min_x,
                                        min_cornery=min_y,
                                        min_cornerz=min_z,
                                        max_cornerx=max_x,
                                        max_cornery=max_y,
                                        max_cornerz=max_z,
                                        epsilon=0.0001,
                                        delta=0.01,
                                        max_step=10000,
                                        blocking=False,
                                        sleep=0,
                                        opt_level=2,
                                        parallel=False,
                                        logging=False,
                                        simplify=True)

intersection = rs.yup
print('length of intersection:', len(intersection))
intersect_region = []
border = []
rs = ResultSet(border=border, ylow=intersect_region, yup=intersection, xspace=rs.xspace)
rs.plot_3D(opacity=0.1)
rs.plot_2D_light(xaxe=0, yaxe=1, fig_title='Projection on (p1,p2) of intersection', var_names=['p1', 'p2', 'p3'])
rs.plot_2D_light(xaxe=1, yaxe=2, fig_title='Projection on (p2,p3) of intersection', var_names=['p1', 'p2', 'p3'])
rs.plot_2D_light(xaxe=0, yaxe=2, fig_title='Projection on (p1,p3) of intersection', var_names=['p1', 'p2', 'p3'])
