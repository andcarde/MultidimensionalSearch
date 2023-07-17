
import os
import tempfile
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
<TERNARY> ::= ite <FUNCTION> <VALUE> <VALUE> // Omitido
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
              ( Until <INTERVAL> <NUMBER> ( Get <FORMULA> ) <FORMULA> ) | // Omitido
              ( Lookup <NUMBER> <NUMBER> <FORMULA> )
^ ::= <FORMULA>

· Sintaxis del lenguaje STLe2 aplicada
^ ::= <SPEC_FILE>
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

# Memoria
memory = {}

# Parameters that has been declared
memory.parameters = {}

# To count how many variables has been declared
memory.variable_counter = 0

# To map variable names into variable 'x<NUMBER' format
memory.variables = {}

# Lista de propiedades
memory.propiedades = {}


def translate_param_list(memory, tree):
    for param in tree:
        memory.parameters.append(param)


def translate_interval(memory, interval):
    if len(interval) == 3:
        return f"({interval[1]} {interval[2]})"
    else:
        return f"({interval[1]} {interval[2]} {interval[3]})"

def translate_operator(memory, op):
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


def translate_signal(memory, sig):
    if len(sig) == 1:
        return sig[0]
    else:
        return f"({translate_operator(memory, sig[1])} {translate_signal(sig[0])} {translate_signal(sig[2])})"


def basic_translate(memory, tree):
    if isinstance(tree, list):
        if tree[0] in ["AND", "OR", "NOT", "IMPLY", "LEQ", "LESS", "GEQ", "GREATER", "NEQ", "PLUS", "MINUS", "TIMES", "DIVIDE"]:
            return translate_function(memory, tree)
        elif tree[0] == "ID":
            return tree[1]
        elif tree[0] == "NUMBER":
            return str(tree[1])
        elif tree[0] == "INTVL":
            return translate_interval(memory, tree)
        elif tree[0] in ["SIG", "CONSTANT_SIGNAL"]:
            return translate_signal(memory, tree)
        else:
            return ' '.join(map(translate, tree))
    else:
        return str(tree)


'''
def recursive(stle2_array):
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
'''


# <SPEC_FILE> definition
# <SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>
# STLCommand
def translate(cpn_tree):
    assert cpn_tree[0] == 'SPEC_FILE'
    # <DEFINITIONS>
    # cpn_tree[1] == ('DEF', t[1])
    _, defs = cpn_tree[1]
    translate_defs(defs)

    # <PROP_LIST>
    # cpn_tree[2] == ('PROP_LIST', t[2])
    _, prop_list = cpn_tree[2]
    translate_prop_list(memory, prop_list)

    # <EVAL_LIST>
    # cpn_tree[3] == ('EVAL_LIST', t[3])
    _, eval_list = cpn_tree[3]
    translate_eval_list(memory, eval_list)

    create_params()

# <DEF> ::= <PARAM_DEF> | <SIGNAL_DEF> | <PROBSIGNAL_DEF>
# <DEFINITIONS> ::= <DEF> | <DEF> <DEFINITIONS>
# <PARAM_DEF> ::= <LET> <PARAM> <PARAM_LIST> <SEMICOLON>
# <SIGNAL_DEF> ::= <LET> <SIGNAL> <SIGNAL_LIST> <SEMICOLON>
# <PROBSIGNAL_DEF> : <LET> <PROBABILISTIC> <SIGNAL> <PROBSIGNAL_LIST> <SEMICOLON>
# <PARAM_LIST> ::= <ID_LIST>
# <SIGNAL_LIST> ::= <ID_LIST>
# <PROBSIGNAL_LIST> ::= <ID_LIST>
# <ID_LIST> ::= ID | ID COMMA ID_LIST

memory.param_file_name = None
memory.is_probsignal = False
memory.component_number = 0
memory.component_map = {}

