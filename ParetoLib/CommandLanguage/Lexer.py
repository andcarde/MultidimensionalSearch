import ply.lex as lex

# Reserved words: The text appears in the left column and the representation appears in the right.
reserved = {'let': 'LET',
            'param': 'PARAM',
            'signal': 'SIGNAL',
            'probabilistic': 'PROBABILISTIC',
            'eval': 'EVAL',
            'on': 'ON',
            'with': 'WITH',
            'in': 'IN',
            # Boolean operators
            'and': 'AND',
            'or': 'OR',
            'not': 'NOT',
            '->': 'IMPLY',
            # Temporal operators
            'F': 'F',
            'G': 'G',
            'U': 'UNTIL',
            # Quantitative operators
            'Min': 'MIN',
            'Max': 'MAX',
            'Pr': 'PROB',
            'Der': 'DER',
            'Int': 'INT'}

# All tokens must be named in advance.
tokens = [
             'ID', 'NUMBER', 'ASSIGNMENT',
             'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
             'VAR',
             'NEQ', 'LEQ', 'LESS', 'GEQ', 'GREATER',
             'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK',
             'COMMA', 'SEMICOLON'
         ] + list(reserved.values())

# Ignored characters
t_ignore = ' \t\n'

# Token matching rules are written as regexs
t_COMMA = r'\,'
t_SEMICOLON = r'\;'

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

t_ASSIGNMENT = r':='
t_NEQ = r'<>'
t_LEQ = r'<='
t_LESS = r'<'
t_GEQ = r'>='
t_GREATER = r'>'

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'


# A regular expression rule with some action code
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9\'\.]*'
    t.type = reserved.get(t.value, 'ID')  # Check for reserved words
    return t


def t_NUMBER(t):
    r'\d*\.?\d+ | inf | -inf'
    try:
        t.value = float(t.value)
        t.type = 'NUMBER'
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0.0
    return t


def t_BOOL(t):
    r'(?i)true|false'
    # (?i) = ignore case.
    # Alternatively:
    # import re
    # lex.lex(reflags=re.IGNORECASE)

    try:
        t.value = bool(t.value)
    except ValueError:
        print("Not properly formatted Bool value %d", t.value)
        t.value = False
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

# Usage mode:
# -----------
# from ParetoLib.CommandLanguage.Lexer import *
# lexer = lex.lex()
# lexer.input("3")
# lexer.token()
