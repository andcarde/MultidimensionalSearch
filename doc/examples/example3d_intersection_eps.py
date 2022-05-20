from ParetoLib.Oracle.OracleEpsSTLe import OracleEpsSTLe
from ParetoLib.Oracle.OracleFunction import OracleFunction
from ParetoLib.Oracle.OracleSTLe import OracleSTLeLib
from ParetoLib.Search.Search import SearchIntersection2D, SearchIntersection3D, Search3D, EPS, DELTA, STEPS
from ParetoLib.Search.ResultSet import ResultSet
from ParetoLib.Geometry.Rectangle import Rectangle
from ParetoLib.Search.Search import create_3D_space
import sys

import time


def pareto_3D_Intersection(ecg_name, numParams, formula_name1, formula_name2, min_tuple, max_tuple):
    nfile1 = './ecgLearn1.txt'
    nfile2 = './ecgLearn2.txt'
    # nfile1 = '../../Tests/Oracle/OracleFunction/2D/test1_1.txt'
    # nfile2 = '../../Tests/Oracle/OracleFunction/2D/test1_2.txt'

    # Copy the template file to a scratch file.
    stl_file = open('./stl/' + formula_name1 + '.stl')
    stl_string = stl_file.read()
    stl_file.close()

    # Write the template formula into a scratch file.
    fn_scratch = open('stl/scratchInterFn.stl', 'w')
    fn_scratch.write(stl_string)
    fn_scratch.close()

    # Copy the template file to a scratch file.
    stl_file = open('./stl/' + formula_name2 + '.stl', 'r')
    stl_string = stl_file.read()
    stl_file.close()

    # Write the template formula into a scratch file.
    fp_scratch = open('stl/scratchInterFp.stl', 'w')
    fp_scratch.write(stl_string)
    fp_scratch.close()

    paramFile = open('ecgLearn.param', 'w')
    for i in range(numParams):
        paramFile.write('p' + str(i + 1) + '\n')
    paramFile.close()

    controlFile = open('ecgLearn1.txt', 'w')
    controlText = ''
    controlLines = []
    controlFile.write('./stl/scratchInterFn.stl\n')
    controlFile.write('./' + ecg_name + 'L.csv\n')
    controlFile.write('./ecgLearn.param\n')

    controlFile.close()

    controlFile = open('ecgLearn2.txt', 'w')
    controlText = ''
    controlLines = []
    controlFile.write('./stl/scratchInterFp.stl\n')
    controlFile.write('./' + ecg_name + 'L.csv\n')
    controlFile.write('./ecgLearn.param\n')

    controlFile.close()

    human_readable = True

    # Definition of the n-dimensional space
    min_x, min_y, min_z = min_tuple
    max_x, max_y, max_z = max_tuple

    orac1 = OracleEpsSTLe(boundOnCount=int(sys.argv[2]), intvlEpsilon=1)
    orac1.from_file(nfile1, human_readable)

    orac2 = OracleEpsSTLe(boundOnCount=int(sys.argv[3]), intvlEpsilon=10)
    orac2.from_file(nfile2, human_readable)

    output_intersect = SearchIntersection3D(ora1=orac1, ora2=orac2,
                                            min_cornerx=min_x,
                                            min_cornery=min_y,
                                            min_cornerz=min_z,
                                            max_cornerx=max_x,
                                            max_cornery=max_y,
                                            max_cornerz=max_z,
                                            epsilon=EPS,
                                            delta=1.0 / float(sys.argv[5]),
                                            max_step=10000,
                                            blocking=False,
                                            sleep=0,
                                            opt_level=int(sys.argv[4]),
                                            parallel=False,
                                            logging=False,
                                            simplify=False)
    return output_intersect


t0 = time.time()
min_tuple = (0.0, -1.0, -1.0)
max_tuple = (70.0, 1.00, 1.0)
rs1 = pareto_3D_Intersection(str(sys.argv[1]), 3, 'ecgInterTemplateFn3D', 'ecgInterTemplateFp3D', min_tuple, max_tuple)
# min_x, min_y, min_z = min_tuple
# max_x, max_y, max_z = max_tuple
# xyspace = create_3D_space(min_x, min_y, min_z, max_x, max_y, max_z)

# intersection = rs1 #.yup
# print("num intersection boxes:", len(intersection))
# rs2 = ResultSet(border=[], yup=intersection, ylow=[], xspace=xyspace)
# rs2.plot_3D(opacity=0.1, fig_title='Intersection of pareto fronts', var_names=['p1','p2','p3'],clip=True)
# rs2.to_file(sys.argv[1]+"_characterizeOnlyOne"+sys.argv[5]+".zip")

intersection = rs1.yup
print("num intersection boxes:", len(intersection))
t1 = time.time()
print('TRESIMP: Time taken for intersection pareto (1):', t1 - t0)
rs1.plot_3D(opacity=0.1, fig_title='Intersection of pareto fronts', var_names=['p1', 'p2', 'p3'], clip=True)
rs1.to_file(sys.argv[1] + "_characterizeOnlyOne" + sys.argv[5] + ".zip")
