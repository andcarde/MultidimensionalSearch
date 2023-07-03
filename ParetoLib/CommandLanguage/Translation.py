from ParetoLib.CommandLanguage.Parser import parser, id_dict

'''
· Sintaxis del lenguaje STLe1
<BOOLEAN> ::= false | true
<FLOAT_NUMBER> ::= \d*\.?\d+
<NUMBER> ::= <FLOAT_NUMBER> | inf | -inf
<INTERVAL> ::= ( <NUMBER> <NUMBER> )
<VARIABLE> ::= x<INTEGER>
<VALUE> ::= <NUMBER> | <VARIABLE>
<AGGREGATE> ::= ( Min <FORMULA> ) | ( Max <FORMULA> )
<ARITHMETIC> ::= min | max | + | - | / | * | abs
<COMPARATION> ::= < | <= | > | >=
<LOGICAL_OP> ::= and |or | not | ->
<TERNARY> ::= ite <FUNCTION> <VALUE> <VALUE>
<FUNCTION> ::= <ARITHMETIC> | <COMPARATION> | <LOGICAL_OP> | <BOOLEAN>
<FORMULA> ::= <VARIABLE> |
              <NUMBER> |
              <BOOLEAN> |
              ( <FUNCTION> <FORMULA>* ) |
              ( F <INTERVAL> <FORMULA> ) |
              ( G <INTERVAL> <FORMULA> ) |
              ( StlUntil <INTERVAL> <FORMULA> <FORMULA> ) |
              ( On <INTERVAL> <AGGREGATE> ) |
              ( Until <INTERVAL> <NUMBER> <AGGREGATE> <FORMULA> ) |
              ( Until <INTERVAL> <NUMBER> ( Get <FORMULA> ) <FORMULA> ) |
              ( Lookup <NUMBER> <NUMBER> <FORMULA> )
^<FORMULA>
              
· Sintaxis del lenguaje STLe2 aplicada
<PARAM_LIST> ::= <ID_LIST>
<SIGNAL_LIST> ::= <ID_LIST>
<PROBSIGNAL_LIST> ::= <ID_LIST>
<ID_LIST> ::= ID | ID COMMA ID_LIST
<PARAM_DEF> ::= <LET> <PARAM> <PARAM_LIST> <SEMICOLON>
<SIGNAL_DEF> ::= <LET> <SIGNAL> <SIGNAL_LIST> <SEMICOLON>
<PROBSIGNAL_DEF> : <LET> <PROBABILISTIC> <SIGNAL> <PROBSIGNAL_LIST> <SEMICOLON>
<EVAL_LIST> ::= <EVAL_EXPR> [<EVAL_LIST>]?
<EVAL_EXPR> ::= <EVAL> <ID> <ON> <ID_LIST> <WITH> <INTVL_LIST>
<NUMBER_ID> ::= <NUMBER> | <ID>
<INTVL> ::= <LBRACK> <NUMBER_ID> <COMMA> <NUMBER_ID> <RBRACK>
<INTVL_LIST> ::= <ID> <IN> <INTVL> [<COMMA> <INTVL_LIST>]?
<DEF> ::= <PARAM_DEF> | <SIGNAL_DEF> | <PROBSIGNAL_DEF>
<DEFINITIONS> ::= <DEF> | <DEF> <DEFINITIONS>
<SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>
<PROP_LIST> : <PROP> | [<PROP_LIST>]?
<PROP> : <ID> <ASSIGNMENT> <PHI> <SEMICOLON> | <ID> <ASSIGNMENT> <PSI> <SEMICOLON>
<PHI> : <SIG>
        | <FUNC>
        | <NOT> <PHI>
        | <PROB> <PHI>
        | <PHI> <BIN_BOOL_OP> <PHI>
        | F <INTVL> <PHI>
        | F <PHI>
        | G <INTVL> <PHI>
        | G <PHI>
        | <PHI> <UNTIL> <INTVL> <PHI>
        | <ON> <INTVL> <PSI>
        | <LPAREN> <PHI> <RPAREN>
        | <PHI> <UNTIL> <PHI>
<PSI> : <MIN> <PHI>
            | <MAX> <PHI>
            | <INT> <PHI>
            | <DER> <PHI>
<FUNC> : <SIG> <BIN_COND> <SIG>
<BIN_BOOL_OP> : <AND>
            | <OR>
            | <IMPLY>
<BIN_COND> : <LEQ>
            | <LESS>
            | <GEQ>
            | <GREATER>
            | <NEQ>
<BIN_OP> : <PLUS>
            | <MINUS>
            | <TIMES>
            | <DIVIDE>
<SIG> : <ID>
            | <CONSTANT_SIGNAL>
            | <SIG> <BIN_OP> <SIG>
            | <LPAREN> <SIG> <RPAREN>
<CONSTANT_SIGNAL> : <NUMBER>
'''

