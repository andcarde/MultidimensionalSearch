import os
import tempfile

'''
· Language STLE1 syntax

-- Extra, not treated
[Omitted] <TERNARY> ::= ite <FUNCTION> <VALUE> <VALUE>
[Omitted] <VALUE> ::= <NUMBER> | <VARIABLE>

^ ::= <FORMULA>
<FORMULA> ::= <VARIABLE> |
              <NUMBER> |
              <BOOLEAN> |
              ( <FUNCTION> <FORMULA>* ) |
              ( F <INTERVAL> <FORMULA> ) |
              ( G <INTERVAL> <FORMULA> ) |
              ( StlUntil <INTERVAL> <FORMULA> <FORMULA> ) |
              ( On <INTERVAL> <AGGREGATE> ) |
              ( Until <INTERVAL> <NUMBER> <AGGREGATE> <FORMULA> ) |
              [Omitted] -- ( Until <INTERVAL> <NUMBER> ( Get <FORMULA> ) <FORMULA> ) | --
              ( Lookup <NUMBER> <NUMBER> <FORMULA> )
<VARIABLE> ::= x<INTEGER>
<NUMBER> ::= <FLOAT_NUMBER> | inf | -inf
<FLOAT_NUMBER> ::= \d*\.?\d+
<BOOLEAN> ::= false | true
<FUNCTION> ::= <ARITHMETIC> | <COMPARATION> | <LOGICAL_OP> | <BOOLEAN>
<ARITHMETIC> ::= min | max | + | - | / | * | abs
<COMPARATION> ::= < | <= | > | >=
<LOGICAL_OP> ::= and |or | not | ->
<INTERVAL> ::= ( <NUMBER> <NUMBER> )
<AGGREGATE> ::= ( Min <FORMULA> ) | ( Max <FORMULA> )
'''

'''
· Language STLE2 syntax
^ ::= <SPEC_FILE>
<SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>

<DEFINITIONS> ::= <DEF> | <DEF> <DEFINITIONS>?
<DEF> ::= <PARAM_DEF> | <SIGNAL_DEF> | <PROBSIGNAL_DEF>
<PARAM_DEF> ::= <LET> <PARAM> <PARAM_LIST> <SEMICOLON>
<PARAM_LIST> ::= <ID_LIST>
<ID_LIST> ::= ID | ID COMMA ID_LIST
<ID> ::= [TERMINAL]
<SIGNAL_DEF> ::= <LET> <SIGNAL> <SIGNAL_LIST> <SEMICOLON>
<SIGNAL_LIST> ::= <ID_LIST>
<PROBSIGNAL_DEF> : <LET> <PROBABILISTIC> <SIGNAL> <PROBSIGNAL_LIST> <SEMICOLON>
<PROBSIGNAL_LIST> ::= <ID_LIST>

<PROP_LIST> : <PROP> | <PROP> [<PROP_LIST>]?
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
<SIG> : <ID>
        | <CONSTANT_SIGNAL>
        | <SIG> <BIN_OP> <SIG>
        | <LPAREN> <SIG> <RPAREN>
<CONSTANT_SIGNAL> : <NUMBER>
<NUMBER> ::= [TERMINAL]
<BIN_OP> : <PLUS>
    | <MINUS>
    | <TIMES>
    | <DIVIDE>
<FUNC> : <SIG> <BIN_COND> <SIG>
<BIN_BOOL_OP> : <AND>
        | <OR>
        | <IMPLY>
<BIN_COND> : <LEQ>
    | <LESS>
    | <GEQ>
    | <GREATER>
    | <NEQ>
<INTVL> ::= <LBRACK> <NUMBER_ID> <COMMA> <NUMBER_ID> <RBRACK>
<NUMBER_ID> ::= <NUMBER> | <ID>
<PSI> : <MIN> <PHI>
            | <MAX> <PHI>
            | <INT> <PHI>
            | <DER> <PHI>

<EVAL_LIST> ::= <EVAL_EXPR> [<EVAL_LIST>]?
<EVAL_EXPR> ::= <EVAL> <ID> <ON> <ID_LIST> <WITH> <INTVL_LIST>
<INTVL_LIST> ::= <ID> <IN> <INTVL> [<COMMA> <INTVL_LIST>]?
<NUMBER_ID> ::= <NUMBER> | <ID>
'''

'''
Input:
    AST (tree of the STLE2 syntax analysis).
Output:
    List of pairs STL file and param file
'''


# Function in charge of translating: <SPEC_FILE>
# -- <SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>


