import sys

from ParetoLib.Oracle.OracleEpsSTLe import OracleEpsSTLe
from ParetoLib.Search.Search import SearchIntersectionND_2, EPS, STEPS


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


def pareto_4d_intersection_eps(ecg_name, num_params, stl_template1, stl_template2,
                               list_intervals, list_contraints, bound1, bound2, delta, opt_level):
    # type: (str, int, str, str, list, list, int, int, float, int) -> ResultSet

    param_name = "ecgLearn"
    create_param_file(param_name, num_params)

    nfile1 = './ecgLearn1.txt'
    nfile2 = './ecgLearn2.txt'
    create_project_file(nfile1, stl_template1, ecg_name, param_name)
    create_project_file(nfile2, stl_template2, ecg_name, param_name)

    human_readable = True

    orac1 = OracleEpsSTLe(bound_on_count=bound1, intvl_epsilon=1)
    orac1.from_file(nfile1, human_readable)

    orac2 = OracleEpsSTLe(bound_on_count=bound2, intvl_epsilon=1)
    orac2.from_file(nfile2, human_readable)

    output_intersect = SearchIntersectionND_2(orac1, orac2,
                                              list_intervals, list_contraints,
                                              epsilon=EPS,
                                              delta=delta,
                                              max_step=STEPS,
                                              blocking=False,
                                              sleep=0,
                                              opt_level=opt_level,
                                              parallel=False,
                                              logging=False,
                                              simplify=False)
    return output_intersect


if __name__ == "__main__":
    # This script learns to detect pulses in ECGs. The detector consists of a Parametric STL formula with
    # parameters (p1, p2, p3). The result of training the detector is the set of valuations of the parameter space such
    # that the detector misclassifies 'bound1' false negatives and 'bound2' false positives.
    #
    # In this example, the following call optimizes the detector for the ECG 221, with up to 0 false negatives, 1 false
    # positives and a resolution of the parameter space of 1/10 (delta = 10). The opt_level = 2 means that the algorithm
    # computes the satisfaction area of the parameter space (green boxes) instead of a single point.
    #
    # python3 ./example4d_intersection_eps.py 100 2 2 0 100
    # ecg_name = str(sys.argv[1])
    # bound1 = int(sys.argv[2])
    # bound2 = int(sys.argv[3])
    # opt_level = int(sys.argv[4])
    # delta = 1.0 / float(sys.argv[5])

    ecg_name = "100"
    bound1 = 33
    bound2 = 33
    opt_level = 0
    delta = 1.0 / 100.0

    min_tuple = (0.0, -1.0, -1.0, 0.0)
    max_tuple = (70.0, 1.00, 1.0, 600.0)
    list_intervals = [(min_i, max_c) for min_i, max_c in zip(min_tuple, max_tuple)]
    list_constraints = []

    rs1 = pareto_4d_intersection_eps(ecg_name, 4, 'ecgInterTemplateFn4D', 'ecgInterTemplateFp4D', list_intervals,
                                     list_constraints, bound1, bound2, delta, opt_level)
    intersection = rs1.yup
    print("num intersection boxes:", len(intersection))
    # rs1.plot_3D(opacity=0.1, fig_title='Intersection of pareto fronts', var_names=['p1', 'p2', 'p3'])
    rs1.to_file(ecg_name + "_characterizeOnlyOne" + sys.argv[5] + ".zip")
    rs1.ylow = []
    rs1.border = []
    print(intersection)

