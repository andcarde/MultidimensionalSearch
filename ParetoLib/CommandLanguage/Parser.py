from ply.yacc import yacc
import os
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
    PARAM_LIST : ID_LIST
    '''
    t[0] = ('PARAM_LIST', t[1])
    # t[0] = ('PARAM_LIST', [p1, p2, p3])

def p_signal_list(t):
    '''
    SIGNAL_LIST : ID_LIST
    '''
    t[0] = ('SIGNAL_LIST', t[1])


def p_probsignal_list(t):
    '''
    PROBSIGNAL_LIST : ID_LIST
    '''
    t[0] = ('PROBSIGNAL_LIST', t[1])

def p_id_list(t):
    '''
    ID_LIST : ID
            | ID COMMA ID_LIST
    '''
    # ID is either a PARAM, a SIGNAL or a PROB_SIGNAL
    if id_dict[t[1]] is not None:
        print("Error: ID already defined!")
    else:
        # Insert type of ID
        id_dict[t[1]] = t[1]
        print("Inserted the ID: " + t[1] + '\n')
    if len(t) == 1:
        # Using Python lists here
        #       ID
        t[0] = [t[1]]
    else:
        # Concatenation of Python lists
        t[0] = [t[1]] + t[3]


def p_def_param(t):
    '''
    PARAM_DEF : LET PARAM PARAM_LIST SEMICOLON
    '''
    #                PARAM_LIST
    t[0] = ('PARAM', t[3])


def p_def_signal(t):
    '''
    SIGNAL_DEF : LET SIGNAL SIGNAL_LIST SEMICOLON
    '''
    #                SIGNAL_LIST
    t[0] = ('SIGNAL', t[3])


# Probablemente haya algún fallo en este
def p_def_probsignal(t):
    '''
    PROBSIGNAL_DEF : LET PROBABILISTIC SIGNAL PROBSIGNAL_LIST SEMICOLON
    '''
    #                   PROBSIGNAL_LIST
    t[0] = ('PROBSIGNAL', t[4])


def p_eval_list(t):
    '''
    EVAL_LIST : EVAL_EXPR
            | EVAL_EXPR EVAL_LIST
    '''
    if len(t) == 1:
        # Using Python lists here
        #       EVAL_EXPR
        t[0] = [t[1]]
    else:
        # Concatenation of Python lists
        t[0] = [t[1]] + t[2]


def p_eval_expr(t):
    '''
    EVAL_EXPR : EVAL ID ON SIGNAL_LIST WITH INTVL_LIST
                | EVAL ID ON PROBSIGNAL_LIST WITH INTVL_LIST
    '''
    # Check that len([WITH INTVL_LIST]*) == len(PARAM_LIST)
    #                    ON    ID    INTVL_LIST
    t[0] = ('EVAL_EXPR', t[3], t[2], t[6])


# TODO: define a rule for parametric intervals
# TODO A Generic INTVL is already defined -> Check in tutorship
def p_number_or_id(t):
    '''
    NUMBER_ID : NUMBER
                | ID
    '''
    None


def p_intvl(t):
    '''
    INTVL : LBRACK NUMBER_ID COMMA NUMBER_ID RBRACK
    '''
    # Check that t[2].value (NUMBER) or t[2].type (ID).
    # In case that it is ID, check that p1 == t[2], then p1 is param and p1 is defined in PARAM_LIST
    t[0] = ('INTVL', t[2], t[4])


def p_intvl_list(t):
    '''
    INTVL_LIST : ID IN INTVL
            | ID IN INTVL COMMA INTVL_LIST
    '''
    if len(t) == 3:
        t[0] = (t[2], t[1], t[3])
    elif len(t) == 5:
        t[0] = (t[2], t[1], t[3], t[4])


def p_def(t):
    '''
    DEF : PARAM_DEF
            | SIGNAL_DEF
            | PROBSIGNAL_DEF
    '''
    None

def p_definitions(t):
    '''
    DEFINITIONS : DEF
        | DEF DEFINITIONS
    '''
    if len(t) == 2:
        t[0] = (t[1], t[2])
        # t[1:] = (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
        # t[0] = (declaration for declaration in t[1:])
    elif len(t) == 1:
        t[0] = t[1]


def p_spec_file(t):
    '''
    SPEC_FILE : DEFINITIONS PROP_LIST EVAL_LIST
    '''
    assert len(t) == 3, "Missing definitions, property list or eval list"
    t[0] = ('SPEC_FILE', ('DEF', t[1]), ('PROP_LIST', t[2]), ('EVAL_LIST', t[3]))


def p_prop_list(t):
    '''
    PROP_LIST : PROP
            | PROP PROP_LIST
    '''
    if len(t) == 1:
        # Using Python lists here
        #       PROP
        t[0] = [t[1]]
    else:
        #  Concatenation of property lists
        #       PROP    PROP_LIST
        t[0] = [t[1]] + t[2]


def p_prop(t):
    '''
    PROP : ID ASSIGNMENT PHI
            | ID ASSIGNMENT PSI
    '''
    #       TYPE    ID    PHI/PSI
    t[0] = ('PROP', t[1], t[3])


def p_phi(t):
    '''
    PHI : ID
        | FUNC
        | NOT PHI
        | PROB PHI
        | PHI BIN_BOOL_OP PHI
        | F INTVL PHI
        | G INTVL PHI
        | PHI UNTIL INTVL PHI
        | ON INTVL PSI
        | LPAREN PHI RPAREN
    '''
    # Case of ID, FUNC
    if len(t) == 1:
        t[0] = ('PHI', t[1])
    # Case of NOT PHI, PROB PHI, PHI
    elif len(t) == 2:
        #       TYPE   OP    PHI
        t[0] = ('PHI', t[1], t[2])
    elif len(t) == 3:
        if t[2] == 'BIN_BOOL_OP':
            #       TYPE   OP    PHI   PHI
            t[0] = ('PHI', t[2], t[1], t[3])
        elif t[1] == 'LPAR' and t[3] == 'RPAR':
            #      PHI
            t[0] = t[2]
    elif len(t) == 5:
        #       TYPE   ON    INTVL  PSI
        #       TYPE   F     INTVL  PHI
        #       TYPE   G     INTVL  PHI
        t[0] = ('PHI', t[1], t[3], t[5])
    elif len(t) == 6:
        #       TYPE   U     INTVL PHI   PHI
        t[0] = ('PHI', t[2], t[4], t[1], t[6])


def p_psi(t):
    '''
    PSI : MIN PHI
            | MAX PHI
            | INT PHI
            | DER PHI
    '''
    #       TYPE   OP   PHI
    t[0] = ('PSI', t[1], t[2])


def p_func(t):
    '''
    FUNC : SIG BIN_COND SIG
            | SIG BIN_OP SIG
    '''
    #       TYPE    OP    SIG1  SIG2
    t[0] = ('FUNC', t[2], t[1], t[3])


def p_bin_bool_op(t):
    '''
    BIN_BOOL_OP : PHI AND PHI
            | PHI OR PHI
            | PHI IMPLY PHI
    '''
    #       OP    PHI1  PHI2
    t[0] = (t[2], t[1], t[3])


def p_bin_cond(t):
    '''
    BIN_COND : SIG LEQ SIG
            | SIG LESS SIG
            | SIG GEQ SIG
            | SIG GREATER SIG
            | SIG NEQ SIG
    '''
    #       OP    SIG1  SIG2
    t[0] = (t[2], t[1], t[3])


def p_bin_arith_op(t):
    '''
    BIN_OP : SIG PLUS SIG
            | SIG MINUS SIG
            | SIG TIMES SIG
            | SIG DIVIDE SIG
    '''
    #       OP    SIG1  SIG2
    t[0] = (t[2], t[1], t[3])


def p_sig(t):
    '''
    SIG : ID
            | CONSTANT_SIGNAL
    '''
    # Save the ID or NUMBER
    t[0] = t[1]


def p_constant_signal(t):
    '''
    CONSTANT_SIGNAL : NUMBER
    '''
    # Save number
    # t[0] = float(t[1])
    t[0] = t[1].value


# Build the parser
current_dir = os.path.dirname(__file__)
tmpdirname = current_dir + "/tmp/"
parser = yacc(start='SPEC_FILE', debugfile=tmpdirname + 'parser.out', write_tables=True)
