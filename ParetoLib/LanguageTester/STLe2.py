
# STLe2.py

import os

from ParetoLib.LanguageTester.Language import Language


class FileReadError(Exception):
    """Custom exception for file read errors."""
    pass


def read(file_path):
    try:
        # Open the file in read mode
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read the file
            content = file.read()
        return content
    except (IOError, OSError):
        raise FileReadError(f"The file in the path '{file_path}' could not be read.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: The file in the path '{file_path}' has not been found.")


class MissingCommand(Exception):
    """Custom exception for missing commands."""
    pass


def extract(content, command):
    # Find the initial position of the command
    init = content.find('>>> ' + command)
    if init == -1:
        raise (MissingCommand(f"The command '{command}' is missing"))
    # Find the newline after the command
    init = content.find('\n', init)
    if init == -1:
        raise (MissingCommand(f"There is no newline after the '{command}' command."))
    # Find the position of the 'end' keyword after the newline
    end = content.find('>>> end', init)
    if end == -1:
        raise (MissingCommand(f"There is no 'end' after the '{command}' command."))
    # Extract the text block from the newline to the 'end' keyword
    block = content[init:end].strip()
    return block


def extract_bnf(bnf_block):
    constant_words_block = extract(bnf_block, 'bnf.variables')
    variable_words_block = extract(bnf_block, 'bnf.constants')
    syntax_block = extract(bnf_block, 'bnf.syntax')
    return constant_words_block, variable_words_block, syntax_block


def main():
    # try:
    # Example: STLe2 charge
    meta_path = os.getcwd()
    file_name = 'stle2_grammar.txt'
    content = read(os.path.join(meta_path, file_name))
    stle2 = Language(*extract_bnf(content))
    # DEBUG 2: Print STLe2 language
    print('\nDEBUG 2: Print STLe2 language (STLe2.py, line 65)\n')
    print(stle2.to_string())
    '''
    except SyntaxError as se:
        print(f'[Syntax Error] {str(se)}')
    except Exception as e:
        print(f"An unknown exception has been launched: '{str(e)}'")
    '''


if __name__ == "__main__":
    main()
