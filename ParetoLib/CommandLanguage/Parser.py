import os
from ply.yacc import yacc
import ParetoLib.CommandLanguage.Lexer as Lexer

'''
In the intended language there are no precedence rules.
However, if necessary, they will be included in the "precedence" array.

precedence = (
    ...
)
'''

# Debug mode flag
debug = False

# Variable needed for ply.yacc
tokens = Lexer.tokens


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
        t[0] = [t[1]] + t[3]
        # Concatenation of Python lists
        print("Generating {0} with length {1}".format([i for i in t[0]], len(t)))


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
    EVAL_EXPR : EVAL ID WITH EVAL_PARAM_LIST SEMICOLON
    '''
    # Check that len([WITH INTVL_LIST]*) == len(PARAM_LIST)
    #                 ID-prop  signalList  INTVL_LIST
    t[0] = ('EVAL_EXPR', t[2], t[4])
    if debug:
        print('[Parser.py] [p_eval_expr(..)]')
        print('EVAL_EXPR: {0} \n'.format([i for i in t[0]]))


def p_eval_param_list(t):
    '''
    EVAL_PARAM_LIST : ID IN INTVL
            | ID IN INTVL COMMA EVAL_PARAM_LIST
    '''
    if len(t) == 4:
        # (ID, INTVL)
        t[0] = [('restriction', ('ID', t[1]), t[3])]
    else:
        # ((ID, INTVL), *EVAL_PARAM_LIST) where * is a pointer
        t[0] = [('restriction', ('ID', t[1]), t[3])]
        t[0].extend(t[5][0:])


def p_number_or_id(t):
    '''
    NUMBER_OR_ID : NUMBER
                | ID
    '''
    t[0] = t[1]


def p_intvl(t):
    '''
    INTVL : LBRACK NUMBER_OR_ID COMMA NUMBER_OR_ID RBRACK
    '''
    # Check that t[2].value (NUMBER) or t[2].type (ID).
    # In case that it is ID, check that p1 == t[2], then p1 is param and p1 is defined in PARAM_LIST
    t[0] = ('INTVL', t[2], t[4])
    if debug:
        print("INTVL: {0} \n".format([i for i in t[0]]))


def p_def(t):
    '''
    DEF : PARAM_DEF
            | SIGNAL_DEF
            | PROBSIGNAL_DEF
    '''
    # DEF = PARAM_DEF | SIGNAL_DEF | PROBSIGNAL_DEF
    t[0] = t[1]


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


def p_prop(t):
    '''
    PROP : ID ASSIGNMENT PHI SEMICOLON
            | ID ASSIGNMENT PSI SEMICOLON
    '''
    #       TYPE    ID    PHI/PSI
    t[0] = ['PROP', t[1], t[3]]


def p_phi(t):
    '''
    PHI : FUNC
        | NOT PHI
        | PROB PHI
        | PHI BIN_BOOL_OP PHI
        | F INTVL PHI
        | F PHI
        | G INTVL PHI
        | G PHI
        | PHI UNTIL INTVL PHI
        | ON INTVL PSI
        | LPAREN PHI RPAREN
        | PHI UNTIL PHI
    '''
    if len(t) == 2:
        t[0] = (t[1][0], t[1][1])
        print('DEBUG -- Parser.p_phi -- {0} (function)'.format(t[1][0]))
        print('DEBUG -- Parser.p_phi -- {0} (definition)'.format(t[1][1]))
    elif t[1] == 'G':
        if len(t) == 3:
            t[0] = ('global', t[2])
        else:
            t[0] = ('global-interval', (t[2], t[3]))
    elif t[1] == 'F':
        if len(t) == 3:
            t[0] = ('future', t[2])
        else:
            t[0] = ('future-interval', (t[2], t[3]))
    elif t[1] == 'on':
        t[0] = ('on', (t[2], t[3][1]))
    elif t[1] == 'not':
        t[0] = ('not', t[2])
    elif len(t) > 2 and t[2] == 'U':
        if len(t) == 4:
            t[0] = ('until', (t[1], t[3]))
        else:
            t[0] = ('until-interval', (t[3], t[1], t[4]))
    elif t[1] == '(':
        # t[2]: phi
        t[0] = t[2]
    elif len(t) == 3 and t[1] == 'PROB':
        t[0] = ('prob', t[2])
    elif len(t) == 4 and t[2][0] == 'binary_boolean_operation':
        t[0] = ('function', (t[2][1], t[1], t[3]))
    else:
        for i in range(0, len(t)):
            print(t[i])
        print('ERROR: No type detected (Parser.p_phi)')

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
    t[0] = ('PSI', (t[1], t[2]))


def p_func(t):
    '''
    FUNC : SIG
            | LPAREN FUNC RPAREN
            | FUNC BIN_COND FUNC
            | FUNC BIN_OP FUNC
    '''
    if len(t) == 2:
        t[0] = t[1]
        print('DEBUG -- Parser.p_func -- {0}'.format(t[1]))
    elif t[1] == '(':
        t[0] = t[2]
    else:
        #       TYPE    OP    SIG  SIG
        t[0] = ('function', (t[2], t[1], t[3]))


def p_bin_bool_op(t):
    '''
    BIN_BOOL_OP : AND
            | OR
            | IMPLY
    '''
    #       OP
    t[0] = ('binary_boolean_operation', t[1])


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
    BIN_OP : PLUS
            | MINUS
            | TIMES
            | DIVIDE
    '''
    #       OP    SIG1  SIG2
    t[0] = t[1]


def p_sig(t):
    '''
    SIG : ID
            | CONSTANT_SIGNAL
    '''
    if not isinstance(t[1], tuple):
        t[0] = ('variable_signal', t[1])
        print('DEBUG -- Parser.p_sig -- {0}'.format(t[1]))
    else:
        t[0] = t[1]


def p_constant_signal(t):
    '''
    CONSTANT_SIGNAL : NUMBER
    '''
    t[0] = ('constant_signal', t[1])


# Build the parser
current_dir = os.path.dirname(__file__)
tmp_route_name = os.path.join(current_dir, '/tmp/', 'parser.out')
parser = yacc(start='SPEC_FILE', debugfile=tmp_route_name, write_tables=True)
