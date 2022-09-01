import sys

from ParetoLib.Oracle.OracleEpsSTLe import OracleEpsSTLe
from ParetoLib.Search.Search import SearchIntersectionND_2, EPS, STEPS
from ParetoLib.Search.ResultSet import ResultSet
from example3d_intersection_eps import create_project_file, create_param_file


def pareto_ND_Intersection_eps(ecg_name, num_params, stl_template1, stl_template2,
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
    # This script learns to classify the day the ECG was recorded. The classifier consists of a Parametric STL formula
    # with parameters (p1, p2, p3). The PSTL is a binary classifier that determines if the ECG was recorded on day 1 or
    # on day 5 for the same patient. The result of training the classifier is the set of valuations of the parameter
    # space such that the detector misclassifies 'bound1' false negatives and 'bound2' false positives.
    #
    # In this example, the following call classifies an ECG taken in day 5 with a resolution of the parameter space
    # of 1/10 (delta = 10). The opt_level = 0 means that the algorithm extracts a single point of the parameter space
    # instead of the full satisfaction area (green boxes).
    #
    # python3 ./examplend_intersection_eps.py 5 0 10
    # Work without constraints on parameters.
    list_intervals = [(0, 30), (0, 20), (-10, 10), (-10, 10), (-10, 10), (0, 100), (0, 100)]
    list_constraints = []
    num_params = 7
    ecg_name = str(sys.argv[1])
    opt_level = int(sys.argv[2])
    delta = float(sys.argv[3]) / 1000
    bound1 = 0
    bound2 = 0
    rs = pareto_ND_Intersection_eps(ecg_name, num_params, 'ecgInterTemplateEpsFnND', 'ecgInterTemplateEpsFpND',
                                    list_intervals, list_constraints, bound1, bound2, delta, opt_level)
    intersection = rs.yup
    print('intersection number:', len(intersection))
    print('intersection box:', intersection)
