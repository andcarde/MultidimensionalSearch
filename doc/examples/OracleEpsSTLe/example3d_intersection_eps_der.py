import sys

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
    # type: (str, int, str, str, tuple, tuple, int, int, float, int) -> ResultSet

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
    # This script learns to detect pulses in ECGs. The detector consists of a Parametric STL formula with
    # parameters (p1, p2, p3). The result of training the detector is the set of valuations of the parameter space such
    # that the detector misclassifies 'bound1' false negatives and 'bound2' false positives.
    #
    # In this example, the following call optimizes the detector for the ECG 221, with up to 0 false negatives, 1 false
    # positives and a resolution of the parameter space of 1/10 (delta = 10). The opt_level = 2 means that the algorithm
    # computes the satisfaction area of the parameter space (green boxes) instead of a single point.
    #
    # python3 ./example3d_intersection_eps.py 221 0 1 2 10
    # python3 ./example3d_intersection_eps.py 123 1 0 2 10
    # python3 ./example3d_intersection_eps.py 100 0 33 2 10
    # python3 ./example3d_intersection_eps_der.py 221 5 5 0 10
    min_tuple = (0.0, 0.0, 0.0)
    max_tuple = (450.0, 50.0, 100.0)
    ecg_name = str(sys.argv[1])
    bound1 = int(sys.argv[2])
    bound2 = int(sys.argv[3])
    opt_level = int(sys.argv[4])
    delta = 1.0 / float(sys.argv[5])
    rs1 = pareto_3d_intersection(ecg_name, 3, 'ecgInterTemplateFn3DDer', 'ecgInterTemplateFp3DDer', min_tuple, max_tuple,
                                 bound1, bound2, delta, opt_level)
    intersection = rs1.yup
    print("num intersection boxes:", len(intersection))
    # rs1.plot_3D(opacity=0.1, fig_title='Intersection of pareto fronts', var_names=['p1', 'p2', 'p3'])
    rs1.to_file(ecg_name + "_characterizeOnlyOne" + sys.argv[5] + ".zip")
    rs1.ylow = []
    rs1.border = []
    rs1.plot_3D(fig_title='Intersection of pareto fronts', var_names=['p1', 'p2', 'p3'])

