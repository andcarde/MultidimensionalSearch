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


class NoTypeException(Exception):
    def __init__(self, _type, function):
        super().__init__('The type {0} has not been detected in {1}.'.format(_type, function))


class UndeclaredIDException(Exception):
    def __init__(self, _id):
        super().__init__('The id \'{0}\' has not been declared.'.format(_id))


class VariableContainer:
    def __init__(self, translation):
        self.translation = translation
        self.signal_ids = set()
        self.parameter_ids = set()
        self.signal_translator = dict()
        # Description: ID counter dictionary. Type: Dictionary<str->Integer>
        self.id_counter = {}

    def add_signal_id(self, _id):
        if _id in self.signal_ids or _id in self.parameter_ids:
            # Increase the counter
            self.id_counter[_id] += 1
        else:
            # Insert id into the dictionary
            self.id_counter[_id] = 1
            index = str(len(self.signal_ids))
            self.signal_ids.add(_id)
            self.signal_translator[_id] = 'x' + index

    def add_parameter_id(self, _id):
        if _id in self.signal_ids or _id in self.parameter_ids:
            # Increase the counter
            self.id_counter[_id] += 1
        else:
            # Insert id into the dictionary
            self.id_counter[_id] = 1
            self.parameter_ids.add(_id)

    def translate_signal(self, key):
        return self.signal_translator[key]

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
            # signal_variables == ['s1', 's2', ...]
            for _id in ids:
                variable_container.add_signal_id(_id)
        elif keyword == 'PROBSIGNAL_LIST':
            # prob_signal_variables == ['s1', 's2', ...]
            for _id in ids:
                variable_container.add_signal_id(_id)
        elif keyword == 'PARAM_LIST':
            # parameters == ['s1', 's2', ...]
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


def translate_prop_list(memory, variable_container, stl_tree_property_list):
    """
        Function in charge of translating:

        <PROP_LIST> ::= ...

        :param memory: instance of class Memory
        :type memory: Memory
        :param variable_container: instance of class VariableContainer
        :type variable_container: VariableContainer
        :param stl_tree_property_list: Signal Temporal Logic Tree, it is a tree (data structure)
            where the data belonging to a temporal logic signal language have been standardized
        :type stl_tree_property_list: list
        :return: no
    """
    for stl_tree_property in stl_tree_property_list:
        property_id = stl_tree_property[1]
        memory.properties_ids.append(property_id)
        if stl_tree_property[2][0] == 'PSI':
            stle1_tree_formula = translate_psi(memory, variable_container, stl_tree_property[2][1])
        else:
            stle1_tree_formula = translate_phi(memory, variable_container, stl_tree_property[2])
        memory.stle1_programs[property_id] = stle1_tree_formula


# Input: treeSTLE (tuple)
#     (<VARIABLE>, )  |
#     (<NUMBER>, )    |
#     (<BOOLEAN>, )   |
#     (<FUNCTION> <FORMULA>*)   |
#     (F, <INTERVAL>, <FORMULA>)  |
#     (G, <INTERVAL>, <FORMULA>)  |
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


# Information required in translate_phi(memory, variable_container, phi):
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


def translate_phi(memory, variable_container, phi):
    var_type = str(phi[0]).lower()
    if var_type == 'function':
        formula = translate_function(variable_container, memory, phi[1])
    elif var_type == 'constant_signal':
        formula = phi[1]
    elif var_type == 'variable_signal':
        formula = translate_variable_signal(variable_container, memory, phi[1])
    elif var_type == "id":
        my_id = translate_variable_signal(variable_container, memory, phi[1])
        formula = memory.properties[my_id]
    elif var_type == 'not':
        formula = 'not '.join(translate_phi(memory, variable_container, phi[1]))
    elif var_type == 'prob':
        formula = translate_prob(memory, variable_container, phi[1])
    elif var_type == 'number':
        formula = str(phi[1])
    elif var_type == 'future':
        formula = translate_future(memory, variable_container, phi[1])
    elif var_type == 'future-interval':
        formula = translate_future_interval(memory, variable_container, phi[1])
    elif var_type == 'global-interval':
        formula = translate_global_interval(memory, variable_container, phi[1])
    elif var_type == 'global':
        formula = translate_global(memory, variable_container, phi[1])
    elif var_type == 'until':
        formula = translate_until(memory, variable_container, phi[1])
    elif var_type == 'until-interval':
        formula = translate_until_interval(memory, variable_container, phi[1])
    elif var_type == 'on':
        formula = translate_on(memory, variable_container, phi[1])
    else:
        raise NoTypeException(var_type, 'translate_phi')
    return formula


def translate_prob(memory, variable_container, phi):
    formula = translate_phi(memory, variable_container, phi)
    return formula


def translate_variable_signal(variable_container, memory, variable_signal):
    return translate_id(variable_container, memory, variable_signal)


def translate_id(variable_container, memory, _id):
    print('DEBUG -- Translation.translate_variable_signal -- {0} (id)'.format(_id))
    if _id in variable_container.parameter_ids:
        return _id
    elif _id in memory.properties_ids:
        return memory.stle1_programs[_id]
    elif _id in variable_container.signal_translator:
        return variable_container.signal_translator[_id]
    else:
        raise UndeclaredIDException(_id)


