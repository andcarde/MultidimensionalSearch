from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Oracle.OracleIpoly import OracleIpoly
from ParetoLib.Oracle.OracleDpoly import OracleDpoly
from ParetoLib.Search.Search import SearchRobustIntersectionND_2, EPS, DELTA, STEPS

# Files containing the definitions of the Oracles
nfile1 = './forinc.txt'
nfile2 = './fordec.txt'
human_readable = True

# Definition of the n-dimensional space
list_intervals = [(0,100),(0,100)]

ora1 = OracleIpoly([(1,1,100)])
ora2 = OracleDpoly([(1,1,130)])
ora3 = OracleSTLeLib()
ora3.from_file(nfile1, human_readable)
ora4 = OracleSTLeLib()
ora4.from_file(nfile2, human_readable)

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
rs.plot_2D()