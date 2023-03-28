
from ParetoLib.CommandLanguage.Lexer import lex
from ParetoLib.CommandLanguage.Parser import parser
from Tests.tree_printer import printTree
from ParetoLib.CommandLanguage.Translation import translate

if __name__ == '__main__':
    input = [(
            'let signal s1;' + ' ' +
            'prop5 := s1;' + ' ' +
            'prop6 := p1 > 5;' + ' ' +
            'prop7 := not prop6;' + ' ' +
            'prop9 := prob prop6;' + ' ' +
            '<boolean> prop8 := F[0, 1] s1' + ' ' +
            '<number> prop9 := ON[0, 1] max (s1)' + ' ' +
            '<function> prop9 := ON[0, 1] der (s1)')
    ]

    for i in input:
        out_parser = parser.parse(i, tracking=True)
        print('Output of the Parser\n')
        printTree(out_parser)
        print('Output of the Translator\n')
        out_translator = translate(out_parser)
        printTree(out_translator)
