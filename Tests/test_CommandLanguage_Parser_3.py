from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate
from Tests.View.TreeViewer import view_tree
from Tests.View.TreeViewer import list_to_tree
from Tests.test_CommandLanguage_Translation_1 import TestController

input1 = '''
    let signal s1;
    let param p1;
    prop1 := F[0,p1] s1 < 0;
    eval prob1 with p1 in [0, 0.5]
'''

list_output1 = parser.parse(input1)
print(list_output1)
list_output2 = ['SPEC_FILE',
                ('DEFINITIONS', ('SIGNAL_LIST', 's1'), ('PARAM_LIST', 'p1')),
                ('PROP_LIST', ['PROP', 'prop1', ('PHI', 'F', ('INTVL', 0.0, 'p1'), ('PHI', ('FUNC', '<', 's1', 0.0)))]),
                ('EVAL_LIST', ('EVAL_EXPR', 'prob1', ('p1', ('INTVL', 0.0, 0.5))))]
print(list_output2)
tree_output1 = list_to_tree(list_output1)
view_tree(tree_output1)

text_stle2 = '''let signal signal1, signal2;
let param param1;
prop1 := signal1 until [ param1 , 5 ] signal2 ;
eval prop1 with param1 in [1, 3]'''

text_stl1 = '( StlUntil [ param1 , 5 ] x1 x2 )'
list_stl1 = ['StlUntil', ['Interval', 'param1', 5], 'x1', 'x2']
real_translate_ex1 = '''
    ( F (0 p1) < s1 0 )
'''
observed_translate_output = translate(tree_output1)


def test_parser():
    print('Parser Test Unit')
    test_controller = TestController()
    test_controller.add_test('Test4_Input_STLe2.txt', parser.parse, 'example1_output')
    test_controller.run()


if __name__ == "__main__":
    test_parser()