'''
'''

'''
Funciones
- Se traducirá el lenguaje CPN a STLE
- Encargarse de que sale una variable una solo vez
- Asegurarse de que tengan sentido las expresiones
    - Si asignamos un valor Tipo1 (ej: Entero) un valor Tipo2 (ej: Boolean) será incorrecto.
- Contruir la string en lenguage STL
'''

'''
Input: AST
Output: 
    - STL file
    - Param file
    - (optionally) CSV file (e.g, signal)
'''

# Diccionario de preposiciones atomicas
ap = {}

# To count how many variables has been declared
global variable_counter
variable_counter = 0

# To map variable names into variable 'x<NUMBER' format
global dic

def translate_interval(interval):
    if len(interval) == 3:
        return f"({interval[1]} {interval[2]})"
    else:
        return f"({interval[1]} {interval[2]} {interval[3]})"

def translate_operator(op):
    operators = {
        "AND": "and",
        "OR": "or",
        "NOT": "not",
        "IMPLY": "->",
        "LEQ": "<=",
        "LESS": "<",
        "GEQ": ">=",
        "GREATER": ">",
        "NEQ": "!=",
        "PLUS": "+",
        "MINUS": "-",
        "TIMES": "*",
        "DIVIDE": "/",
    }
    return operators[op]

def translate_function(func):
    return f"({func[0]} {' '.join(map(translate, func[1:]))})"

def translate_signal(sig):
    if len(sig) == 1:
        return sig[0]
    else:
        return f"({translate_operator(sig[1])} {translate_signal(sig[0])} {translate_signal(sig[2])})"

def translate(tree):
    if isinstance(tree, list):
        if tree[0] in ["AND", "OR", "NOT", "IMPLY", "LEQ", "LESS", "GEQ", "GREATER", "NEQ", "PLUS", "MINUS", "TIMES", "DIVIDE"]:
            return translate_function(tree)
        elif tree[0] == "ID":
            return tree[1]
        elif tree[0] == "NUMBER":
            return str(tree[1])
        elif tree[0] == "INTVL":
            return translate_interval(tree)
        elif tree[0] in ["SIG", "CONSTANT_SIGNAL"]:
            return translate_signal(tree)
        else:
            return ' '.join(map(translate, tree))
    else:
        return str(tree)

import os

def createParams(params):
    # Crear la carpeta temp si no existe
    if not os.path.exists('temp'):
        os.makedirs('temp')

    # Crear el archivo param.txt en la carpeta temp
    with open('temp/param.txt', 'w') as f:
        for param in params:
            # Escribir cada parámetro en una línea diferente
            f.write(f"{param}\n")


