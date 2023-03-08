from ply.yacc import yacc
import ParetoLib.CommandLanguage.Lexer as lexer

'''
In the intended language there are no precedence rules.
However, if necessary, they will be included in the "precedence" array.

precedence = (
)
'''

tokens = lexer.tokens

# dictionary of names
id_dict = {}


def p_param_list(t):
    '''
    PARAM_LIST = ID_LIST
    '''
    t[0] = ('PARAM_LIST', t[1])


def p_signal_list(t):
    '''
    SIGNAL_LIST = ID_LIST
    '''
    t[0] = ('SIGNAL_LIST', t[1])


def p_probsignal_list(t):
    '''
    PROBSIGNAL_LIST = ID_LIST
    '''
    t[0] = ('PROBSIGNAL_LIST', t[1])


def p_id_list(t):
    '''
    ID_LIST = ID | ID COMMA ID_LIST
    '''
    if len(t) == 1:
        # TODO: Insert ID in id_dict
        # ID is either a PARAM, a SIGNAL or a PROBSIGNAL
        if id_dict[t[1]] is not None:
            print("Error: ID already defined!")
        else:
            id_dict[t[1]] = "Insert type of ID"
        t[0] = ('ID_LIST', t[1])
    else:
        # recursive case
        t[0] = ('ID_LIST', t[1], t[2])


def p_def_param(t):
    '''
    PARAM_DEF = LET PARAM PARAM_LIST SEMICOLON
    '''
    #                PARAM_LIST
    t[0] = ('PARAM', t[3])


def p_def_signal(t):
    '''
    SIGNAL_DEF = LET SIGNAL SIGNAL_LIST SEMICOLON
    '''
    #                SIGNAL_LIST
    t[0] = ('SIGNAL', t[3])


# Probablemente haya algún fallo en este
def p_def_probsignal(t):
    '''
    PROBSIGNAL_DEF = LET PROB SIGNAL PROBSIGNAL_LIST SEMICOLON
    '''
    #                   PROBSIGNAL_LIST
    t[0] = ('PROBSIGNAL', t[4])


def p_eval(t):
    '''
    EVAL_EXPR = EVAL ID ON SIGNAL_LIST WITH INTVL_LIST |
           EVAL ID ON PROBSIGNAL_LIST WITH INTVL_LIST
    '''
    t[0] = ('EVAL_EXPR', t[3], t[2], t[4], t[6])


# TODO: parametric intervals
def p_intvl_list(t):
    '''
    INTVL_LIST = ID IN INTVL |
                 ID IN INTVL COMMA INTVL_LIST
    '''
    if len(t) == 3:
        t[0] = (t[2], t[1], t[3])
    elif len(t) == 5:
        t[0] = (t[2], t[1], t[3], t[4])


def p_eval_list(t):
    '''
    EVAL_LIST = EVAL_EXPR | EVAL_EXPR EVAL_LIST
    '''
    if len(t) == 1:
        t[0] = ('EVAL_LIST', t[1])
    elif len(t) == 2:
        t[0] = ('EVAL_LIST', t[1], t[2])


def p_intvl(t):
    '''
    INTVL = LBRACKET [NUMBER | ID ] COMMA [NUMBER | ID] RBRACKET
    '''
    t[0] = ('INTVL', t[1], t[2], t[3], t[4])


def p_spec_file(t):
    '''
    SPEC_FILE = [DEF_SIGNAL | DEF_PROBSIGNAL]?
	    [DEF_PARAM]? PROP_LIST EVAL_LIST
    '''
    counter = 0
    if t[0] == 'DEF_SIGNAL' or t[0] == 'DEF_PROBSIGNAL':
        counter += 1
    if t[counter] == 'DEF_PARAM':
        counter += 1
    if counter == 0:
        t[0] = ('SPEC_FILE', t[1], t[2])
    elif counter == 1:
        t[0] = ('SPEC_FILE', t[2], t[1], t[3])
    elif counter == 2:
        t[0] = ('SPEC_FILE', t[3], t[1], t[2], t[4])



def prop_list(t):
    '''
    PROP_LIST = PROP | PROP PROP_LIST
    '''
    t[0] = ('PROP_LIST', t[1])


def p_prop(t):
    '''
    PROP = ID := PHI | PSI
    '''
    #       TYPE    OP    ID    PHI/PSI
    t[0] = ('PROP', t[2], t[1], t[3])


def p_phi(t):
    '''
    PHI : ID | FUNC | NOT PHI | PROB PHI | PHI BIN_BOOL_OP PHI | F[INTVL]? PHI
        | G[INTVL]? PHI | PHI U[INTVL]? PHI | ON[INTVL] PSI | LPAR PHI RPAR
    '''
    t[0] = ('PHI', t[0])
    # Case of ID, FUNC
    if len(t) == 1:
        t[0] = ('PHI', t[1])
    # Case of NOT PHI, PROB PHI
    elif len(t) == 2:
        #       TYPE   OP    PHI
        t[0] = ('PHI', t[1], t[2])
    elif len(t) == 3:
        #       TYPE   OP    PHI   PHI
        t[0] = ('PHI', t[2], t[1], t[3])


def p_psi(t):
    '''
    PSI = MIN PHI |
          MAX PHI |
          INTEGRAL PHI |
          DER PHI
    '''
    #       TYPE   OP   PHI
    t[0] = ('PSI', t[1], t[2])


def p_func(t):
    '''
    FUNC = SIG BIN_COND SIG | SIG BIN_OP SIG
    '''
    #       TYPE    OP    SIG1  SIG2
    t[0] = ('FUNC', t[2], t[1], t[3])


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
    # Save the ID or NUMBER
    t[0] = t[1]


def p_constant_signal(t):
    '''
    CONSTANT_SIGNAL = NUMBER
    '''
    # Save number
    # t[0] = float(t[1])
    t[0] = t[1].value


# Build the parser
tmpdirname = "/tmp/"
parser = yacc.yacc(start='param', debugfile=tmpdirname + 'parser.out', write_tables=True)
