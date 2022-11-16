from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import Search2D, EPS, DELTA, STEPS

# File containing the definition of the Oracle
# nfile = '../../../Tests/Oracle/OracleSTLe/2D/triangular/derivative/triangular_int.txt'
# nfile = '../../../Tests/Oracle/OracleSTLe/2D/triangular/derivative/triangular_float.txt'
# nfile = '../../../Tests/Oracle/OracleSTLe/2D/stabilization/derivative/stabilization.txt'
nfile = 'Tests/Oracle/OracleSTLe/2D/stabilization/derivative/stabilization.txt'
human_readable = True

# Definition of the n-dimensional space
# For triangular_int:
# min_x, min_y = (1.0, 0.0)
# max_x, max_y = (999.0, 2.0)

# For triangular_float:
# min_x, min_y = (0.0, 0.0)
# max_x, max_y = (10.0, 0.002)

# For stabilization_der:
# min_x, min_y = (80.0, 0.0)
# max_x, max_y = (120.0, 0.005)

# For stabilization_min_max:
min_x, min_y = (0.0, 0.0)
max_x, max_y = (200.0, 0.8)

oracle = OracleSTLeLib()
oracle.from_file(nfile, human_readable)
rs = Search2D(ora=oracle,
              min_cornerx=min_x,
              min_cornery=min_y,
              max_cornerx=max_x,
              max_cornery=max_y,
              epsilon=EPS,
              delta=DELTA,
              max_step=STEPS,
              blocking=False,
              sleep=0,
              opt_level=0,
              parallel=False,
              logging=True,
              simplify=False)
rs.to_file("result.zip")
