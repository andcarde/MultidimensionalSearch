from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Oracle.OracleFunction import OracleFunction
from ParetoLib.Search.Search import SearchRobustIntersectionND_2, EPS, STEPS

"""
This is a toy example for robust intersection of STL formulae. 
Has general increasing (icons.txt) and decreasing (dcons.txt) sets.
The formulae are valid only in the intersection of these sets.
"""

# Files containing the definitions of the Oracles
nfile1 = './stl/icons.txt'
nfile2 = './stl/dcons.txt'
nfile3 = './stl/forinc.txt'
nfile4 = './stl/fordec.txt'
human_readable = True

# Definition of the n-dimensional space
list_intervals = [(0, 100), (0, 100)]

ora1 = OracleFunction()
ora1.from_file(nfile1, human_readable)
ora2 = OracleFunction()
ora2.from_file(nfile2, human_readable)
ora3 = OracleSTLeLib()
ora3.from_file(nfile3, human_readable)
ora4 = OracleSTLeLib()
ora4.from_file(nfile4, human_readable)

rs = SearchRobustIntersectionND_2(ora1, ora2,
                                  ora3, ora4,
                                  list_intervals,
                                  epsilon=EPS,
                                  delta=0.01,
                                  max_step=STEPS,
                                  blocking=False,
                                  sleep=0.0,
                                  opt_level=2,
                                  parallel=False,
                                  logging=True,
                                  simplify=False)
rs.filtering()
rs.plot_2D()