def translate_on(memory, variable_container, on):
    interval = translate_interval(on[0])
    psi = translate_psi(memory, variable_container, on[1])
    stle1_expression = '( On {0} {1} )'.format(interval, psi)
    return stle1_expression


'''
<PSI> : <MIN> <PHI>
    | <MAX> <PHI>
    | <INT> <PHI>
    | <DER> <PHI>
'''


def translate_psi(memory, variable_container, psi):
    # psi == (<OP>, <PHI>)
    stle2_operator, phi = psi
    stle1_operator = translate_operator(stle2_operator)
    formula = '( {0} {1} )'.format(stle1_operator, translate_phi(memory, variable_container, phi))
    return formula


def translate_operator(stle2_op):
    stle1_operator_map = {
        'Min': 'min',
        'Max': 'Max',
        'Der': 'D',
        'Int': 'I'
    }
    stle1_operator = stle1_operator_map[stle2_op]
    return stle1_operator


# <BOOLEAN> ::= false | true
def translate_boolean(tree_com_lang):
    if tree_com_lang[0]:
        return 'true'
    else:
        return 'false'


# <NUMBER> ::= Floating-point number | inf | -inf
# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def translate_interval(interval):
    return '( {0} {1} )'.format(interval[1], interval[2])


# <VARIABLE> ::= x<INTEGER>
def translate_variable(memory, variable):
    integer = variable[1]
    # To map variable names into variable 'x<NUMBER' format
    memory.signal_variable_counter += 1
    memory.signal_variables[integer] = memory.signal_variable_counter
    return 'x' + str(memory.signal_variable_counter)


# ('PHI', 'function', (symbol, signal1  signal2))
# (<FUNCTION> <FORMULA>*)
def translate_function(variable_container, memory, function):
    symbol = function[0]
    print('DEBUG -- Translator.translate_function -- {0} (symbol)'.format(function))
    signal1 = function[1]
    print('DEBUG -- Translator.translate_function -- {0} (signal2)'.format(function))
    signal2 = function[2]
    print('DEBUG -- Translator.translate_function -- {0} (signal)'.format(function))
    stle1_expression = '( {0} {1} {2} )'.format(symbol,
                                                translate_phi(memory, variable_container, signal1),
                                                translate_phi(memory, variable_container, signal2))
    return stle1_expression


# until = (('PHI', 'until', phi, phi)
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def translate_until(memory, variable_container, until):
    phi1 = until[0]
    phi2 = until[1]
    stle1_expression = '( StlUntil ( 0 inf ) {0} {1} )'.format(translate_phi(memory, variable_container, phi1),
                                                               translate_phi(memory, variable_container, phi2))
    return stle1_expression


# until_interval = ('PHI', 'until-interval', interval, psi, psi)
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def translate_until_interval(memory, variable_container, until_interval):
    interval = until_interval[0]
    phi1 = until_interval[1]
    phi2 = until_interval[2]
    stle1_expression = '( StlUntil {0} {1} {2} )'.format(translate_interval(interval),
                                                         translate_phi(memory, variable_container, phi1),
                                                         translate_phi(memory, variable_container, phi2))
    return stle1_expression


# future = ('PHI', 'future', phi)
# (F <INTERVAL> <FORMULA>)
def translate_future(memory, variable_container, future):
    phi = future
    stle1_expression = '(F (0 inf) {0})'.format(translate_phi(memory, variable_container, phi))
    return stle1_expression


# future_interval = ('PHI', 'future-interval', interval, phi)
# (F <INTERVAL> <FORMULA>)
def translate_future_interval(memory, variable_container, future_interval):
    interval = future_interval[0]
    phi = future_interval[1]
    stle1_expression = '(F {0} {1})'.format(translate_interval(interval),
                                            translate_phi(memory, variable_container, phi))
    return stle1_expression


# (G <INTERVAL> <FORMULA>)
# ('PHI', 'global', _global)
def translate_global(memory, variable_container, _global):
    phi = _global
    return '(G (0 inf) {0})'.format(translate_phi(memory, variable_container, phi))


# ('PHI', 'global', interval, _global)
# (G <INTERVAL> <FORMULA>)
def translate_global_interval(memory, variable_container, global_interval):
    interval = global_interval[0]
    phi = global_interval[1]
    stle1_expression = 'G {0} {1}'.format(translate_interval(interval),
                                          translate_phi(memory, variable_container, phi))
    return stle1_expression


def translate_eval_list(memory, evaluation_expression_list):
    """
    <EVAL_EXPR> ::= <EVAL> <ID> <ON> <ID_LIST> <WITH> <INTVL_LIST>
    :param memory:
    :param evaluation_expression_list:
    :return:
    """
    for evaluation_expression in evaluation_expression_list:
        _property = evaluation_expression[1]
        if _property not in memory.properties_ids:
            raise NoTypeException(_property)
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
    translate_prop_list(memory, variable_container, prop_list)

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
