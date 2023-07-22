import pytest
from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate


class TestController:
    tests = []

    def add_test(self, my_input, function, output):
        self.tests[1] = [my_input, function, output]

    def run(self):
        for i in range(len(self.tests)):
            real_output = self. tests[i][1](self.tests[0])
            print('Test nº' + str(i))
            if self.tests[i][2] == real_output:
                print(' passed')
            else:
                print(' FAILED')
                print('\n Obtained Output: ' + real_output)
                print('\n Waited Output: ' + self.tests[i][2])
                print('\n Tests have been abort!')
                break


# Command Language Translation Test Unit
print('CommandLanguage Translation Tests')
testController = TestController()

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
interval1 = []
interval1[0] = number1
interval1[1] = number2
interval2 = []
interval2[0] = number4
interval2[1] = number3
interval3 = []
interval3[0] = number5
interval3[1] = number6
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
