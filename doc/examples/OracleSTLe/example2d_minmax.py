from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import Search2D, EPS, DELTA, STEPS

# File containing the definition of the Oracle
nfile = 'Tests/Oracle/OracleSTLe/2D/stabilization/min_max/stabilization.txt'
human_readable = True


# For stabilization_der:
min_x, min_y = (900.0, 0.0)
max_x, max_y = (1000.0, 0.005)

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
