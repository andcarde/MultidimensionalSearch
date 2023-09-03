import os
import tempfile


class Keys:
    def __init__(self):
        # Dictionary of names
        self.id_dictionary = dict()
        self.duplicated_keys = []

    def add_key(self, key):
        if key in self.id_dictionary.keys():
            self.duplicated_keys.append(key)
        else:
            # Insert type of ID
            self.id_dictionary[key] = key

    def get_duplicated_keys(self):
        return self.duplicated_keys


def translate(stl_tree):
    """
    Translates an STL tree into an instance of the Translation class

    Args:
        AST (tree of the STLE2 syntax analysis).
    Returns:
        List of pairs STL file and param file
        :param stl_tree: Signal Temporal Logic Tree, it is a tree (data structure) where the data belonging
            to a temporal logic signal language have been standardized
    """
    # Dictionary of properties. Each property is a pair with the file name path of
    # the parameters and the file name path of the language STLE1
    translations = {}

    # Auxiliary memory as a solution to poor class and interface design
    memory = Memory(translations)

    assert stl_tree[0] == 'SPEC_FILE'
    translate_spec_file(memory, stl_tree)

    return translations


def translate_spec_file(memory, stl_tree):
    """
    Function in charge of translating:
        <SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>

    :param memory: instance of class Memory
    :param stl_tree: Signal Temporal Logic Tree, it is a tree (data structure) where the data belonging
            to a temporal logic signal language have been standardized
    :return: no
    """
    # <DEFINITION> Node: tree_com_lang[1] == ('DEF', t[1])
    _, definitions = stl_tree[1]
    translate_definitions(memory, definitions)

    # <PROP_LIST>
    # tree_com_lang[2] == ('PROP_LIST', t[2])
    _, prop_list = stl_tree[2]

    prop_file_name = create_prop_file()
    create_prop(prop_file_name, memory.properties[len(memory.properties) - 1])

    # <EVAL_LIST>
    # tree_com_lang[3] == ('EVAL_LIST', t[3])
    _, eval_list = stl_tree[3]
    translate_eval_list(memory, eval_list)


class Memory:
    def __init__(self, translations):
        # Signal variables (probabilistic and common)
        self.signal_variables = {}

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

def translate_definitions(memory, definitions):
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

    memory.signal_variables = signal_variables
    memory.signal_variables = prob_signal_variables
    i = 0
    for parameter in parameters:
        memory.parameters.push(parameter, 'x'.join(str(i)))
        i += 1


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


def translate_prop_list(memory, prop_list):
    for prop in prop_list:
        memory.actual_property_param = []
        formula = generate_property(memory, prop)

        param_file_name = create_file()
        # Each property will be stored in a 'temporary.stl' file STL 1.0 format
        stl_prop_file = create_file()
        memory.translations.push([param_file_name, stl_prop_file])

        write_params(param_file_name, memory.actual_property_param)
        write_property(stl_prop_file, formula)


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
    _, prop_id, phi_or_psi = prop

    # Translate prop into STLe1 format
    if phi_or_psi[0] == "PSI":
        formula = translate_psi(memory, prop[2])
    else:
        formula = translate_phi(memory, prop[2])

    memory.properties[prop_id] = formula
    return formula


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


def translate_phi(memory, tree_com_lang):
    var_type = str(tree_com_lang[0]).lower()
    body = tree_com_lang[1]
    if var_type == 'variable':
        formula = generate_variable(memory, body)
    elif var_type == 'function':
        formula = generate_function(memory, body)
    elif var_type == 'sig':
        formula = tree_com_lang[1]
    elif var_type == "id":
        my_id = tree_com_lang[1]
        formula = memory.properties[my_id]
    elif var_type == 'func':
        formula = translate_function(tree_com_lang[1])
    elif var_type == 'not':
        formula = "not".join(translate_phi(memory, tree_com_lang[2]))
    elif var_type == 'prob':
        formula = "prob".join(translate_phi(memory, tree_com_lang[2]))
    elif var_type == 'bin_bool_op':
        formula = "(" + translate_bool_op(tree_com_lang[1]).join(translate_phi(memory, tree_com_lang[2])) \
            .join(translate_phi(memory, tree_com_lang[3])) + ")"
    elif var_type == 'number':
        formula = str(body)
    elif var_type == 'boolean':
        formula = generate_boolean(body)
    elif var_type == 'f':
        formula = generate_f(memory, body)
    elif var_type == 'g':
        formula = generate_g(memory, body)
    elif var_type == 'until':
        formula = generate_u(memory, body)
    elif var_type == 'on':
        formula = generate_on(memory, body)
    else:
        formula = None
    return formula


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
