from ParetoLib.Oracle.OracleFunction import *
from ParetoLib.Search.Search import *

# File containing the definition of the Oracle
nfile = '../../Tests/Oracle/OracleFunction/2D/test1.txt'
human_readable = True

# Definition of the n-dimensional space
min_x, min_y = (0.0, 0.0)
max_x, max_y = (1.0, 1.0)

oracle = OracleFunction()
oracle.fromFile(nfile, human_readable)
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
              logging=True)
