
from ParetoLib.CommandLanguage.Lexer import lex
from ParetoLib.CommandLanguage.Parser import parser
from Tests.tree_printer import printTree
from ParetoLib.CommandLanguage.Translation import translate

"""
ParetoLib package.
"""
__version__ = '1.0.0'
__name__ = 'Command Language Tester'
__all__ = ['CommandLanguage']


# -------------------------------------------------------------------------------

class MissingExtDependencyError(Exception):
    """
    Missing an external dependency. Used for our unit tests to allow skipping
    tests with missing external dependencies, e.g. missing command line tools.
    """
    pass

# -------------------------------------------------------------------------------

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
    lexer = lex.lex()
    lexer.input("i")
    lexer.token()
    out_lexer = lexer.get()
    out_parser = parser.parse(out_lexer, tracking=True)
    print('Output of the Parser\n')
    printTree(out_parser)
    print('Output of the Translator\n')
    out_translator = translate(out_parser)
    printTree(out_translator)