# <test_CommandLanguage_Translation.py>

from ParetoLib.CommandLanguage.FileUtils import read_file
from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate
from Tests.View.TreeViewer import list_to_tree, view_tree
import os

# Settings

# Type: bool
SHOW_SYNTAX_TREE_IN_CONSOLE = True
# Type: bool
SHOW_SYNTAX_TREE_IN_VIEWER = False


def get_temporal_number(temporal_number):
    if temporal_number == "":
        return ""
    try:
        # Type: float
        number = float(temporal_number)
        if number.is_integer():
            # Type: int
            number = int(number)
        return str(number)
    except ValueError:
        print('!! Exception occurred: \'ValueError\'' +
              '\n   ' + 'Location: test_CL_T.py > get_temporal_number' +
              '\n   ' + f'Info: The provided temporal_number ({temporal_number}) could not be converted to a number.')
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

    if SHOW_SYNTAX_TREE_IN_CONSOLE:
        # Print in console the syntax tree structure on plain text
        print(_list)

    if SHOW_SYNTAX_TREE_IN_VIEWER:
        tree = list_to_tree(_list)
        # Show the tree in the view util
        view_tree(tree)

    translation = translate(_list)
    return translation


def analyze_string(text):
    print(f'** Analyzing: {text}')
    for i in range(len(text)):
        if text[i] == '\n':
            print(f' - Char {i}: \\n)')
        elif text[i] == '\r':
            print(f' - Char {i}: \\r)')
        elif text[i] == '\t':
            print(f' - Char {i}: \\t)')
        elif text[i] == ' ':
            print(f' - Char {i}: \\w)')
        else:
            print(f' - Char {i}: {text[i]}')


def compare_strings(str1, str2):
    print(f'** Comparing strings: "{str1}", "{str2}"')

    if str1 == str2:
        print(" - Strings are identical")
    elif len(str1) != len(str2):
        print(f" - Strings have different lengths: {len(str1)} vs {len(str2)}")
        analyze_string(str1)
        analyze_string(str2)
    else:
        # Type: bool
        missing = True
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                missing = False
                print(f" - Difference found at index {i}: '{str1[i]}' vs '{str2[i]}'")

        if missing:
            print(" - Strings are different but no specific difference found")


class Test:
    """
    We host each test along with its output
    """

    def __init__(self, _id, name, _stle2, _param, _stle1):
        self.id = _id
        self.name = name
        self.stle2 = _stle2
        self.param = _param
        self.stle1 = _stle1

    def to_test(self):
        translation = process(self.stle2)
        if len(translation.errors) > 0:
            print(" + " + "Test nº" + str(self.id) + ", named " + self.name + ", has failed.")
            print("    * " + "The following errors have been generated:")
            for error in translation.errors:
                print('    - ' + error)
        else:
            sol_stle1 = read_file(translation.stle1_packs[0].program_file_path)
            sol_stle1 = parse_numbers_in_string(sol_stle1)
            sol_param = read_file(translation.stle1_packs[0].parameters_file_path)
            sol_param = parse_numbers_in_string(sol_param)
            errors_exist = (sol_param != self.param or sol_stle1 != self.stle1)
            if not errors_exist:
                print(" + " + "Test nº" + str(self.id) + ", named " + self.name + ", has been successful.")
            else:
                print(" + " + "Test nº" + str(self.id) + ", named " + self.name + ", has failed.")
                if sol_param != self.param:
                    print("Inequality on parameters:")
                    print("Desired parameters:\n" + self.param)
                    print("Obtained parameters:\n" + sol_param)
                    compare_strings(self.param, sol_param)
                if sol_stle1 != self.stle1:
                    print("Inequality on formula:")
                    print("Desired formula:  " + self.stle1)
                    print("Obtained formula: " + sol_stle1)
                    compare_strings(self.stle1, sol_stle1)


class TestCreator:
    def __init__(self):
        self.counter = 0

    def create_test(self, name):
        name = os.path.join('Language', 'language_examples', name)
        self.counter += 1
        return Test(
            self.counter,
            name,
            read_file(name + '_Input_STLe2.stle'),
            read_file(name + '_Output_Parameters.txt'),
            read_file(name + '_Output_STLe1.txt')
        )


def build_tests():
    # Type: class TestCreator
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
        try:
            test.to_test()
        except Exception as e:
            print("Exception occurred:", e)


if __name__ == "__main__":
    test_translation()
