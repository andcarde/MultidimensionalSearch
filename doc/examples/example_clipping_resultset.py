import sys

from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Search.Search import create_3D_space

# python example_clipping_resultset.py sample_resultset.zip
rs = ResultSet()
rs_file_name = sys.argv[1]
rs.from_file(rs_file_name)
# Change clip_box to clip using the box and display
clip_box = create_3D_space(0.0, 0.6, 0.0, 20.0, 0.8, 0.25)
rs.plot_3D(opacity=0.1, fig_title='Intersection of pareto fronts', var_names=['p1', 'p2', 'p3'],clip_box=clip_box)
