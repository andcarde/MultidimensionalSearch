from ply.lex import lex

# --- Tokenizer

# Here I describe the reserved words.
reserved = ( 'let', 'param', 'signal', 'probabilistict', 'allocator', 'and', 'not', 'eval', 'on',
        'with', 'in', ',', '[', '(', ')', ';')

concepts = ('iParam', 'iSignal', 'iProbabilisticSignal', 'iTime', 'iFunctionName')
expressions = ('interval', 'function', 'assignment', 'probabilisticExp', 'evalExp')

# All tokens must be named in advance.
tokens = ( 'LET', 'PARAM', 'SIGNAL', 'PROBABILISTIC', 'COMMA', 'SEMICOLON', 'ASSIGNMENT',
           'AND', 'NOT', 'EVAL', 'ON', 'WITH', 'IN', 'CLOSED_LEFT_PA', 'CLOSED_RIGHT_PA', 'POINT',
           'NAME', 'NUMBER' ) + list(reserved.values())

# Ignored characters
t_ignore = ' \t'

# Token matching rules are written as regexs
t_LET = r'[l][e][t]'
t_PARAM = r'[p][a][r][a][m]'
t_SIGNAL = r'[s][i][g][n][a][l]'
t_PROBABILISTIC = r'[p][r][o][b][a][b][i][l][i][s][t][i][c]'
t_COMMA = r'\,'
t_SEMICOLON = r'\;'
t_ASSIGNMENT = r'[:][=]'
t_AND = r'[a][n][d]'
t_NOT = r'[n][o][t]'
t_EVAL = r'[e][v][a][l]'
t_ON = r'[o][n]'
t_WITH = r'[w][i][t][h]'
t_IN = r'[i][n]'
t_CLOSED_LEFT_PA = r'['
t_CLOSED_RIGHT_PA = r']'
t_POINT = r'\.'
t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
t_NUMBER = r'[0-9][.]?[0-9]*'
# Alternative: r'[0-9]*[[.][0-9]*]?'

# A function can be used if there is an associated action.
'''
for (size >= 2)
    name_list(t.trim(0, size / 2))
    name_list(t.trim(size / 2, size))
    size = size / 2
'''
# Build the lexer
lex.lex()