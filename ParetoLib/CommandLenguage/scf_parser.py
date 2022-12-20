from ply.yacc import yacc
import ParetoLib.CommonLanguage.scf_lexer

tokens = scf_lexer.tokens

def p_not(t):
    '''
    PROB: NOT + PROB
    '''
    t[0] = ('not', t[0], t[1])


def p_and(t):
    '''
    PROB = PROB AND PROB
    '''
    t[0] = ('and_mas_otrascosas', t[1], t[3])


def p_interval(t):
    '''
    INTERVAL = CLOSED_LEFT_PA NUMBER COMMA NUMBER CLOSED_RIGHT_PA
    '''
    t[0] = ('interval', t[1], t[3])


def p_in(t):
    '''
    IN = I_PROBABILISTIC IN INTERVAL
    '''
    t[0] = ('in', t[1], t[0], t[2])


def p_prob_enum(t):
    '''
    PROB_ENUM = IN COMMA IN
    '''
    t[0] = ('prob_enum', t[1], t[0], t[2])


def p_signal_enum(t):
    '''
    SIGNAL_ENUM = ISIGNAL COMMA ISIGNAL
    '''
    t[0] = ('signal_enum', t[1], t[0], t[2])


def p_question(t):
    '''
    QUESTION = SIGNAL_ENUM WITH PROB_ENUM
    '''
    t[0] = ('signal_enum', t[1], t[0], t[2])


def p_expression_list(t):
    '''
    ID_LIST: ID | ID, ID_LIST
    '''
    # Using real lists here
    if len(t) == 2:
        t[0] = ('param', t[1])
    elif len(t) == 4:
        t[0] = ('param', t[1], t[3])
    else:
        assert False


# Write the matching regex in the docstring.
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

# let prop := t1, t2, t3, t11, t21, t34


def p_expression_search(t):
    t[0] = ('search', t[2], t[1], t[3])


def p_expression_comma(t):
    t[0] = ('group', t[2], t[1], t[3])


def p_expression_on(t):
    t[0] = ('on', t[2], t[1], t[3])


def p_expression_with(t):
    t[0] = ('with', t[2], t[1], t[3])


def p_expression(t):
    '''
    expression : term PLUS term
               | term MINUS term
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : term PLUS term
    #   p[0]     : p[1] p[2] p[3]
    #
    t[0] = ('binop', t[2], t[1], t[3])


def p_expression_term(t):
    '''
    expression : term
    '''
    t[0] = t[1]


def p_term(t):
    '''
    term : factor TIMES factor
         | factor DIVIDE factor
    '''
    t[0] = ('binop', t[2], t[1], t[3])


def p_term_factor(t):
    '''
    term : factor
    '''
    t[0] = t[1]


def p_factor_number(t):
    '''
    factor : NUMBER
    '''
    t[0] = ('number', t[1])


def p_factor_name(t):
    '''
    factor : NAME
    '''
    t[0] = ('name', t[1])


def p_factor_unary(t):
    '''
    factor : NOT factor
    '''
    t[0] = ('unary', t[1], t[2])


def p_factor_grouped(t):
    '''
    factor : LPAREN expression RPAREN
    '''
    t[0] = ('grouped', t[2])


def p_error(t):
    print(f'Syntax error at {t.value!r}')


# Build the parser
tmpdirname = "/tmp/"
parser = yacc.yacc(start='param', debugfile=tmpdirname + 'parser.out', write_tables=True)
