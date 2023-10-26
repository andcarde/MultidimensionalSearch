
### test_CommandLanguage_Translation.py

from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate
from ParetoLib.CommandLanguage.FileUtils import read_file
# from Tests.test_CommandLanguage_Parser_4 import print_tree
from Tests.View.TreeViewer import list_to_tree, view_tree


def process(stle2_text):
    print(stle2_text)
    _list = parser.parse(stle2_text)
    print(_list)
    tree = list_to_tree(_list)
    view_tree(tree)
    translation = translate(_list)
    return translation


class Test:
    """
    We host each test along with its output
    """

    def __init__(self, _id, _stle2, _param, _stle1):
        self.id = _id
        self.stle2 = _stle2
        self.param = _param
        self.stle1 = _stle1

    def to_test(self):
        translation = process(self.stle2)
        if len(translation.errors) > 0:
            print("Test nº" + self.id + " has failed.")
            print("The following errors have been generated:")
            for error in translation.errors:
                print('-' + error)
        else:
            sol_stle1 = read_file(translation.stle1_packs[0].program_file_path)
            sol_param = read_file(translation.stle1_packs[0].parameters_file_path)
            if sol_param != self.param:
                print("Test nº" + str(self.id) + " has failed.")
                print("desired_parameter: \n" + self.param)
                print("obtained_parameter: \n" + sol_param)
            if sol_stle1 != self.stle1:
                print("Test nº" + str(self.id) + " has failed.")
                print("desired_parameter: \n" + self.stle1)
                print("obtained_parameter: \n" + sol_stle1)


def build_test1():
    # Test 1 -- STLE2
    '''
    stle2 = "let param p1, p2;" + "\n" \
            + "let signal s1;" + "\n" \
            + "prop1 := G [8, 12] p1 and p2" + "\n" \
            + "eval prop1 with p1 in [5, 8], p2 in [7, inf]"
    '''
    stle2 = "let param p1;" + "\n" \
            + "let signal s1;" + "\n" \
            + "prop1 := G [8, 12] p1;" + "\n" \
            + "eval prop1 with p1 in [5, 8]"

    # Test 1 -- Parameters
    parameters = "p1 5 8" + "\n" \
                 + "p2 7"

    # Test 1 -- STLE1
    stle1 = "G ( 8 12 ) ( and p1 p2 )"

    return Test(1, stle2, parameters, stle1)


def create_test(_id, name):
    name = '..\\Language\language_examples\\' + name
    return Test(_id + 1, read_file(name + '_Input_STLe2.stle'),
                read_file(name + '_Output_Parameters.txt'), read_file(name + '_Output_STLe1.txt'))


def build_tests():
    # Map [archivo STLE2] -> ([archivo STLE1], [archivo Parameters])
    tests = [
        build_test1(),
    ]
    tests.append(create_test(len(tests), 'Test100'))
    return tests


def test_translation():
    """
    test_CommandLanguage_Translation_2.py Execute Method
    Run the translation test suite
    """

    tests = build_tests()
    for test in tests:
        test.to_test()


if __name__ == "__main__":
    test_translation()
