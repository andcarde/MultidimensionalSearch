
import os
import pytest
from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate
from ParetoLib.CommandLanguage.Utils import print_tree


class TestController:
    tests = []

    def add_test(self, my_input, function, output):
        self.tests.append([read(my_input), function, read(output)])

    def run(self):
        for i in range(len(self.tests)):
            my_input = self.tests[i][0]
            function = self.tests[i][1]
            output = self.tests[i][2]
            real_output = function(my_input)
            print('Test nº' + str(i))
            if output == real_output:
                print(' passed')
            else:
                print(' FAILED')
                print('\n Obtained Output: ' + real_output)
                print('\n Waited Output: ' + output)
                print('\n Tests have been abort!')
                break


# Basic Types
# 1. Names
name1 = 'p1'
name2 = 'function'
name3 = 'function09123'

# 2. Number
number1 = 7
number2 = 324
number3 = 93112
number4 = 234
number5 = 12
number6 = 98

# Intervals
# definition: <INTERVAL> ::= (<NUMBER> <NUMBER>)
interval1 = [number1, number2]
interval2 = [number4, number3]
interval3 = [number5, number6]
interval4 = (1, 2)
interval5 = (5, 7)


# Test U
def test_u():
    pass


# Test F
def test_f():
    pass


# Test G
@pytest.mark.parametrize('interval', [interval4, interval5])
def test_parametric_g(interval):
    a, b = interval

    # G [a,b] X
    my_input = 'G [{0},{1}] x > 0'.format(a, b)

    # input_tree == (G, (1, 4), (<, x, 0))
    input_tree = parser.parse(my_input)

    # output_tree == "(G <INTERVAL> <FORMULA>)"
    # output_tree == "(G [1, 4] (< x 0))"
    output_tree = translate(input_tree)

    input_tree[0] = ["G"]
    assert output_tree == "(G [1, 4] (< x 0))", "The expected output do not correspond with the obtained."


def redirect(file):
    # Get the absolute path of the current directory where test_CommandLanguage_Translation_1.py is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Combine current path with tests sub-folders and file name
    relative_path = os.path.join(current_dir, "Language", "examples", file + ".txt")

    return relative_path


def read(file):
    rute = redirect(file)
    print(rute)
    try:
        with open(rute, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return None


def process(my_input):
    input_tree = parser.parse(my_input)
    print('[test_CommandLanguage_Translation_1.py] [process(..)]')
    print(my_input)
    print_tree(input_tree)
    output_tree = translate(input_tree)
    return output_tree


def main():
    # Command Language Translation Test Unit
    print('CommandLanguage Translation Tests')
    test_controller = TestController()

    def salute(name):
        if name == 'hola':
            return 'adios'
        else:
            return 'bye'

    test_controller.add_test('hola', salute, 'adios')
    test_controller.add_test('hello', salute, 'bye')
    test_controller.add_test('Test1_Input', salute, 'Test1_Output')
    test_controller.add_test('STLE3Ex3', process, 'STLE1Ex3')
    test_controller.run()


if __name__ == "__main__":
    main()
