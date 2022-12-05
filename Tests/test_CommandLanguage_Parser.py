import numpy
from ParetoLib.CommandLenguage.scf_parser import parser

simple_expressions = [
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

complex_expressions = [
    'let param p1, p2, ..., pn; let signal s1, s2, ..., sn; let probabilistic signal s1, s2, ..., sn;',
    'eval prob1 on s1 with p1 in [0, 0.5], p2 in [0, 0.5]'
]

# Parse an expression
res = parser.parse('let param p1, p2, ..., pn; let signal s1, s2, ..., sn; let probabilistic signal s1, s2, ..., sn;')

print('CommandLanguage Parser Tests')
print('>> Simple expression (' + numpy.size(simple_expressions) + ')');
counter = 1
for x in simple_expressions:
    print('Test nº' + counter + '/n')
    res = parser.parse(x)
    print(res)
    counter += 1
