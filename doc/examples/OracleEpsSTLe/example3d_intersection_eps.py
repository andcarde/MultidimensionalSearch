import sys
import time

from ParetoLib.Oracle.OracleEpsSTLe import OracleEpsSTLe
from ParetoLib.Search.Search import SearchIntersection3D, EPS


def create_param_file(param_name, num_params):
    # type: (str, int) -> None
    param_file = open('./stl/' + param_name + '.param', 'w')
    for i in range(num_params):
        param_file.write('p' + str(i + 1) + '\n')
    param_file.close()


def create_project_file(project_file, stl_template_file, ecg_file, param_file):
    # type: (str, str, str, str) -> str

    suffix = '_instance'
    # Copy the template file to a scratch file.
    stl_file = open('./stl/' + stl_template_file + '.stl')
    stl_string = stl_file.read()
    stl_file.close()

    # Write the template formula into a scratch file.
    fn_scratch = open('./stl/' + stl_template_file + suffix + '.stl', 'w')
    fn_scratch.write(stl_string)
    fn_scratch.close()

    # project_file = './ecgLearn1.txt'
    control_file = open(project_file, 'w')
    control_file.write('./stl/' + stl_template_file + suffix + '.stl\n')
    control_file.write('./ecg/' + ecg_file + 'L.csv\n')
    control_file.write('./stl/' + param_file + '.param\n')
    control_file.close()

    return project_file


def pareto_3d_intersection(ecg_name, num_params, stl_template1, stl_template2, min_tuple, max_tuple, bound1, bound2,
                           delta, opt_level):
    # type: (str, int, str, str, tuple, tuple, int, int float, int) -> ResultSet

    param_name = "ecgLearn"
    create_param_file(param_name, num_params)

    nfile1 = './ecgLearn1.txt'
    nfile2 = './ecgLearn2.txt'
    create_project_file(nfile1, stl_template1, ecg_name, param_name)
    create_project_file(nfile2, stl_template2, ecg_name, param_name)

    human_readable = True

    # Definition of the n-dimensional space
    min_x, min_y, min_z = min_tuple
    max_x, max_y, max_z = max_tuple

    orac1 = OracleEpsSTLe(bound_on_count=bound1, intvl_epsilon=1)
    orac1.from_file(nfile1, human_readable)

    orac2 = OracleEpsSTLe(bound_on_count=bound2, intvl_epsilon=10)
    orac2.from_file(nfile2, human_readable)

    output_intersect = SearchIntersection3D(ora1=orac1, ora2=orac2,
                                            min_cornerx=min_x,
                                            min_cornery=min_y,
                                            min_cornerz=min_z,
                                            max_cornerx=max_x,
                                            max_cornery=max_y,
                                            max_cornerz=max_z,
                                            epsilon=EPS,
                                            delta=delta,
                                            max_step=10000,
                                            blocking=False,
                                            sleep=0,
                                            opt_level=opt_level,
                                            parallel=False,
                                            logging=False,
                                            simplify=False)
    return output_intersect


if __name__ == "__main__":
    # python3 ./example3d_intersection_eps.py 221 0 1 2 10
    min_tuple = (0.0, -1.0, -1.0)
    max_tuple = (70.0, 1.00, 1.0)
    ecg_name = str(sys.argv[1])
    bound1 = int(sys.argv[2])
    bound2 = int(sys.argv[3])
    opt_level = int(sys.argv[4])
    delta = 1.0 / float(sys.argv[5])
    t0 = time.time()
    rs1 = pareto_3d_intersection(ecg_name, 3, 'ecgInterTemplateFn3D', 'ecgInterTemplateFp3D', min_tuple, max_tuple,
                                 bound1, bound2, delta, opt_level)
    t1 = time.time()
    intersection = rs1.yup
    print("num intersection boxes:", len(intersection))
    print('TRESIMP: Time taken for intersection pareto (1):', t1 - t0)
    rs1.plot_3D(opacity=0.1, fig_title='Intersection of pareto fronts', var_names=['p1', 'p2', 'p3'], clip=True)
    rs1.to_file(ecg_name + "_characterizeOnlyOne" + sys.argv[5] + ".zip")
