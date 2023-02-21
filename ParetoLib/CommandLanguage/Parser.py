from ply.yacc import yacc
import ParetoLib.CommandLanguage.Lexer as lexer

tokens = lexer.tokens

def p_param_list(t):
    '''
    PARAM_LIST = ID_LIST
    '''
    t[0] = ('PARAM_LIST', t[1])

def p_id_list(t):
    '''
    ID_LIST = ID | ID, ID_LIST
    '''
    if len(t) == 1:
        t[0] = ('ID_LIST', t[1])
    else:
        # blabla
        t[0] = ('ID_LIST', t[1], t[2])

def p_signal_list(t):
    '''
    SIGNAL_LIST = ID_LIST
    '''
    t[0] = ('SIGNAL_LIST', t[1])


def p_probsignal_list(t):
    '''
    PROBSIGNAL_LIST = ID_LIST
    '''
    t[0] = ('PROBSIGNAL_LIST', t[0])


def p_def_param(t):
    '''
    PARAM = LET_WORD PARAM_WORD PARAM_LIST SEMICOLON
    '''
    t[0] = ('PARAM', t[1], t[2], ...)


def p_def_signal(t):
    '''
    SIGNAL = LET_WORD SIGNAL_WORD SIGNAL_LIST SEMICOLON
    '''
    t[0] = ('SIGNAL', t[0])


def p_def_probsignal(t):
    '''
    PROBSIGNAL = LET_WORD + PROBABILISTIC_WORD + SIGNAL_WORD + PROBSIGNAL_LIST + SEMICOLON
    '''
    t[0] = ('PROBSIGNAL', t[0])


def p_eval(t):
    '''
    EVAL = eval ID ON SIGNAL_LIST WITH INTVL_LIST |
           eval ID ON PROBSIGNAL_LIST WITH INTVL_LIST |
           eval ID WITH INTVL_LIST ON SIGNAL_LIST |
           eval ID WITH INTVL_LIST ON PROBSIGNAL_LIST
    '''
    if t[3] == tokens.ON:
        t[0] = ('EVAL', t[0])


def p_intvl_list(t):
    '''
    INTVL_LIST = ID IN INTVL |
                 ID IN INTVL COMMA INTVL_LIST
    '''
    t[0] = ('INTVL_LIST', t[0])


def p_intvl(t):
    '''
    INTVL = LBRACKET [NUMBER | ID ] COMMA [NUMBER | ID] RBRACKET
    '''
    t[0] = ('INTVL', t[0])


def p_spec_file(t):
    '''
    SPEC_FILE = [DEF_SIGNAL | DEF_PROBSIGNAL]?
	    [DEF_PARAM]? PROP_LIST [EVAL]+
    '''
    t[0] = ('SPEC_FILE', t[0])


def prop_list(t):
    '''
    PROP_LIST = PROP | PROP PROP_LIST
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


def p_psi(t):
    '''
    PSI = [MIN | MAX | integral | der] PHI
    '''
    t[0] = ('PSI', t[0])


def p_func(t):
    '''
    FUNC = SIG BIN_COND SIG | SIG BIN_OP SIG
    '''
    t[0] = ('FUNC', t[0])


def p_bin_bool_op(t):
    '''
    BIN_BOOL_OP = PHI AND PHI |
                  PHI OR PHI |
                  PHI IMPLY PHI
    '''
    #       OP    PHI1  PHI2
    t[0] = (t[2], t[1], t[3])


def p_bin_cond(t):
    '''
    BIN_COND = SIG LEQ SIG |
               SIG LESS SIG |
               SIG GEQ SIG |
               SIG GREATER SIG
    '''
    #       OP    SIG1  SIG2
    t[0] = (t[2], t[1], t[3])


def p_bin_arith_op(t):
    '''
    BIN_OP = SIG PLUS SIG |
               SIG MINUS SIG |
               SIG TIMES SIG |
               SIG DIVIDE SIG
    '''
    #       OP    SIG1  SIG2
    t[0] = (t[2], t[1], t[3])

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
    t[0] = ('PROB', t[0])



# Ignored token with an action associated with it
def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


# Error handler for illegal characters
def t_error(t):
    print(f'Illegal character {t.value[0]!r}')
    t.lexer.skip(1)


# Build the parser
tmpdirname = "/tmp/"
parser = yacc.yacc(start='param', debugfile=tmpdirname + 'parser.out', write_tables=True)
