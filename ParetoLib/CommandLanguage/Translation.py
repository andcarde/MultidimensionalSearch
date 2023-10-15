# <Translation.py>
# Exports: translate function, Translation class
from ParetoLib.CommandLanguage.FileUtils import create_and_write_to_file


class STLe1Pack:
    """
    This class stores the correct translation data of a property, a pair formed
    by the path of the parameters file name and the text itself in STLE1
    """

    def __init__(self, program_file_path, parameters_file_path):
        # Types: (program: str), (parameters_file_path: str)

        # Type: str
        self.program_file_path = program_file_path
        # Type: str
        self.parameters_file_path = parameters_file_path


class Translation:
    """
    This class stores the translation data originated from a program in SLe2
    """
    def __init__(self):
        # Description: List of STLe1Packs. Type: Array<Class STL1e1Pack>
        self.stle1_packs = []
        # Description: List of errors. Type: Array<str>
        self.errors = []

    def add_stle1_pack(self, stle1_pack):
        # Types: (stle1_pack: Class STL1e1Pack)

        self.stle1_packs.append(stle1_pack)

    def add_error(self, error):
        # Types: (error: str)

        self.errors.append(error)


class VariableContainer:
    def __init__(self, translation):
        self.translation = translation
        self.signal_ids = set()
        self.parameter_ids = set()
        self.parameter_translator = {}
        # Description: ID counter dictionary. Type: Dictionary<str->Integer>
        self.id_counter = {}

    def add_signal_id(self, _id):
        if _id in self.signal_ids or _id in self.parameter_ids:
            # Increase the counter
            self.id_counter[_id] += 1
        else:
            # Insert id into the dictionary
            self.id_counter[_id] = 1
            self.signal_ids.add(_id)

    def add_parameter_id(self, _id):
        if _id in self.signal_ids or _id in self.parameter_ids:
            # Increase the counter
            self.id_counter[_id] += 1
        else:
            # Insert id into the dictionary
            self.id_counter[_id] = 1
            self.parameter_translator[_id] = 'x'.join(str(len(self.parameter_ids)))
            self.parameter_ids.add(_id)

    def generate_errors(self):
        # Type: Array<Array<id: str, count: Integer>>
        duplicated_keys = []
        for _id in self.id_counter.keys():
            if self.id_counter[_id] > 1:
                duplicated_keys.append([_id, self.id_counter[_id]])

        for _id, count in duplicated_keys:
            self.translation.add_error('The id named ' + _id + ' is declared a total of '
                                       + count + ' times when only a maximum of 1 is allowed')


class Memory:
    """
    Auxiliary memory as a solution to poor class and interface design
    """

    def __init__(self):
        # Signal variables (probabilistic and common)
        self.signal_variables = set()

        # Type: (id_property : str, List<Parameter>)
        self.evaluations = []

        # To count how many variables has been declared
        self.components_counter = 0

        # To map components (signals) names into variable 'x<NUMBER' format
        self.components = {}

        # Properties dictionary
        self.properties = {}

        # Keep the name of the file of params that has to be return
        self.param_file_name = None

        # Indicates is the actual signal is probabilistic or not
        self.is_probabilistic_signal = False

        # Description: Dictionary of programs in tree form. Type: Dictionary<id_property : str -> stle1_program : list>
        self.stle1_programs = {}

        # Description: Sets of parameters. Type: set
        self.parameters_id = set()

        # Description: List of properties IDs. Type: list
        self.properties_ids = []

        # Dictionary of parameter translations
        self.parameters_id_translations = {}


def recursive_tree_print(tree):
    if isinstance(tree, (list, tuple)):
        string = ''
        for node in tree:
            string += recursive_tree_print(node)
        return string
    else:
        return str(tree) + ' '


def stle1_print(stle1_tree):
    # Types: (stle1_tree: Tree)

    # Type: str
    stle1_text = recursive_tree_print(stle1_tree)
    stle1_text = stle1_text.rstrip()
    return stle1_text


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


