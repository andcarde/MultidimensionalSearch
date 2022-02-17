from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import SearchND, EPS, DELTA, STEPS

# File containing the definition of the Oracle
nfile = '../../../Tests/Oracle/OracleSTLe/2D/triangular/triangular.txt'
human_readable = True

# Definition of the n-dimensional space
min_c, max_c = (0.0, 1.0)

oracle = OracleSTLeLib()
oracle.from_file(nfile, human_readable)
rs = SearchND(ora=oracle,
              min_corner=min_c,
              max_corner=max_c,
              epsilon=EPS,
              delta=DELTA,
              max_step=STEPS,
              blocking=False,
              sleep=0,
              opt_level=0,
              parallel=False,
              logging=True,
              simplify=True)
rs.to_file("result.zip")