def translate(stle2_array):
    if stle2_array[0] == "PARAM_LIST":
        pass
    elif stle2_array[0] == "SIGNAL_LIST":
        pass
    elif stle2_array[0] == "PROBSIGNAL_LIST":
        pass
    elif stle2_array[0] == "ID_LIST":
        pass
    elif stle2_array[0] == "ID":
        pass
    elif stle2_array[0] == "PARAM_DEF":
        pass
    elif stle2_array[0] == "PARAM_LIST":
        createParams(stle2_array[1])
        return ""
    elif stle2_array[0] == "SIGNAL_DEF":
        pass
    elif stle2_array[0] == "PROBSIGNAL_LIST":
        pass
    elif stle2_array[0] == "EVAL_LIST":
        pass
    elif stle2_array[0] == "EVAL_EXPR":
        pass
    elif stle2_array[0] == "INTVL_LIST":
        pass
    elif stle2_array[0] == "NUMBER_ID":
        pass
    elif stle2_array[0] == "INTVL":
        pass
    elif stle2_array[0] == "DEF":
        for elem in stle2_array[1]:
            return " ".join(map(translate, elem))
    elif stle2_array[0] == "PROBSIGNAL_DEF":
        pass
    elif stle2_array[0] == "DEFINITIONS":
        for elem in stle2_array[1]:
            return " ".join(map(translate, elem))
    elif stle2_array[0] == "SPEC_FILE":
        for elem in stle2_array[1]:
            return " ".join(map(translate, elem))
    elif stle2_array[0] == "PROP_LIST":
        pass
    elif stle2_array[0] == "PROP":
        pass
    elif stle2_array[0] == "PHI":
        pass
    elif stle2_array[0] == "PSI":
        pass
    elif stle2_array[0] == "SIG":
        pass
    elif stle2_array[0] == "FUNC":
        pass
    elif stle2_array[0] == "NOT":
        pass
    elif stle2_array[0] == "PROB":
        pass
    elif stle2_array[0] == "BIN_BOOL_OP":
        pass
    elif stle2_array[0] == "MIN":
        pass
    elif stle2_array[0] == "MAX":
        pass
    elif stle2_array[0] == "INT":
        pass
    elif stle2_array[0] == "DER":
        pass
    elif stle2_array[0] == "BIN_COND":
        pass
    elif stle2_array[0] == "AND":
        pass
    elif stle2_array[0] == "OR":
        pass
    elif stle2_array[0] == "IMPLY":
        pass
    elif stle2_array[0] == "LEQ":
        pass
    elif stle2_array[0] == "LESS":
        pass
    elif stle2_array[0] == "GEQ":
        pass
    elif stle2_array[0] == "GREATER":
        pass
    elif stle2_array[0] == "NEQ":
        pass
    elif stle2_array[0] == "BIN_OP":
        pass
    elif stle2_array[0] == "PLUS":
        pass
    elif stle2_array[0] == "MINUS":
        pass
    elif stle2_array[0] == "TIMES":
        pass
    elif stle2_array[0] == "DIVIDE":
        pass
    elif stle2_array[0] == "":
        pass
    elif stle2_array[0] == "":
        pass
    elif stle2_array[0] == "":
        pass

    else:
        pass
    if stle2_array[0] == "":
        for elem in stle2_array:
            if elem[0] == "INTVL":
                return elem[1]
            else:
                return 0


# STLCommand
def translate2(cpn_tree):
    assert cpn_tree[0] == 'SPEC_FILE'
    # DEFINITIONS
    # cpn_tree[1] == ('DEF', t[1])
    _, defs = cpn_tree[1]
    translate_defs(defs)

    # PROP_LIST
    # cpn_tree[2] == ('PROP_LIST', t[2])
    _, prop_list = cpn_tree[2]
    translate_prop_list(prop_list)

    # EVAL_LIST
    # cpn_tree[3] == ('EVAL_LIST', t[3])
    _, eval_list = cpn_tree[3]
    translate_eval_list(eval_list)


def translate_defs(defs):
    # defs == (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
    for (keyword, signal_or_param_list) in defs:
        if keyword == 'SIGNAL_LIST':
            None
        elif keyword == 'PROBSIGNAL_LIST':
            None
        elif keyword == 'PARAM_LIST':
            # Save 'signal_or_param_list' into temporary file and save record
            param_list = ["p1", "p2"]
            return param_list

wrappers = [
    'BIN_BOOL_OP',
    'PROBSIGNAL_LIST',
    'SIGNAL_LIST',
    'PARAM_LIST',
    'DEFINITIONS',
    'PROP_LIST',
    'EVAL_LIST'
]

indicators = [
    'PSI',
    'FUNC',
    'SPEC_FILE',
    'INTVL',
    'EVAL_EXPR',
    'PHI',
]


def remove_wrappers(tree):
    if isinstance(tree, (list, tuple)):
        for indicator in indicators:
            if tree[0] == indicator:
                tree.pop(0)
                break
        for wrapper in wrappers:
            if tree[0] == wrapper:
                tree = tree[1]
                break
        if isinstance(tree, (list, tuple)):
            for node in tree:
                remove_wrappers(node)