def translate_defs(memory, defs):
    # defs == (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
    for (keyword, signal_or_param_list) in defs:
        if keyword == 'SIGNAL_LIST':
            for signal in signal_or_param_list:
                memory.component_map[signal] = "x" + memory.component_number
                memory.component_number += 1
        elif keyword == 'PROBSIGNAL_LIST':
            is_probsignal = True
        elif keyword == 'PARAM_LIST':
            # Save 'signal_or_param_list' into temporary file and save record
            param_list = ["p1", "p2"]
            param_file_name = create_params_file(memory, param_list)


def create_params_file(memory, self):
    stl_param = tempfile.NamedTemporaryFile(delete=False)
    stl_param_file = stl_param.name
    stl_param.close()
    return stl_param_file

def create_params(memory):
    # Crear la carpeta temp si no existe
    if not os.path.exists(memory.param_file_name):
        os.makedirs(memory.param_file_name)

    # Crear el archivo param.txt en la carpeta temp
    with open(memory.param_file_name.join('/param.txt'), 'w') as f:
        for param in memory.parameters:
            # Escribir cada parámetro en una línea diferente
            f.write(f"{param.name}\n")
            if (param.below_limit != "0"):
                f.write(f" {param.below_limit}")
            if (param.upper_limit != "inf"):
                f.write(f" {param.upper_limit}")
            f.write(f"\n")

memory.wrappers = [
    'BIN_BOOL_OP',
    'PROBSIGNAL_LIST',
    'SIGNAL_LIST',
    'PARAM_LIST',
    'DEFINITIONS',
    'PROP_LIST',
    'EVAL_LIST'
]

memory.indicators = [
    'PSI',
    'FUNC',
    'SPEC_FILE',
    'INTVL',
    'EVAL_EXPR',
    'PHI',
]


def remove_wrappers(memory, tree):
    if isinstance(tree, (list, tuple)):
        for indicator in memory.indicators:
            if tree[0] == indicator:
                tree.pop(0)
                break
        for wrapper in memory.wrappers:
            if tree[0] == wrapper:
                tree = tree[1]
                break
        if isinstance(tree, (list, tuple)):
            for node in tree:
                remove_wrappers(node)


def translate_prop_list(memory, prop_list):
    for prop in prop_list:
        # Translate prop into STLe format
        generate_property(memory, prop)
        # Each property will be stored in a 'temporary.stl' file
        # STL 1.0 format
        stl_prop_file = create_prop_file(memory)
        propiedad = None
        if prop[2][0] == "PSI":
            propiedad = translate_psi(memory, prop[2][1])
        else:
            propiedad = translate_phi(memory, prop[2][1])
        memory.propiedades.pop(memory.propiedades, prop[1], propiedad)

'''
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
'''
def translate_phi(memory, phi):
    if phi[1][0] == "SIG":
        return phi[1]
    elif phi[1][0] == "ID":
        return phi[1]
    elif phi[1][0] == "FUNC":
        return translate_function(memory, phi[1])
    elif phi[1][0] == "NOT":
        return "not".join(translate_phi(memory, phi[2]))
    elif phi[1][0] == "PROB":
        return "prob".join(translate_phi(memory, phi[2]))
    elif phi[1][0] == "BIN_BOOL_OP":
        return "(" + translate_bool_op(phi[1]).join(translate_phi(phi[2])).join(translate_phi(phi[3])) + ")"
    elif phi[1][0] == "F":
        return generate_f(phi)
    elif phi[1][0] == "G":
        return generate_g(phi)
    elif phi[1][0] == "UNTIL":
        return generate_u(phi)
    elif phi[1][0] == "ON":
        return generate_on(phi)
'''
<PSI> : <MIN> <PHI>
            | <MAX> <PHI>
            | <INT> <PHI>
            | <DER> <PHI>
'''
def create_prop_file(self):
    stl_prop = tempfile.NamedTemporaryFile(delete=False)
    stl_prop_file = stl_prop.name
    stl_prop.close()
    return stl_prop_file


def translate_bool_op(bool_op):
    return bool_op[1]


def generate_on(on_phi):
    interval = translate_interval(on_phi[1])
    psi = translate_psi(on_phi[2])
    return "(" + "ON" + " " + interval + " " + psi + ")"

