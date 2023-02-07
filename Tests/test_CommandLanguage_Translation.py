import numpy
from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate

class TestController :
    tests = []
    def addTest(self, entrada, function, salida) :
        self.tests[1] = [entrada, salida]
    def run(self) :
        for i in numpy.size(self.tests) :
            salidaReal = self. tests[i][1](self.tests[0])
            print('Test nº' + i)
            if self.tests[i][2] == salidaReal :
                print(' passed')
            else :
                print(' FAILED')
                print('\n Obtained Output: ' + salidaReal)
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


# Test U
# Test F
# Test G
def test_g():
    # G [a,b] X
    input = "G[1,4] x > 0"
    input_tree = parser.parse(input)
    # input_tree == (G, (1, 4), (<, x, 0))
    output_tree = translate(input_tree)
    # output_tree == "(G <INTERVAL> <FORMULA>)"
    # output_tree == "(G [1, 4] (< x 0))"
    input_tree[0] = ["G"]
    self.assertEqual(output_tree, "(G [1, 4] (< x 0))")
    assert output_tree == "(G [1, 4] (< x 0))", "Mensaje de error"


intvl1 = (1, 2)
intvl2 = (5, 7)
@pytest.mark.parametrize("intvl", [intvl1, intvl2])
def test_g_parametrico(intvl):
    # G [a,b] X
    a, b = intvl
    input = "G [{0},{1}] x > 0".format(a, b)
    input_tree = parser.parse(input)
    # input_tree == (G, (1, 4), (<, x, 0))
    output_tree = translate(input_tree)
    # output_tree == "(G <INTERVAL> <FORMULA>)"
    # output_tree == "(G [1, 4] (< x 0))"
    input_tree[0] = ["G"]
    self.assertEqual(output_tree, "(G [1, 4] (< x 0))")
    assert output_tree == "(G [1, 4] (< x 0))", "Mensaje de error"
