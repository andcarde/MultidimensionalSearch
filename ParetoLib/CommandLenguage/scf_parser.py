from ply.yacc import yacc
import ParetoLib.CommandLenguage.scf_lexer

tokens = scf_lexer.tokens

def p_let_word(t):
    '''
    r'let'
    '''
    t[0] = ('LET_WORD', t[0])
def p_param_word(t):
    '''
    r'param'
    '''
    t[0] = ('PARAM_WORD', t[0])

def p_signal_word(t):
    '''
    r'signal'
    '''
    t[0] = ('SIGNAL_WORD', t[0])
def p_probabilistic_word(t):
    '''
    r'probabilistic'
    '''
    t[0] = ('PROBABILISTIC_WORD', t[0])
def p_semicolon(t):
    '''
    r';'
    '''
    t[0] = ('SEMICOLON', t[0])
def p_param_list(t):
    '''
    PARAM_LIST = ID_LIST
    '''
    t[0] = ('PARAM_LIST', t[0])
def p_signal_list(t):
    '''
    SIGNAL_LIST = ID_LIST
    '''
    t[0] = ('SIGNAL_LIST', t[0])
def p_probsignal_list(t):
    '''
    PROBSIGNAL_LIST = ID_LIST
    '''
    t[0] = ('PROBSIGNAL_LIST', t[0])
def p_def_param(t):
    '''
    DEF_PARAM = LET_WORD + PARAM_WORD + PARAM_LIST + SEMICOLON
    '''
    t[0] = ('PARAM', t[0])
def p_def_signal(t):
    '''
    DEF_SIGNAL = LET_WORD + SIGNAL_WORD + SIGNAL_LIST + SEMICOLON
    '''
    t[0] = ('SIGNAL', t[0])
def p_def_probsignal(t):
    '''
    DEF_PROBSIGNAL = LET_WORD + PROBABILISTIC_WORD + SIGNAL_WORD + PROBSIGNAL_LIST + SEMICOLON
    '''
    t[0] = ('PROBSIGNAL', t[0])
def p_id_list(t):
    '''
    ID_LIST = ID | ID, ID_LIST
    '''
    t[0] = ('ID_LIST', t[0])
def p_id(t):
    '''
    r'[\w+][\d*]'
    '''
    t[0] = ('ID', t[0])
def p_eval(t):
    '''
    eval ID on SIGNAL_LIST with INTVL_LIST | eval ID with INTVL_LIST on SIGNAL_LIST |
        ID on PROBSIGNAL_LIST with INTVL_LIST | eval ID with INTVL_LIST on PROBSIGNAL_LIST |
    '''
    t[0] = ('EVAL', t[0])
def p_intvl_list(t):
    '''
    INTVL_LIST = ID in INTVL | ID in INTVL, INTVL_LIST
    '''
    t[0] = ('INTVL_LIST', t[0])
def p_intvl(t):
    '''
    INTVL = LBRACKET [NUMBER | ID ] COMMA [NUMBER | ID] RBRACKET
    '''
    t[0] = ('INTVL', t[0])
def p_comma(t):
    '''
    r','
    '''
    t[0] = ('COMMA', t[0])
def p_lbracket(t):
    '''
    r'['
    '''
    t[0] = ('LBRACKET', t[0])
def p_rbracket(t):
    '''
    r']'
    '''
    t[0] = ('RBRACKET', t[0])
def p_number(t):
    '''
    r'[-]?[\d+].[\d+]'
    '''
    t.value = float(t.value)
    t[0] = ('NUMBER', t[0])
# Write the matching regex in the docstring.
# Cuando hacemos t.value almacenamos información en dicho patrón
# El (int), castea el texto en un integer (tipo de Python)
def t_integer(t):
    '''
    r'[-]?\d+'
    '''
    t.value = int(t.value)
    return t
def p_spec_file(t):
    '''
    SPEC_FILE = [DEF_SIGNAL | DEF_PROBSIGNAL]?
	    [DEF_PARAM]? [PROP_LIST]+ [EVAL]+
    '''
    t[0] = ('SPEC_FILE', t[0])
def prop_list(t):
    '''
    PROP_LIST = PROP | PROP + PROP_LIST
    '''
    t[0] = ('PROP_LIST', t[0])
def p_prop(t):
    '''
    PROP = ID := [PHI | PSI] [SEMICOLON]?
    '''
    t[0] = ('PROP', t[0])
