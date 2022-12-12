import numpy
import pytest
import ParetoLib.CommandLenguage.scf_lexer
from ParetoLib.CommandLenguage.scf_parser import parser


class ParserTree:
    @staticmethod
    def build_son(text):
        return ParserTree(text)

    def __init__(self, text):
        self.root = text[0]
        if numpy.size(text) >= 1:
            self.left = ParserTree.build_son(text[1])
            if numpy.size(text) == 2:
                self.right = ParserTree.build_son(text[2])


simple_expressions_inputs = [
    'let signal s1;',
    'let param p1;',
    'let probabilistic signal s1'
    'eval prob1 on s1',
    '[9, 8]'
    '[0,5]'
    'with p1 in [0, 5]'
    'F[0,t1]'
    'prop1 = F[0,t1]'
]

simple_expressions_outputs = [
    ['let', 'signal', 's1'],
    ['let', 'param', 'p1'],
    ['let', ['signal', 'probabilistic'], 'p1'],
    ['eval', ['on', 'prob1', 's1']],
    ['[]', ['9', '8']],
    ['with', ['in', 'p1', ['[]', ['9', '8']]]],
    ['with', ['in', 'p1', ['[]', ['9', '8']]]],
    ['F', ['[]', ['0', 't1']]],
    ['=', 'prop1', ['F', ['[]', ['0', 't1']]]]
]

simple_expressions_tree_outputs = []
for output in simple_expressions_outputs:
    simple_expressions_tree_outputs.append(ParserTree(output))

simple_expressions = []
for i in range(numpy.size(simple_expressions_inputs)):
    entry = [simple_expressions_inputs[i], simple_expressions_outputs[i]]
    simple_expressions.append(entry)

complex_expressions = (
    "let param p1, p2, ..., pn; let signal s1, s2, ..., sn; let probabilistic signal s1, s2, ..., sn;",
    "eval prob1 on s1 with p1 in [0, 0.5], p2 in [0, 0.5]"
)


class Test:
    def __init__(self, pre, post):
        self.precondition = pre
        self.postcondition = post

    def execute(self):
        result = parser.parse(self.precondition)
        assert result != self.postcondition


@pytest.mark.parametrice('tests', 'simpleTests')
class TextRunner:
    numTest = 0
    tests = []

    def add_test(self, tests):
        self.tests += tests
        self.numTest += 1

    def execute_tests(self):
        j = 0
        for test in self.tests:
            print('Test nº' + str(j) + ' : ')
            test.execute()
            print('Passed!' + '\n')
            j += 1


@pytest.mark.parametrice('conditions', 'simple_expressions')
class SimpleTestUnit:
    @staticmethod
    def test_simple_expressions(conditions):
        # Init the SimpleTests
        simpleTests = []
        # condition[0] is the precondition and condition[1] is the postcondition
        for condition in conditions:
            simpleTests.append(Test(condition[0], condition[1]))

        # Init the ComplexTests
        # complexTests = []
        # for condition in conditions :
        #   complexTest.append(Test(condition.pre, condition.post))

        # Init the TextRunner
        textRunner = TextRunner

        # Add tests
        textRunner.add_test(textRunner.self, simpleTests)

        # Execute the tests
        textRunner.execute_tests(textRunner.self)


# Header of the Command Language Test Unit (Temporal Logic Language)
print('CommandLanguage Parser Tests')
print('>> Simple expression (' + str(numpy.size(simple_expressions)) + ')')

# Execution of the tests with simple expressions
SimpleTestUnit.test_simple_expressions(simple_expressions)
