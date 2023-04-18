from ParetoLib.CommandLanguage.Parser import parser, id_dict

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


# STLCommand
def translate(cpn_tree):
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
