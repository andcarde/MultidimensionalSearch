from ParetoLib.CommandLanguage.Lexer import lexer
from ParetoLib.CommandLanguage.Parser import parser


def print_tree(tree):
    if tree is None:
        print('None')
    elif not isinstance(tree, (list, tuple)):
        print(tree)
    else:
        for j in range(len(tree)):
            print('{(' + str(j) + ')')
            print_tree(tree[j])
            print('},')


if __name__ == '__main__':
    '''
    (
        'let signal s1;' + ' ' +
        'prop5 := s1;' + ' ' +
        'prop6 := p1 > 5;' + ' ' +
        'prop7 := not prop6;' + ' ' +
        'prop9 := prob prop6;' + ' ' +
        '<boolean> prop8 := F[0, 1] s1' + ' ' +
        '<number> prop9 := ON[0, 1] max (s1)' + ' ' +
        '<function> prop9 := ON[0, 1] der (s1)'
    ),
    '''
    parserInput = (
            'let param p1, p2;' + '\n' +
            'let signal s1, s2, s3;' + '\n' +
            'let probabilistic signal ps1, ps2;' + '\n' +
            'prop1 := F[0,p1] (s1 < 0);' + '\n' +
            'prop2 := F[0,p2] (s2 + s3) > 1.0;' + '\n' +
            'prop3 := prop1 and not prop2;' + '\n' +
            'prop4 := Pr F (s3 < 0);' + '\n' +
            'prop5 := on[1.4,.3] Min s3;' + '\n' +
            'prop6 := on[4,8] Int (G (s1 + 2));' + '\n' +
            'prop7 := s2 U[0,p2] (s3 < s4);' + '\n' +
            'eval prob1 on s3 with p1 in [0, 0.5], p2 in [0, 0.5]' + '\n' +
            'eval prob2 on s1, s3 with p1 in [0, 0.5], p2 in [0, 0.5]'
    )
    # 'prop1 := F[0,p1] s1 < 0;'
    # (:=(prop1, F([0, p1], < (s1, 0))))
    '''
    'let param p1, p2;' + '\n' +
    'let signal s1, s2, s3;' + '\n' +
    'let probabilistic signal ps1, ps2;' + '\n' +
    'prop1 := F[0,p1] (s1 < 0);' + '\n' +
    'prop2 := F[0,p2] (s2 + s3) > 1.0;' + '\n' +
    'prop3 := prop1 and not prop2;' + '\n' +
    'prop4 := Pr F (s3 < 0);' + '\n' +
    'eval prob1 with p1 in [0, 0.5], p2 in [0, 0.5]' + '\n' +
    'eval prob2 with p1 in [0, 0.5], p2 in [0, 0.5]'
    ...
    'prop5 := ON [4, 8] Int (G (s1 + 2));' + '\n' +
    '''

    # for i in input:
    out_parser = parser.parse(input=parserInput, tracking=True, lexer=lexer)
    print('Output of the Parser\n')
    print(out_parser)
    print(out_parser)
    '''
    print('Output of the Translator\n')
    out_translator = translate(out_parser)
    printTree(out_translator)
    '''