def p_phi(t):
    '''
    PHI : ID | FUNC | NOT PHI | PROB PHI | PHI BIN_BOOL_OP PHI | F[INTVL]? PHI
        | G[INTVL]? PHI | PHI U[INTVL]? PHI | ON[INTVL] PSI | LPAR PHI RPAR
    '''
    t[0] = ('PHI', t[0])
def p_on(t):
    '''
    r'on'
    '''
    t[0] = ('ON', t[0])
def p_lpar(t):
    '''
    r'('
    '''
    t[0] = ('LPAR', t[0])
def p_rpar(t):
    '''
    r')'
    '''
    t[0] = ('RPAR', t[0])
def p_psi(t):
    '''
    PSI = min PHI | max PHI | integral PHI | der PHI
    '''
    t[0] = ('PSI', t[0])
def p_func(t):
    '''
    FUNC = SIG BIN_COND SIG | SIG BIN_OP SIG
    '''
    t[0] = ('FUNC', t[0])
# Greater op, greater or equal op, less op, less or equal..
def p_bin_bool_op(t):
    '''
    BIN_BOOL_OP = GR_OP | GRE_OP, LE_OP, LEE_OP
    '''
    t[0] = ('BIN_BOOL_OP', t[0])
# Tengo que añadir la suma, resta, mul., div. (operaciones binarias)
def p_bin_cond(t):
    '''
    BIN_COND = ADD_OP | SUS_OP | MUL_OP | DIV_OP
    '''
    t[0] = ('BIN_COND', t[0])
# Tengo que añadir AND, OR, IMPLICATE
def p_bin_bool_op(t):
    '''
    BIN_COND = ...
    '''
    t[0] = ('BIN_COND', t[0])
def p_sig(t):
    '''
    SIG = ID | CONSTANT_SIGNAL
    '''
    t[0] = ('SIG', t[0])
def p_constant_signal(t):
    '''
    CONSTANT_SIGNAL = NUMBER
    '''
    t[0] = ('CONSTANT_SIGNAL', t[0])
def p_let_word(t):
    '''
    r'let'
    '''
    t[0] = ('LET_WORD', t[0])
def p_param_word(t):
    '''
    r'param'
    '''
    t[0] = ('PARAM_WORD', t[0])

def p_signal_word(t):
    '''
    r'signal'
    '''
    t[0] = ('SIGNAL_WORD', t[0])
def p_probabilistic_word(t):
    '''
    r'probabilistic'
    '''
    t[0] = ('PROBABILISTIC_WORD', t[0])
def p_semicolon(t):
    '''
    r';'
    '''
    t[0] = ('SEMICOLON', t[0])
def p_param_list(t):
    '''
    PARAM_LIST = ID_LIST
    '''
    t[0] = ('PARAM_LIST', t[0])
def p_signal_list(t):
    '''
    SIGNAL_LIST = ID_LIST
    '''
    t[0] = ('SIGNAL_LIST', t[0])
def p_probsignal_list(t):
    '''
    PROBSIGNAL_LIST = ID_LIST
    '''
    t[0] = ('PROBSIGNAL_LIST', t[0])
def p_def_param(t):
    '''
    DEF_PARAM = LET_WORD + PARAM_WORD + PARAM_LIST + SEMICOLON
    '''
    t[0] = ('PARAM', t[0])
def p_def_signal(t):
    '''
    DEF_SIGNAL = LET_WORD + SIGNAL_WORD + SIGNAL_LIST + SEMICOLON
    '''
    t[0] = ('SIGNAL', t[0])
def p_def_probsignal(t):
    '''
    DEF_PROBSIGNAL = LET_WORD + PROBABILISTIC_WORD + SIGNAL_WORD + PROBSIGNAL_LIST + SEMICOLON
    '''
    t[0] = ('PROBSIGNAL', t[0])
def p_id_list(t):
    '''
    ID_LIST = ID | ID, ID_LIST
    '''
    t[0] = ('ID_LIST', t[0])
def p_id(t):
    '''
    r'[\w+][\d*]'
    '''
    t[0] = ('ID', t[0])
def p_eval(t):
    '''
    eval ID on SIGNAL_LIST with INTVL_LIST | eval ID with INTVL_LIST on SIGNAL_LIST |
        ID on PROBSIGNAL_LIST with INTVL_LIST | eval ID with INTVL_LIST on PROBSIGNAL_LIST |
    '''
    t[0] = ('EVAL', t[0])