def translate_definitions(variable_container, definitions):
    # <DEFINITIONS> == (('SIGNAL_LIST', [...]), ('PROBSIGNAL_LIST', [...]), ('PARAM_LIST', [...]))
    for keyword, ids in definitions:
        if keyword == 'SIGNAL_LIST':
            # signal_variables == ["s1", "s2", ...]
            for _id in ids:
                variable_container.add_signal_id(_id)
        elif keyword == 'PROBSIGNAL_LIST':
            # prob_signal_variables == ["s1", "s2", ...]
            for _id in ids:
                variable_container.add_signal_id(_id)
        elif keyword == 'PARAM_LIST':
            # parameters == ["s1", "s2", ...]
            for _id in ids:
                variable_container.add_parameter_id(_id)

    variable_container.generate_errors()


class Parameter:
    def __init__(self, name):
        self.name = name

    def to_string(self):
        string = self.name
        if hasattr(self, 'below_limit'):
            string += ' ' + str(self.below_limit)
        if hasattr(self, 'upper_limit'):
            string += ' ' + str(self.upper_limit)
        return string


def list_to_string(_list):
    string = ''
    for element in _list:
        string += element.to_string() + '\n'
    string = string.rstrip()
    return string


def translate_prop_list(memory, stl_tree_property_list):
    """
        Function in charge of translating:

        <PROP_LIST> ::= ...

        :param memory: instance of class Memory
        :type memory: Memory
        :param stl_tree_property_list: Signal Temporal Logic Tree, it is a tree (data structure)
            where the data belonging to a temporal logic signal language have been standardized
        :type stl_tree_property_list: list
        :return: no
        """
    for stl_tree_property in stl_tree_property_list:
        generate_property(memory, stl_tree_property)
        property_id = stl_tree_property[1]
        memory.properties_ids.append(property_id)
        if stl_tree_property[2][0] == 'PHI':
            stle1_tree_formula = translate_phi(memory, stl_tree_property[2])
        else:
            stle1_tree_formula = translate_psi(memory, stl_tree_property[2])
        memory.properties[property_id] = stle1_tree_formula


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

    memory.stle1_programs[prop_id] = formula
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
    var_type = str(tree_com_lang[1]).lower()
    body = tree_com_lang[1]
    if var_type == 'variable':
        formula = generate_variable(memory, body)
    elif var_type == 'function':
        formula = generate_function(memory, body)
    elif var_type == 'sig':
        formula = tree_com_lang[2]
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
    elif var_type == 'global-interval':
        interval = tree_com_lang[2]
        phi = tree_com_lang[3]
        formula = generate_global_interval(memory, interval, phi)
    elif var_type == 'global':
        formula = generate_global(memory, body)
    elif var_type == 'until':
        formula = generate_u(memory, body)
    elif var_type == 'on':
        formula = generate_on(memory, body)
    else:
        formula = None
    return formula


def translate_bool_op(bool_op):
    return bool_op[1]


def generate_on(memory, on_phi):
    interval = translate_interval(on_phi[1])
    psi = translate_psi(memory, on_phi[2])
    return "(" + "ON" + " " + interval + " " + psi + ")"


# <EVAL_EXPR> ::= <EVAL> <ID> <ON> <ID_LIST> <WITH> <INTVL_LIST>
def translate_eval_list(memory, evaluation_expression_list):
    for evaluation_expression in evaluation_expression_list:
        _property = evaluation_expression[1]
        parameters_list = evaluation_expression[2]
        # Type: List<Parameter>
        class_parameters = []
        for tree_parameter in parameters_list:
            name = tree_parameter[1][1]
            class_parameter = Parameter(name)
            class_parameter.below_limit = tree_parameter[2][1]
            class_parameter.upper_limit = tree_parameter[2][2]
            class_parameters.append(class_parameter)
        memory.evaluations.append([_property, class_parameters])


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
def generate_interval(interval):
    return '({0} {1})'.format(interval[1], interval[2])


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
def generate_global(memory, phi):
    return '(G (0 inf) {0})'.format(translate_phi(memory, phi))

