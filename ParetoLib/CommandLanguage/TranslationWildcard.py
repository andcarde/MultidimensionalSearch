# <TranslationWilcard.py>
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


def translate(stl_tree):
    """
    Translates a standardized Signal Temporal Logic (STL) tree into an instance of a Translation class.

    :param stl_tree: A standardized STL tree representing temporal logic signals.
        This tree is a data structure used to standardize temporal logic signal language data.
    :type stl_tree: list
    :return: An instance of the Translation class that stores the translated STLe1 data and any errors encountered.
    :rtype: Translation
    """

    # Test numbering: 1 to 3
    wildcard_enum = 1

    if wildcard_enum == 1:
        translation = create_translation_wildcard1()
    elif wildcard_enum == 2:
        translation = create_translation_wildcard2()
    else:
        translation = create_translation_wildcard3()
    return translation


def create_translation_wildcard1():
    translation = Translation()
    translation.errors = [
        'The variable s1 has been declared 3 times'
        'The interval [9, 8] is not allowed since it must contain at least one point'
    ]
    translation.stle1_packs = []
    return translation


def create_translation_wildcard2():
    translation = Translation()
    translation.errors = []

    program = '( Max ( F ( 0 p2 ) ( - ( < x1 p1 ) 10 ) ) )'
    parameters = 'p1 1 2' + '\n' + 'p2'

    program_file_path = create_and_write_to_file(program)
    parameters_file_path = create_and_write_to_file(parameters)

    translation.stle1_packs = [
        STLe1Pack(program_file_path, parameters_file_path)
    ]
    return translation


def create_translation_wildcard3():
    translation = Translation()
    translation.errors = []

    program1 = '( - ( < x1 p1 ) 10 )'
    parameters1 = 'p1 1 2'
    program2 = '( Max ( F ( 0 p2 ) ( - ( < x1 p1 ) 10 ) ) )'
    parameters2 = 'p1 1 2' + '\n' + 'p2'

    program_file_path1 = create_and_write_to_file(program1)
    parameters_file_path1 = create_and_write_to_file(parameters1)
    program_file_path2 = create_and_write_to_file(program2)
    parameters_file_path2 = create_and_write_to_file(parameters2)

    translation.stle1_packs = [
        STLe1Pack(program_file_path1, parameters_file_path1),
        STLe1Pack(program_file_path2, parameters_file_path2)
    ]
    return translation