def translate_prop_list(prop_list):
    for prop in prop_list:
        # Translate prop into STLe format
        generate_property(prop)
        # Each property will be stored in a 'temporary.stl' file
        # STL 1.0 format
        prop_list = ["(F ())", "(G ())"]
        return prop_list


def translate_eval_list(eval_list):
    None


def translate_psi(cpn_tree):
    # cpn_tree == ('PSI', OP, PHI)
    _, op, phi = cpn_tree
    formula = '({0} {1})'.format(op, generate_property(phi))
    return formula


# <BOOLEAN> ::= false | true
def generate_boolean(tree_cpn):
    if tree_cpn[0]:
        return 'true'
    else:
        return 'false'


# <NUMBER> ::= Floating-point number | inf | -inf
# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generate_interval(tree_cpn):
    return '({0} {1})'.format(tree_cpn[1], tree_cpn[2])


# <VARIABLE> ::= x<INTEGER>
def generate_variable(tree_cpn):
    variable_counter += 1
    dic[tree_cpn[1]] = variable_counter
    return 'x' + str(variable_counter)


# (<FUNCTION> <FORMULA>*)
def generate_function(tree_cpn):
    if tree_cpn[0] == 'BIN_BOOL_OP' or tree_cpn[0] == 'BIN_COND':
        sol = '('
        for i in len(tree_cpn):
            if i > 0:
                sol += generate_property(tree_cpn[i])
        return sol
    return None


# Input: treeSTLE (tuple)
#     (<VARIABLE>, )  |
#     (<NUMBER>, )    |
#     (<BOOLEAN>, )   |
#     (<FUNCTION> <FORMULA>*)   |
#     (F, <INTERVAL>, <FORMULA>)  |
#     (G, <INTERVAL>, <FORMULA>)"  |
#     (UNTIL, <INTERVAL>, <FORMULA>, <FORMULA>)

# Output: (str)
# <FORMULA> ::=
#     <VARIABLE>  |
#     <NUMBER>    |
#     <BOOLEAN>   |
#     (<FUNCTION> <FORMULA>*)   |
#     (F <INTERVAL> <FORMULA>)  |
#     (G <INTERVAL> <FORMULA>)  |
#     (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generate_property(prop):
    # prop = ('PROP', ID, PHI/PSI)
    _, id_prop, phi_or_psi = prop
    return id_prop, transform_formula(phi_or_psi)


def transform_formula(tree_cpn):
    var_type = str(tree_cpn[0]).lower()
    if var_type == 'variable':
        formula = generate_variable(tree_cpn)
    elif var_type == 'number':
        formula = str(tree_cpn)
    elif var_type == 'boolean':
        formula = generate_boolean(tree_cpn)
    elif var_type == 'function':
        formula = generate_function(tree_cpn)
    elif var_type == 'f':
        formula = generate_f(tree_cpn)
    elif var_type == 'g':
        formula = generate_g(tree_cpn)
    elif var_type == 'u':
        formula = generate_u(tree_cpn)
    return formula


# (F <INTERVAL> <FORMULA>)
def generate_f(tree_cpn):
    sol = '(F '
    sol += generate_interval(tree_cpn[2])
    sol = ' '
    sol += generate_property(tree_cpn[3])
    sol += ')'
    return sol


# (G <INTERVAL> <FORMULA>)
def generate_g(tree_cpn):
    sol = '(G '
    sol += generate_interval(tree_cpn[2])
    sol = ' '
    sol += generate_property(tree_cpn[3])
    sol += ')'
    return sol


# Precondition: treeCPN := treeCPN[0]='F', treeCPN[1]=<TreeInterval>;
# <TreeInterval> := <TreeInterval>[0]=INTERVAL, <TreeInterval>[1] = <name>, <TreeInterval>[2] = <name>
# stringCPN: 'F[<value>,<value>]', <value> = <name> | <integer>, <name> = r{[a-zA-Z][a-zA-Z]*[0-9]*}, <integer> = r{[0-9]+}
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generate_u(tree_cpn):
    sol = '(StlUntil '
    sol += generate_interval(tree_cpn)
    sol = ' '
    sol += generate_property(tree_cpn)
    sol = ' '
    sol += generate_property(tree_cpn)
    sol += ')'
    return sol