def generate_global_interval(memory, interval, phi):
    sol = '(G {0} {1})'.format(generate_interval(interval),
                               translate_phi(memory, phi))
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


def translate_spec_file(variable_container, memory, stl_tree):
    """
    Function in charge of translating:

    <SPEC_FILE> ::= <DEFINITIONS> <PROP_LIST> <EVAL_LIST>

    :param variable_container: Contains the IDs and generates errors for repeated IDs.
    :type variable_container: VariableContainer
    :param memory: instance of class Memory
    :type memory: Memory
    :param stl_tree: Signal Temporal Logic Tree, it is a tree (data structure) where the data belonging
            to a temporal logic signal language have been standardized
    :type stl_tree: list
    :return: None
    """

    assert stl_tree[0] == 'SPEC_FILE'

    # <DEFINITION> Node: tree_com_lang[1] == ('DEF', t[1])
    _, definitions = stl_tree[1]
    translate_definitions(variable_container, definitions)

    # <PROP_LIST>
    # tree_com_lang[2] == ('PROP_LIST', t[2])
    _, prop_list = stl_tree[2]
    translate_prop_list(memory, prop_list)

    # <EVAL_LIST>
    # tree_com_lang[3] == ('EVAL_LIST', t[3])
    _, eval_list = stl_tree[3]
    translate_eval_list(memory, eval_list)


def generate_plain_text_properties(memory):
    """
    Transforms all trees containing stle1 programs to plain text. Plain text programs are stored in the
    'memory' singleton instance and are mapped using the ID of the property that contained the program.
    Therefore, the trees are returned mapped to this same ID.

    :param memory: instance of class Memory
    :type memory: Memory
    :return: Dictionary(property_id : str -> plain_text_stle1_program : str)
    :rtype: dict
    """

    plain_text_stle1_program = {}
    for property_id in memory.properties_ids:
        # Type: list
        stle1_tree = memory.stle1_programs[property_id]
        # Type: str
        stle1_text = stle1_print(stle1_tree)
        plain_text_stle1_program[property_id] = stle1_text
    return plain_text_stle1_program


def generate_packs(memory, properties, translation):
    """
    Add all stle1 packs to 'translation'.
    Generates an error for each case of trying to evaluate a property not previously defined.

    :param memory: singleton instance of Memory class
    :type memory: Memory
    :param properties: Dictionary(property_id : str -> property_stle1_program : str)
    :type properties: dict
    :param translation: Singleton instance of Translation class
    :type translation: Translation
    :return: None
    """

    for evaluation in memory.evaluations:
        property_id = evaluation[0]
        try:
            stle1_text = properties.get(property_id)
            # Each property will be stored in a 'temporary.stl' file STL 1.0 format
            stle1_file_path = create_and_write_to_file(stle1_text)

            # Type: str
            parameters_file_path = None
            # Type: bool
            class_parameters = evaluation[1]
            is_parameterized = len(class_parameters) > 0
            if is_parameterized:
                # Type: List<Parameter>
                parameters = evaluation[1]
                parameters_file_path = create_and_write_to_file(list_to_string(parameters))

            # Type: STLe1Pack
            stle1_pack = STLe1Pack(stle1_file_path, parameters_file_path)
            translation.add_stle1_pack(stle1_pack)
        except KeyError:
            translation.add_error('The property ' + property_id + 'has not been defined')


def translate(stl_tree):
    """
    Translates a standardized Signal Temporal Logic (STL) tree into an instance of a Translation class.

    :param stl_tree: A standardized STL tree representing temporal logic signals.
        This tree is a data structure used to standardize temporal logic signal language data.
    :type stl_tree: list
    :return: An instance of the Translation class that stores the translated STLe1 data and any errors encountered.
    :rtype: Translation
    """

    translation = Translation()
    variable_container = VariableContainer(translation)
    memory = Memory()

    translate_spec_file(variable_container, memory, stl_tree)
    plain_text_properties = generate_plain_text_properties(memory)
    generate_packs(memory, plain_text_properties, translation)

    return translation