def translate(tree_com_lang):
    # Dictionary of properties. Each property is a pair with the file name path of the parameters and the file name path
    # of the language STLE1
    translations = {}

    # Auxiliary memory as a solution to poor class and interface design
    memory = init_memory(translations)

    assert tree_com_lang[0] == 'SPEC_FILE'

    # <DEFINITION> Node: tree_com_lang[1] == ('DEF', t[1])
    _, definitions = tree_com_lang[1]
    signal_variables, prob_signal_variables, parameters = translate_definitions(definitions)

    # TODO: Todas las prop de prop_list usan todos los parametros de parameters?
    #  -> Se pueden crear ficheros temporales "personalizados" por propiedad.
    #  Es decir, se crearia un fichero temporal de parámetros con un subconjunto de parametros del conjuto inicial

    # <PROP_LIST>
    # tree_com_lang[2] == ('PROP_LIST', t[2])
    _, prop_list = tree_com_lang[2]
    # TODO: make "translate_prop_list" return the list of properties "prop_list" in new format ("new_prop_list")
    # Warning: cuidado con propiedades anidadas! E.g.:
    # prop_1 := (s1 > 0)
    # prop_2 := F prop_1

    prop_file_name = create_prop_file()
    create_prop(prop_file_name, memory.properties[len(memory.properties) - 1])

    # <EVAL_LIST>
    # cpn_tree[3] == ('EVAL_LIST', t[3])
    _, eval_list = tree_com_lang[3]
    translate_eval_list(memory, eval_list)

    # TODO:
    #  1) desenrollar las propiedades anidadas y
    #  2) recuperar los enlaces a las rutas temporales de los ficheros de prop y param correspondientes
    return translations


def init_memory(translations):
    class Memory:
        def __init__(self):
            # Parameters that has been declared
            self.parameters = {}

            # To count how many variables has been declared
            self.components_counter = 0

            # To map components (signals) names into variable 'x<NUMBER' format
            self.components = {}

            # Properties list
            self.properties = translations

            # Keep the name of the file of params that has to be return
            self.param_file_name = None

            # Indicates is the actual signal is probabilistic or not
            self.is_probabilistic_signal = False

    # Create an object 'memory'
    return Memory()


def translate_param_list(memory, tree):
    for param in tree:
        memory.parameters.append(param)


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
    return f"({func[0]} {' '.join(map(str, map(translate, func[1:])))})"


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
            return ' '.join(map(str, map(translate, tree)))
    else:
        return str(tree)


# Precondition of translate_definitions(definitions):
# definitions are defined by:
# -- <DEF> ::= <PARAM_DEF> | <SIGNAL_DEF> | <PROBSIGNAL_DEF>
# -- <DEFINITIONS> ::= <DEF> | <DEF> <DEFINITIONS>
# -- <PARAM_DEF> ::= <LET> <PARAM> <PARAM_LIST> <SEMICOLON>
# -- <SIGNAL_DEF> ::= <LET> <SIGNAL> <SIGNAL_LIST> <SEMICOLON>
# -- <PROBSIGNAL_DEF> : <LET> <PROBABILISTIC> <SIGNAL> <PROBSIGNAL_LIST> <SEMICOLON>
# -- <PARAM_LIST> ::= <ID_LIST>
# -- <SIGNAL_LIST> ::= <ID_LIST>
# -- <PROBSIGNAL_LIST> ::= <ID_LIST>
# -- <ID_LIST> ::= ID | ID COMMA ID_LIST

def translate_definitions(definitions):
    # Signal components
    signal_variables = []

    # Probabilistic signal components
    prob_signal_variables = []

    # Parameters that have been declared
    parameters = []

    # <DEFINITIONS> == (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
    for (keyword, signal_or_param_list) in definitions:
        if keyword == 'SIGNAL_LIST':
            # signal_variables == ["s1", "s2", ...]
            signal_variables = signal_or_param_list
        elif keyword == 'PROBSIGNAL_LIST':
            # prob_signal_variables == ["s1", "s2", ...]
            prob_signal_variables = signal_or_param_list
        elif keyword == 'PARAM_LIST':
            # parameters == ["s1", "s2", ...]
            parameters = signal_or_param_list

    return signal_variables, prob_signal_variables, parameters


def create_file():
    file = tempfile.NamedTemporaryFile(delete=False)
    file_name = file.name
    file.close()
    return file_name


def write_params(file_name, parameters):
    with open(file_name, 'w') as file:
        for param in parameters:
            line = param.name
            if hasattr(param, 'inferior'):
                line += ' ' + str(param.below_limit)
            if hasattr(param, 'superior'):
                line += ' ' + str(param.upper_limit)
            file.write(line + '\n')


def write_property(file_name, my_property):
    with open(file_name, 'w') as file:
        file.write(my_property + '\n')


# TODO: ¿formula?
def translate_prop_list(memory, prop_list):
    for prop in prop_list:
        memory.actual_property_param = []
        # Translate prop into STLe1 format
        my_id, formula = generate_property(memory, prop)

        if prop[2][0] == "PSI":
            my_property = translate_psi(memory, prop[2][1])
        else:
            my_property = translate_phi(memory, prop[2][1])

        memory.properties[my_id] = my_property

        param_file_name = create_file()
        # Each property will be stored in a 'temporary.stl' file STL 1.0 format
        stl_prop_file = create_file()
        memory.translations.push([param_file_name, stl_prop_file])

        write_params(param_file_name, memory.actual_property_param)
        write_property(stl_prop_file, my_property)


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

