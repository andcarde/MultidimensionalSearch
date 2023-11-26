# <test_CommandLanguage_Translation.py>

from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate
from ParetoLib.CommandLanguage.FileUtils import read_file
# from Tests.test_CommandLanguage_Parser_4 import print_tree
from Tests.View.TreeViewer import list_to_tree, view_tree
import os


def get_temporal_number(temporal_number):
    try:
        number = float(temporal_number)
        if number.is_integer():
            return str(int(number))
        return str(number)
    except ValueError:
        return temporal_number


def parse_numbers_in_string(string):
    result = ""
    temporal_number = ""

    for char in string:
        if char.isdigit() or char == '.':
            temporal_number += char
        else:
            result += get_temporal_number(temporal_number) + char
            temporal_number = ""

    result += get_temporal_number(temporal_number)

    return result


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
            sol_stle1 = parse_numbers_in_string(sol_stle1)
            sol_param = read_file(translation.stle1_packs[0].parameters_file_path)
            sol_param = parse_numbers_in_string(sol_param)
            errors_exist = False
            if sol_param != self.param:
                print("Test nº" + str(self.id) + " has failed.")
                print("desired_parameter: \n" + self.param)
                print("obtained_parameter: \n" + sol_param)
                errors_exist = True
            if sol_stle1 != self.stle1:
                print("Test nº" + str(self.id) + " has failed.")
                print("desired_parameter: \n" + self.stle1)
                print("obtained_parameter: \n" + sol_stle1)
                errors_exist = True
            if not errors_exist:
                print("Test nº" + str(self.id) + " has been successful.")


class TestCreator:
    def __init__(self):
        self.counter = 0

    def create_test(self, name):
        name = os.path.join('Language', 'language_examples', name)
        self.counter += 1
        return Test(self.counter,
                    read_file(name + '_Input_STLe2.stle'),
                    read_file(name + '_Output_Parameters.txt'),
                    read_file(name + '_Output_STLe1.txt')
                    )


def build_tests():
    test_creator = TestCreator()
    # Map [archivo STLE2] -> ([archivo STLE1], [archivo Parameters])
    tests = [
        test_creator.create_test('Test100'),
        test_creator.create_test('Test5'),
        test_creator.create_test('Test3-1'),
        test_creator.create_test('Test3-2'),
        test_creator.create_test('Test1'),
        test_creator.create_test('Test4'),
    ]
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
