from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.ResultSet import ResultSet

# File containing the definition of the Oracle
nfile = '../../../Tests/Oracle/OracleSTLe/2D/triangular/triangular.txt'
human_readable = True

oracle = OracleSTLeLib()
oracle.from_file(nfile, human_readable)

rs = ResultSet()
rs.from_file("result.zip")
rs.plot_2D_light(var_names=oracle.get_var_names())
