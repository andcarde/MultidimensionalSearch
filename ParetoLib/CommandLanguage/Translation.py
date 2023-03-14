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

# TODO Do we need to use it?
# Diccionario de preposiciones atomicas
ap = {}

# To count how many variables has been declared
global variable_counter
variable_counter = 0

# To map variable names into variable 'x<NUMBER' format
global dic


# STLCommand
def translate(cpn_tree):
    if cpn_tree[0] == 'max':
        formula = generate_number(cpn_tree)
    elif cpn_tree[0] == 'min':
        formula = generate_formula(cpn_tree)
    return formula


def build_string(tree):
    string = ""
    check(tree, string)
    return string


def check(nodo_actual, string):
    if nodo_actual.left is not None:
        check(nodo_actual.left, string)
    string = string + nodo_actual.raiz
    if nodo_actual.left is not None:
        check(nodo_actual.right, string)


# <NUMBER> ::= Floating-point number | inf | -inf
def generate_number(tree_cpn):
    return tree_cpn[0]


# <BOOLEAN> ::= false | true
def generate_boolean(tree_cpn):
    if tree_cpn[0]:
        return 'true'
    else:
        return 'false'


# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generate_interval(tree_cpn):
    sol = '('
    sol += generate_number(tree_cpn[1])
    sol += ','
    sol += generate_number(tree_cpn[2])
    sol += ')'
    return sol


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
                sol += generate_formula(tree_cpn[i])
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
def generate_formula(tree_cpn):
    sol = ''
    for i in range(len(tree_cpn)):
        if i != 0:
            if i != 1 and i != len(tree_cpn):
                sol += ' '
            sol += transform_formula(tree_cpn[i])
    if len(tree_cpn) > 1:
        sol = '(' + sol + ')'
    return sol


def transform_formula(tree_cpn):
    var_type = str(tree_cpn[0]).lower()
    if var_type == 'variable':
        formula = generate_variable(tree_cpn)
    elif var_type == 'number':
        formula = generate_number(tree_cpn)
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
    sol += generate_formula(tree_cpn[3])
    sol += ')'
    return sol


# (G <INTERVAL> <FORMULA>)
def generate_g(tree_cpn):
    sol = '(G '
    sol += generate_interval(tree_cpn[2])
    sol = ' '
    sol += generate_formula(tree_cpn[3])
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
    sol += generate_formula(tree_cpn)
    sol = ' '
    sol += generate_formula(tree_cpn)
    sol += ')'
    return sol
