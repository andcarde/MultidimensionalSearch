from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Search.Search import *

# File containing the definition of the Oracle
nfile='../../Tests/Search/OracleFunction/ND/test-2d.txt'
human_readable=True

# Definition of the n-dimensional space
min_c, max_c = (0.0, 1.0)

oracle = OracleFunction()
oracle.fromFile(nfile, human_readable)
rs = SearchND(ora=oracle,
              min_corner=min_c,
              max_corner=max_c,
              epsilon=EPS,
              delta=DELTA,
              max_step=STEPS,
              blocking=False,
              sleep=0)