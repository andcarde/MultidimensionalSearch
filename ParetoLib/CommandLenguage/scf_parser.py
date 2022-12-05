from ply.yacc import yacc

def p_not(t):
    '''
    PROB: NOT + PROB
    '''
    p[0] = ('not', p[0], p[1])


def p_and(t):
    '''
    PROB = PROB AND PROB
    '''
    p[0] = ('and', p[1], p[0], p[2])


def p_interval(t):
    '''
    INTERVAL = CLOSED_LEFT_PA NUMBER COMMA NUMBER CLOSED_RIGHT_PA
    '''
    p[0] = ('interval', p[1], p[3])


def p_in(t):
    '''
    IN = I_PROBABILISTIC IN INTERVAL
    '''
    p[0] = ('in', p[1], p[0], p[2])


def p_prob_enum(t):
    '''
    PROB_ENUM = IN COMMA IN
    '''
    p[0] = ('prob_enum', p[1], p[0], p[2])


def p_signal_enum(t):
    '''
    SIGNAL_ENUM = ISIGNAL COMMA ISIGNAL
    '''
    p[0] = ('signal_enum', p[1], p[0], p[2])


def p_question(t):
    '''
    QUESTION = SIGNAL_ENUM WITH PROB_ENUM
    '''
    p[0] = ('signal_enum', p[1], p[0], p[2])

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

# let prop := p1, p2, p3, p11, p21, p34

def p_interval(p):
    p[0] = ('interval', p[1], p[3])


def p_expression_search(p):
    p[0] = ('search', p[2], p[1], p[3])


def p_expression_comma(p):
    p[0] = ('group', p[2], p[1], p[3])


def p_expression_on(p):
    p[0] = ('on', p[2], p[1], p[3])


def p_expression_with(p):
    p[0] = ('with', p[2], p[1], p[3])


def p_expression(p):
    '''
    expression : term PLUS term
               | term MINUS term
    '''
    # p is a sequence that represents rule contents.
    #
    # expression : term PLUS term
    #   p[0]     : p[1] p[2] p[3]
    #
    p[0] = ('binop', p[2], p[1], p[3])


def p_expression_term(p):
    '''
    expression : term
    '''
    p[0] = p[1]


def p_term(p):
    '''
    term : factor TIMES factor
         | factor DIVIDE factor
    '''
    p[0] = ('binop', p[2], p[1], p[3])


def p_term_factor(p):
    '''
    term : factor
    '''
    p[0] = p[1]


def p_factor_number(p):
    '''
    factor : NUMBER
    '''
    p[0] = ('number', p[1])


def p_factor_name(p):
    '''
    factor : NAME
    '''
    p[0] = ('name', p[1])


def p_factor_unary(p):
    '''
    factor : NOT factor
    '''
    p[0] = ('unary', p[1], p[2])


def p_factor_grouped(p):
    '''
    factor : LPAREN expression RPAREN
    '''
    p[0] = ('grouped', p[2])


def p_error(p):
    print(f'Syntax error at {p.value!r}')

# Build the parser
parser = yacc()