'''


def translate_phi(memory, phi):
    if phi[1][0] == "SIG":
        return phi[1]
    elif phi[1][0] == "ID":
        return phi[1]
    elif phi[1][0] == "FUNC":
        return translate_function(phi[1])
    elif phi[1][0] == "NOT":
        return "not".join(translate_phi(memory, phi[2]))
    elif phi[1][0] == "PROB":
        return "prob".join(translate_phi(memory, phi[2]))
    elif phi[1][0] == "BIN_BOOL_OP":
        return "(" + translate_bool_op(phi[1]).join(translate_phi(memory, phi[2])) \
            .join(translate_phi(memory, phi[3])) + ")"
    elif phi[1][0] == "F":
        return generate_f(memory, phi)
    elif phi[1][0] == "G":
        return generate_g(memory, phi)
    elif phi[1][0] == "UNTIL":
        return generate_u(memory, phi)
    elif phi[1][0] == "ON":
        return generate_on(memory, phi)


def create_prop_file():
    stl_prop = tempfile.NamedTemporaryFile(delete=False)
    stl_prop_file = stl_prop.name
    stl_prop.close()
    return stl_prop_file


def create_prop(prop_file_name, prop_list):
    # Create the temp folder if it does not exist
    if not os.path.exists(prop_file_name):
        os.makedirs(prop_file_name)

    # Create the file param.txt in the temporal folder
    with open(prop_file_name.join('/prop.txt'), 'w') as f:
        for prop in prop_list:
            # Write each parameter in a different line
            f.write(f"{prop}\n")


def translate_bool_op(bool_op):
    return bool_op[1]


def generate_on(memory, on_phi):
    interval = translate_interval(on_phi[1])
    psi = translate_psi(memory, on_phi[2])
    return "(" + "ON" + " " + interval + " " + psi + ")"


# <EVAL_EXPR> ::= <EVAL> <ID> <ON> <ID_LIST> <WITH> <INTVL_LIST>
def translate_eval_list(memory, eval_list):
    for eval_expr in eval_list:
        param_list = eval_expr[2]
        interval_list = eval_expr[3]
        index = 0
        for param in param_list:
            parameter = {}
            parameter.name = param
            parameter.below_limit = interval_list[index][0]
            parameter.upper_limit = interval_list[index][1]
            memory.parameters.append(memory.parameters, parameter)


'''
<PSI> : <MIN> <PHI>
    | <MAX> <PHI>
    | <INT> <PHI>
    | <DER> <PHI>
'''


def translate_psi(memory, tree_com_lang):
    # cpn_tree == ('PSI', OP, PHI)
    _, op, phi = tree_com_lang
    formula = '({0} {1})'.format(op, generate_property(memory, phi))
    return formula


# <BOOLEAN> ::= false | true
def generate_boolean(tree_com_lang):
    if tree_com_lang[0]:
        return 'true'
    else:
        return 'false'


# <NUMBER> ::= Floating-point number | inf | -inf
# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generate_interval(tree_com_lang):
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
        sol = '({0})'.format(generate_property(memory, prop_i) for prop_i in tree_com_lang[1:])
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


def generate_property(memory, prop):
    # prop = ('PROP', ID, PHI/PSI)
    _, id_prop, phi_or_psi = prop
    return id_prop, transform_formula(memory, phi_or_psi)


def transform_formula(memory, tree_com_lang):
    var_type = str(tree_com_lang[0]).lower()
    if var_type == 'variable':
        formula = generate_variable(memory, tree_com_lang)
    elif var_type == 'number':
        formula = str(tree_com_lang)
    elif var_type == 'boolean':
        formula = generate_boolean(tree_com_lang)
    elif var_type == 'function':
        formula = generate_function(memory, tree_com_lang)
    elif var_type == 'f':
        formula = generate_f(memory, tree_com_lang)
    elif var_type == 'g':
        formula = generate_g(memory, tree_com_lang)
    elif var_type == 'u':
        formula = generate_u(memory, tree_com_lang)
    else:
        formula = None
    return formula


# (F <INTERVAL> <FORMULA>)
def generate_f(memory, tree_com_lang):
    sol = '(F {0} {1})'.format(generate_interval(tree_com_lang[2]),
                               generate_property(memory, tree_com_lang[3]))
    return sol


# (G <INTERVAL> <FORMULA>)
def generate_g(memory, tree_com_lang):
    sol = '(G {0} {1})'.format(generate_interval(tree_com_lang[2]),
                               generate_property(memory, tree_com_lang[3]))
    return sol


# Precondition:
# treeCPN := treeCPN[0]='F', treeCPN[1]=<TreeInterval>;
# <TreeInterval> := <TreeInterval>[0]=INTERVAL, <TreeInterval>[1] = <name>, <TreeInterval>[2] = <name>
# stringCPN: 'F[<value>,<value>]', <value> = <name> |
#      <integer>, <name> = r{[a-zA-Z][a-zA-Z]*[0-9]*}, <integer> = r{[0-9]+}
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generate_u(memory, tree_com_lang):
    return '(StlUntil {0} {1} {2})'.format(generate_interval(tree_com_lang),
                                           generate_property(memory, tree_com_lang),
                                           generate_property(memory, tree_com_lang))