# <EVAL_EXPR> ::= <EVAL> <ID> <ON> <ID_LIST> <WITH> <INTVL_LIST>
def translate_eval_list(memory, eval_list):
    for eval_expr in eval_list:
        prop = eval_expr[1]
        param_list =  eval_expr[2]
        interval_list = eval_expr[3]
        index = 0
        for param in param_list:
            parameter = {}
            parameter.name = param
            parameter.below_limit = interval_list[index][0]
            parameter.upper_limit = interval_list[index][1]
            memory.parameters.pop(memory.parameters, parameter)


def translate_psi(memory, cpn_tree):
    # cpn_tree == ('PSI', OP, PHI)
    _, op, phi = cpn_tree
    formula = '({0} {1})'.format(op, generate_property(phi))
    return formula


# <BOOLEAN> ::= false | true
def generate_boolean(memory, tree_cpn):
    if tree_cpn[0]:
        return 'true'
    else:
        return 'false'


# <NUMBER> ::= Floating-point number | inf | -inf
# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generate_interval(memory, tree_cpn):
    return '({0} {1})'.format(tree_cpn[1], tree_cpn[2])


# <VARIABLE> ::= x<INTEGER>
def generate_variable(memory, tree_cpn):
    memory.variable_counter += 1
    memory.variables[tree_cpn[1]] = memory.variable_counter
    return 'x' + str(memory.variable_counter)


# (<FUNCTION> <FORMULA>*)
def generate_function(memory, tree_cpn):
    if tree_cpn[0] == 'BIN_BOOL_OP' or tree_cpn[0] == 'BIN_COND':
        sol = '('
        for i in len(tree_cpn):
            if i > 0:
                sol += generate_property(memory, tree_cpn[i])
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
def generate_property(memory, prop):
    # prop = ('PROP', ID, PHI/PSI)
    _, id_prop, phi_or_psi = prop
    return id_prop, transform_formula(memory, phi_or_psi)


def transform_formula(memory, tree_cpn):
    var_type = str(tree_cpn[0]).lower()
    if var_type == 'variable':
        formula = generate_variable(memory, tree_cpn)
    elif var_type == 'number':
        formula = str(tree_cpn)
    elif var_type == 'boolean':
        formula = generate_boolean(memory, tree_cpn)
    elif var_type == 'function':
        formula = generate_function(memory, tree_cpn)
    elif var_type == 'f':
        formula = generate_f(memory, tree_cpn)
    elif var_type == 'g':
        formula = generate_g(memory, tree_cpn)
    elif var_type == 'u':
        formula = generate_u(memory, tree_cpn)
    return formula


# (F <INTERVAL> <FORMULA>)
def generate_f(memory, tree_cpn):
    sol = '(F '
    sol += generate_interval(memory, tree_cpn[2])
    sol = ' '
    sol += generate_property(memory, tree_cpn[3])
    sol += ')'
    return sol


# (G <INTERVAL> <FORMULA>)
def generate_g(memory, tree_cpn):
    sol = '(G '
    sol += generate_interval(memory, tree_cpn[2])
    sol = ' '
    sol += generate_property(memory, tree_cpn[3])
    sol += ')'
    return sol


# Precondition: treeCPN := treeCPN[0]='F', treeCPN[1]=<TreeInterval>;
# <TreeInterval> := <TreeInterval>[0]=INTERVAL, <TreeInterval>[1] = <name>, <TreeInterval>[2] = <name>
# stringCPN: 'F[<value>,<value>]', <value> = <name> | <integer>, <name> = r{[a-zA-Z][a-zA-Z]*[0-9]*}, <integer> = r{[0-9]+}
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generate_u(memory, tree_cpn):
    sol = '(StlUntil '
    sol += generate_interval(memory, tree_cpn)
    sol = ' '
    sol += generate_property(memory, tree_cpn)
    sol = ' '
    sol += generate_property(memory, tree_cpn)
    sol += ')'
    return sol