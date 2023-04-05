from ply.yacc import yacc
import os
import ParetoLib.CommandLanguage.Lexer as Lexer

'''
In the intended language there are no precedence rules.
However, if necessary, they will be included in the "precedence" array.

precedence = (
)
'''

debug = True
tokens = Lexer.tokens

# dictionary of names
id_dict = dict()


def p_param_list(t):
    '''
    PARAM_LIST : ID_LIST
    '''
    # Ej: t[0] = ('PARAM_LIST', [p1, p2, p3])
    t[0] = ('PARAM_LIST', t[1])


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
    if len(t) == 2:
        # Using Python lists here
        #       ID
        t[0] = [t[1]]
    else:
        # Concatenation of Python lists
        print("Generating {0} with length {1}".format([i for i in t], len(t)))
        t[0] = [t[1]] + t[3]


def p_def_param(t):
    '''
    PARAM_DEF : LET PARAM PARAM_LIST SEMICOLON
    '''
    #      PARAM_LIST
    t[0] = t[3]


def p_def_signal(t):
    '''
    SIGNAL_DEF : LET SIGNAL SIGNAL_LIST SEMICOLON
    '''
    #      SIGNAL_LIST
    t[0] = t[3]



def p_def_probsignal(t):
    '''
    PROBSIGNAL_DEF : LET PROBABILISTIC SIGNAL PROBSIGNAL_LIST SEMICOLON
    '''
    #      PROBSIGNAL_LIST
    t[0] = t[4]


def p_eval_list(t):
    '''
    EVAL_LIST : EVAL_EXPR
            | EVAL_EXPR EVAL_LIST
    '''
    if len(t) == 2:
        # Using Python lists here
        #       EVAL_EXPR
        t[0] = [t[1]]
    else:
        # Concatenation of Python lists
        t[0] = [t[1]] + t[2]


def p_eval_expr(t):
    '''
    EVAL_EXPR : EVAL ID ON ID_LIST WITH INTVL_LIST
    '''
    # Check that len([WITH INTVL_LIST]*) == len(PARAM_LIST)
    #                 ID-prop  signalList  INTVL_LIST
    t[0] = ('EVAL_EXPR', t[2], t[4], t[6])
    if debug:
        print('EVAL_EXPR: {0} \n'.format([i for i in t[0]]))


def p_number_or_id(t):
    '''
    NUMBER_ID : NUMBER
                | ID
    '''
    t[0] = t[1]


def p_intvl(t):
    '''
    INTVL : LBRACK NUMBER_ID COMMA NUMBER_ID RBRACK
    '''
    # Check that t[2].value (NUMBER) or t[2].type (ID).
    # In case that it is ID, check that p1 == t[2], then p1 is param and p1 is defined in PARAM_LIST
    t[0] = ('INTVL', t[2], t[4])
    if debug:
        print("INTVL: {0} \n".format([i for i in t[0]]))


def p_intvl_list(t):
    '''
    INTVL_LIST : ID IN INTVL
            | ID IN INTVL COMMA INTVL_LIST
    '''
    if len(t) == 4:
        # INTVL_LIST : ID, INTVL
        t[0] = [(t[1], t[3])]
    elif len(t) == 6:
        # INTVL_LIST : ID, INTVL, INTVL_LIST
        t[0] = [(t[1], t[3])] + t[5]
    if debug:
        print('Detected INTVL_LIST: {0} \n'.format([i for i in t[0]]))


def p_def(t):
    '''
    DEF : PARAM_DEF
            | SIGNAL_DEF
            | PROBSIGNAL_DEF
    '''
    # DEF = PARAM_DEF | SIGNAL_DEF | PROBSIGNAL_DEF
    t[0] = t[1]
    for i in t[0][1]:
        if i in id_dict.keys():
            print("Error: ID already defined!")
        else:
            # Insert type of ID
            id_dict[i] = i
            print("Inserted the ID: " + i)


def p_definitions(t):
    '''
    DEFINITIONS : DEF
        | DEF DEFINITIONS
    '''
    if len(t) == 3:
        t[0] = [t[1]] + t[2]
        # t[1:] = (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
        # t[0] = (declaration for declaration in t[1:])
    elif len(t) == 2:
        t[0] = [t[1]]
    if debug:
        print('Definitions Rule -> t: {0}\n'.format([i for i in t[0]]))



def p_spec_file(t):
    '''
    SPEC_FILE : DEFINITIONS PROP_LIST EVAL_LIST
    '''
    assert len(t) == 4, "Missing definitions, property list or eval list"
    t[0] = ('SPEC_FILE', ('DEFINITIONS', t[1]), ('PROP_LIST', t[2]), ('EVAL_LIST', t[3]))
    if debug:
        print("SPEC_FILE: {0} \n".format([i for i in t[0]]))


def p_prop_list(t):
    '''
    PROP_LIST : PROP
            | PROP PROP_LIST
    '''
    if len(t) == 2:
        # Using Python lists here
        #       PROP
        t[0] = [t[1]]
    else:
        #  Concatenation of property lists
        #       PROP    PROP_LIST
        t[0] = [t[1]] + t[2]


# TODO Debo asegurarme que prob2, solo se evalue si ha sido definida
def p_prop(t):
    '''
    PROP : ID ASSIGNMENT PHI SEMICOLON
            | ID ASSIGNMENT PSI SEMICOLON
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
        | PHI UNTIL PHI
    '''
    # Case of ID, FUNC
    if len(t) == 2:
        t[0] = ('PHI', t[1])
    # Case of NOT PHI, PROB PHI
    elif len(t) == 3:
        #       TYPE   OP    PHI
        t[0] = ('PHI', t[1], t[2])
    elif len(t) == 4:
        if t[2] == 'BIN_BOOL_OP':
            #       TYPE   OP    PHI   PHI
            t[0] = ('PHI', t[2], t[1], t[3])
        elif t[2] == 'PHI':
            #      PHI
            t[0] = t[2]
        elif t[2] == 'UNTIL':
            #       TYPE   UNTIL PHI   PHI
            t[0] = ('PHI', t[2], t[1], t[3])
        # Case of 'F INTVL PHI', 'G INTVL PHI' and 'ON INTVL PSI', elif t[2] == 'INTVL'
        else:
            t[0] = ('PHI', t[1], t[2], t[3])
    elif len(t) == 5:
        #       TYPE   U     INTVL PHI   PHI
        t[0] = ('PHI', t[2], t[4], t[1], t[6])
    if debug:
        print("PHI: {0} \n".format([i for i in t[0]]))


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
            | PHI BIN_OP PHI
    '''
    #       TYPE    OP    SIG/PHI1  SIG/PHI2
    t[0] = ('FUNC', t[2], t[1], t[3])
    if debug:
        print("FUNC: {0} \n".format([i for i in t[0]]))


def p_bin_bool_op(t):
    '''
    BIN_BOOL_OP : AND
            | OR
            | IMPLY
    '''
    #       OP
    t[0] = t[1]


def p_bin_cond(t):
    '''
    BIN_COND : LEQ
            | LESS
            | GEQ
            | GREATER
            | NEQ
    '''
    #       OP
    t[0] = t[1]


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
    if debug:
        print('SIG: ' + str(t[0]))


def p_constant_signal(t):
    '''
    CONSTANT_SIGNAL : NUMBER
    '''
    # Save number
    # t[0] = float(t[1])
    t[0] = t[1]


# Build the parser
current_dir = os.path.dirname(__file__)
tmpdirname = current_dir + "/tmp/"
parser = yacc(start='SPEC_FILE', debugfile=tmpdirname + 'parser.out', write_tables=True)
