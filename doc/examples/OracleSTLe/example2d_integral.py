from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import Search2D, EPS, DELTA, STEPS

# File containing the definition of the Oracle
# nfile = '../../../Tests/Oracle/OracleSTLe/2D/triangular/integral/triangular_int.txt'
nfile = '../../../Tests/Oracle/OracleSTLe/2D/triangular/integral/triangular_float.txt'
human_readable = True

# Definition of the n-dimensional space
# For triangular_int:
# min_x, min_y = (1990.0, 0.0)
# max_x, max_y = (2000.0, 300.0)

# For triangular_float:
min_x, min_y = (1950.0, 0.0)
max_x, max_y = (2000.0, 3.0)

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
              logging=False,
              simplify=False)
rs.to_file("result.zip")
