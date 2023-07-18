
import os
import tempfile

# TODO:
#  - Use id_dict for checking id names
#       - Problema asociado: id_dict no diferencia entre los nombre de las variables declaradas en la sección de <PROP_LIST>,
#       los nombres de los parámetros declarados en la sección de <DEFINITIONS>, ni de las componentes de señal declarados, ni de
#       componentes de señal probabilística declarados.
#  - import and use tokens (keywords) from ParetoLib.CommandLanguage.Parser
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
- Se traducirá el lenguaje STLE3 a STLE1
- Encargarse de que sale una variable una solo vez
- Asegurarse de que tengan sentido las expresiones
    - Si asignamos un valor Tipo1 (ej: Entero) un valor Tipo2 (ej: Boolean) será incorrecto.
- Contruir la string en lenguage STL1
'''

'''
Input: AST (árbol (estructura de datos) con el análisis sintáctico de STLE3).
Output:
    - STL file
    - Param file
'''

# Function in charge of translating: <SPEC_FILE>
# -- <SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>
def translate(tree_com_lang):
    # Auxiliary memory as a solution to poor class and interface design
    memory = init_memory()

    assert tree_com_lang[0] == 'SPEC_FILE'

    # <DEFINITION> Node: tree_com_lang[1] == ('DEF', t[1])
    _, defs = tree_com_lang[1]
    signal_variables, prob_signal_variables, parameters = translate_defs(defs)

    # TODO: Todas las prop de prop_list usan todos los parametros de parameters?
    #  -> Se pueden crear ficheros temporales "personalizados" por propiedad.
    #  Es decir, se crearia un fichero temporal de parametros con un subconjunto de parametros del conjuto inicial
    # Save parameters into temporary file and save record
    param_file_name = create_params_file(memory)
    create_params(memory, param_file_name, parameters)

    # <PROP_LIST>
    # tree_com_lang[2] == ('PROP_LIST', t[2])
    _, prop_list = tree_com_lang[2]
    # TODO: make "translate_prop_list" return the list of properties "prop_list" in new format ("new_prop_list")
    # Warning: cuidado con propiedades anidadas! E.g.:
    # prop_1 := (s1 > 0)
    # prop_2 := F prop_1
    new_prop_list = translate_prop_list(memory, prop_list)

    # TODO: Create one file per property?, Or use a single file for storing all the properties?
    #  I prefer the first option. --> @Andres: please, manage this issue.
    prop_file_name = create_prop_file()
    create_prop(memory, prop_file_name, new_prop_list)

    # <EVAL_LIST>
    # cpn_tree[3] == ('EVAL_LIST', t[3])
    _, eval_list = tree_com_lang[3]
    translate_eval_list(eval_list)

    # TODO:
    #  1) desenrollar las propiedades anidadas y
    #  2) recuperar los enlaces a las rutas temporales de los ficheros de prop y param correspondientes
    #  --> devolver una estructura de datos tipo diccionario como resultado de translate_eval_list?


def init_memory():
    # Memoria
    memory = {}

    # Parameters that has been declared
    memory.parameters = {}

    # To count how many variables has been declared
    memory.components_counter = 0

    # To map components (signals) names into variable 'x<NUMBER' format
    memory.components = {}

    # Properties list
    memory.properties = {}

    # Keep the name of the file of params that has to be return
    memory.param_file_name = None

    # Indicates is the actual signal is probabilistic or not
    memory.is_probsignal = False

    return memory


def translate_param_list(memory, tree):
    for param in tree:
        memory.parameters.append(param)


def translate_interval(interval):
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


def translate_signal(sig):
    if len(sig) == 1:
        return sig[0]
    else:
        return f"({translate_operator(sig[1])} {translate_signal(sig[0])} {translate_signal(sig[2])})"


def basic_translate(tree):
    if isinstance(tree, list):
        if tree[0] in ["AND", "OR", "NOT", "IMPLY", "LEQ", "LESS", "GEQ", "GREATER", "NEQ", "PLUS", "MINUS", "TIMES",
                       "DIVIDE"]:
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


# Preocondition of translate_defs(defs):
# defs are defined by:
# -- <DEF> ::= <PARAM_DEF> | <SIGNAL_DEF> | <PROBSIGNAL_DEF>
# -- <DEFINITIONS> ::= <DEF> | <DEF> <DEFINITIONS>
# -- <PARAM_DEF> ::= <LET> <PARAM> <PARAM_LIST> <SEMICOLON>
# -- <SIGNAL_DEF> ::= <LET> <SIGNAL> <SIGNAL_LIST> <SEMICOLON>
# -- <PROBSIGNAL_DEF> : <LET> <PROBABILISTIC> <SIGNAL> <PROBSIGNAL_LIST> <SEMICOLON>
# -- <PARAM_LIST> ::= <ID_LIST>
# -- <SIGNAL_LIST> ::= <ID_LIST>
# -- <PROBSIGNAL_LIST> ::= <ID_LIST>
# -- <ID_LIST> ::= ID | ID COMMA ID_LIST

def translate_defs(defs):
    # Signal components
    signal_variables = []

    # Probabilistic signal components
    prob_signal_variables = []

    # Parameters that have been declared
    parameters = []

    # <DEFINITIONS> == (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
    for (keyword, signal_or_param_list) in defs:
        if keyword == 'SIGNAL_LIST':
            # signal_variables == ["s1", "s2", ...]
            signal_variables = signal_or_param_list
        elif keyword == 'PROBSIGNAL_LIST':
            # prob_signal_variables == ["s1", "s2", ...]
            prob_signal_variables = signal_or_param_list
        elif keyword == 'PARAM_LIST':
            # parameters == ["s1", "s2", ...]
            parameters = signal_or_param_list

    # TODO: Check that signal_variables \intersection prob_signal_variables \intersection parameters == 0
    #  --> Identifiers must be different
    # It is checked in the Parser.
    return signal_variables, prob_signal_variables, parameters

def create_params_file():
    stl_param = tempfile.NamedTemporaryFile(delete=False)
    stl_param_file = stl_param.name
    stl_param.close()
    return stl_param_file

def write_params(file_name, parameters):
    with open(file_name, 'w') as file:
        for param in parameters:
            line = param.name
            if hasattr(param, 'inferior'):
                line += ' ' + str(param.below_limit)
            if hasattr(param, 'superior'):
                line += ' ' + str(param.upper_limit)
            file.write(line + '\n')


def translate_prop_list(memory, prop_list):
    for prop in prop_list:
        memory.actual_property_param = []
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
        param_file_name = create_params_file()
        memory.properties.push(param_file_name)
        write_params(param_file_name, memory.actual_property_param)

# Information required in translate_phi(memory, phi):
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
<PSI> : <MIN> <PHI>
            | <MAX> <PHI>
            | <INT> <PHI>
            | <DER> <PHI>
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


def create_prop_file():
    stl_prop = tempfile.NamedTemporaryFile(delete=False)
    stl_prop_file = stl_prop.name
    stl_prop.close()
    return stl_prop_file


def create_prop(prop_file_name, prop_list):
    # Crear la carpeta temp si no existe
    if not os.path.exists(prop_file_name):
        os.makedirs(prop_file_name)

    # Crear el archivo param.txt en la carpeta temp
    with open(prop_file_name.join('/prop.txt'), 'w') as f:
        for prop in prop_list:
            # Escribir cada parámetro en una línea diferente
            f.write(f"{prop}\n")



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


def translate_psi(memory, tree_com_lang):
    # cpn_tree == ('PSI', OP, PHI)
    _, op, phi = tree_com_lang
    formula = '({0} {1})'.format(op, generate_property(phi))
    return formula


# <BOOLEAN> ::= false | true
def generate_boolean(memory, tree_com_lang):
    if tree_com_lang[0]:
        return 'true'
    else:
        return 'false'


# <NUMBER> ::= Floating-point number | inf | -inf
# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generate_interval(memory, tree_com_lang):
    return '({0} {1})'.format(tree_com_lang[1], tree_com_lang[2])


# <VARIABLE> ::= x<INTEGER>
def generate_variable(memory, tree_com_lang):
    # To map variable names into variable 'x<NUMBER' format
    memory.signal_variable_counter += 1
    memory.signal_variables[tree_com_lang[1]] = memory.signal_variable_counter
    return 'x' + str(memory.signal_variable_counter)


# (<FUNCTION> <FORMULA>*)
def generate_function(memory, tree_com_lang):
    sol = None
    if tree_com_lang[0] == 'BIN_BOOL_OP' or tree_com_lang[0] == 'BIN_COND':
        sol = '({0})'.format(generate_property(prop_i) for prop_i in tree_com_lang[1:])
    return sol

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


def transform_formula(memory, tree_com_lang):
    var_type = str(tree_com_lang[0]).lower()
    if var_type == 'variable':
        formula = generate_variable(memory, tree_com_lang)
    elif var_type == 'number':
        formula = str(tree_com_lang)
    elif var_type == 'boolean':
        formula = generate_boolean(memory, tree_com_lang)
    elif var_type == 'function':
        formula = generate_function(memory, tree_com_lang)
    elif var_type == 'f':
        formula = generate_f(memory, tree_com_lang)
    elif var_type == 'g':
        formula = generate_g(memory, tree_com_lang)
    elif var_type == 'u':
        formula = generate_u(memory, tree_com_lang)
    return formula


# (F <INTERVAL> <FORMULA>)
def generate_f(memory, tree_com_lang):
    sol = '(F {0} {1})'.format(generate_interval(tree_com_lang[2]),
                               generate_property(tree_com_lang[3]))
    return sol


# (G <INTERVAL> <FORMULA>)
def generate_g(memory, tree_com_lang):
    sol = '(G {0} {1})'.format(generate_interval(tree_com_lang[2]),
                               generate_property(tree_com_lang[3]))
    return sol


# Precondition: treeCPN := treeCPN[0]='F', treeCPN[1]=<TreeInterval>;
# <TreeInterval> := <TreeInterval>[0]=INTERVAL, <TreeInterval>[1] = <name>, <TreeInterval>[2] = <name>
# stringCPN: 'F[<value>,<value>]', <value> = <name> | <integer>, <name> = r{[a-zA-Z][a-zA-Z]*[0-9]*}, <integer> = r{[0-9]+}
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generate_u(memory, tree_com_lang):
    sol = '(StlUntil {0} {1} {2})'.format(generate_interval(tree_com_lang),
                                          generate_property(tree_com_lang),
                                          generate_property(tree_com_lang))
    return sol

''' NOT USED
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
'''