def p_intvl_list(t):
    '''
    INTVL_LIST = ID in INTVL | ID in INTVL, INTVL_LIST
    '''
    t[0] = ('INTVL_LIST', t[0])
def p_intvl(t):
    '''
    INTVL = LBRACKET [NUMBER | ID ] COMMA [NUMBER | ID] RBRACKET
    '''
    t[0] = ('INTVL', t[0])
def p_comma(t):
    '''
    r','
    '''
    t[0] = ('COMMA', t[0])
def p_lbracket(t):
    '''
    r'['
    '''
    t[0] = ('LBRACKET', t[0])
def p_rbracket(t):
    '''
    r']'
    '''
    t[0] = ('RBRACKET', t[0])
def p_number(t):
    '''
    r'[-]?[\d+].[\d+]'
    '''
    t.value = float(t.value)
    t[0] = ('NUMBER', t[0])
# Write the matching regex in the docstring.
# Cuando hacemos t.value almacenamos información en dicho patrón
# El (int), castea el texto en un integer (tipo de Python)
def t_integer(t):
    '''
    r'[-]?\d+'
    '''
    t.value = int(t.value)
    return t
def p_spec_file(t):
    '''
    SPEC_FILE = [DEF_SIGNAL | DEF_PROBSIGNAL]?
	    [DEF_PARAM]? [PROP_LIST]+ [EVAL]+
    '''
    t[0] = ('SPEC_FILE', t[0])
def prop_list(t):
    '''
    PROP_LIST = PROP | PROP + PROP_LIST
    '''
    t[0] = ('PROP_LIST', t[0])
def p_prop(t):
    '''
    PROP = ID := [PHI | PSI] [SEMICOLON]?
    '''
    t[0] = ('PROP', t[0])
def p_phi(t):
    '''
    PHI : ID | FUNC | NOT PHI | PROB PHI | PHI BIN_BOOL_OP PHI | F[INTVL]? PHI
        | G[INTVL]? PHI | PHI U[INTVL]? PHI | ON[INTVL] PSI | LPAR PHI RPAR
    '''
    t[0] = ('PHI', t[0])
def p_on(t):
    '''
    r'on'
    '''
    t[0] = ('ON', t[0])
def p_lpar(t):
    '''
    r'('
    '''
    t[0] = ('LPAR', t[0])
def p_rpar(t):
    '''
    r')'
    '''
    t[0] = ('RPAR', t[0])
def p_psi(t):
    '''
    PSI = min PHI | max PHI | integral PHI | der PHI
    '''
    t[0] = ('PSI', t[0])
def p_func(t):
    '''
    FUNC = SIG BIN_COND SIG | SIG BIN_OP SIG
    '''
    t[0] = ('FUNC', t[0])
# Greater op, greater or equal op, less op, less or equal..
def p_bin_bool_op(t):
    '''
    BIN_BOOL_OP = GR_OP | GRE_OP, LE_OP, LEE_OP
    '''
    t[0] = ('BIN_BOOL_OP', t[0])
# Tengo que añadir la suma, resta, mul., div. (operaciones binarias)
def p_bin_cond(t):
    '''
    BIN_COND = ADD_OP | SUS_OP | MUL_OP | DIV_OP
    '''
    t[0] = ('BIN_COND', t[0])
# Tengo que añadir AND, OR, IMPLICATE
def p_bin_bool_op(t):
    '''
    BIN_COND = ...
    '''
    t[0] = ('BIN_COND', t[0])
def p_sig(t):
    '''
    SIG = ID | CONSTANT_SIGNAL
    '''
    t[0] = ('SIG', t[0])
def p_constant_signal(t):
    '''
    CONSTANT_SIGNAL = NUMBER
    '''
    t[0] = ('CONSTANT_SIGNAL', t[0])

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


# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)

# let prop := t1, t2, t3, t11, t21, t34

def p_expression_comma(t):
    '''
    expression: expression, expression | factor
    '''
    t[0] = ('group', t[2], t[1], t[3])


def p_expression_on(t):
    '''
        expression: ON: term
    '''
    t[0] = ('on', t[2], t[1], t[3])


def p_expression_with(t):
    '''
    expression: WITH: term
    '''
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
