# Language.py

from typing import Union, List
import re


class BNFSyntaxError(SyntaxError):
    """Exception for syntax error in Backus–Naur form (BNF) Language."""
    pass


class InvalidCharacter(Exception):
    """Custom exception for disallowed characters."""
    pass


class Language:
    """
    Represents a language definition with its associated words and syntax rules.

    Attributes:
    word_types (Set[str]): A set of all word types in the language, including both constant and variable words.
    constant_words (Dict[str, str]): A dictionary mapping constant word identifiers to their definitions.
    variable_words (Dict[str, re.Pattern]): A dictionary mapping variable word identifiers to their regex patterns.
    sentence_types (Set[str]): A set of sentence types defined in the language.
    syntax_rules (Set[SyntaxRule]): A set of syntax rules, each represented by a SyntaxRule instance.
    """

    # :: Set[str]: Set of special characters
    SPECIAL_CHARACTERS = frozenset({':', '|', '[', ']', '?', '+', '*', '!'})

    def __init__(self, constant_words_block: str, variable_words_block: str, syntax_block: str):
        """
        Initializes the Language instance by parsing and building its components from the provided blocks.

        Args:
        constant_words_block (str): A string block defining constant words and their values.
        variable_words_block (str): A string block defining variable words and their regex patterns.
        syntax_block (str): A string block defining the syntax rules of the language.
        """
        # Initialize 'constant_words' dictionary and build from the provided block
        self.constant_words = self.build_words(constant_words_block)

        # Initialize 'variable_words' dictionary and build from the provided block
        self.variable_words = self.build_words(variable_words_block)

        # Verify if there are commons keys between both dictionaries
        common_keys = set(self.constant_words.keys()).intersection(self.variable_words.keys())
        if common_keys:
            raise BNFSyntaxError(f"The following word identifiers are defined in both constant and"
                                 + "variable words: {', '.join(common_keys)}")

        # Initialize 'word_types' with the keys of both dictionaries
        self.word_types = set(self.constant_words.keys()).union(self.variable_words.keys())

        # syntax_words_matrix (List[List[str]]): Parse syntax block to get a matrix of words
        syntax_words_matrix = self.parse_syntax(syntax_block)

        # DEBUG 1: Print syntax words matrix
        print('\nDEBUG 1: Print syntax words matrix (Language.py, line 60)\n')
        for i, line in enumerate(syntax_words_matrix):
            print(f'{i + 1}: {line}')

        # Build 'sentence_types' and 'syntax_rules' from the word matrix
        self.sentence_types, self.syntax_rules = self.build_syntax(syntax_words_matrix)

    @classmethod
    def parse_syntax(cls, syntax_block: str):
        """
        Parses the syntax block into a matrix of words, handling special characters and word definitions.

        Args:
        syntax_block (str): A string block representing the syntax rules.

        Returns:
        List[List[str]]: A matrix of words where each inner list represents a line of words from the block.
        """
        # :: List[str]: List of lines (block)
        lines = syntax_block.split('\n')
        # Strip leading and trailing whitespace from each line and remove empty lines
        lines = [line.strip() for line in lines if line.strip()]

        # :: List[List[str]]: List of lists of words (block)
        word_matrix = []

        for line in lines:
            # :: List[str]: List of characters (word)
            current_word = ''

            # If it is a comment, skip the line
            if line[0] == '#':
                continue

            # :: List[String]: List of words (line)
            words = []
            for char in line:
                # If it is a comment, skip the line
                if char == '#':
                    break
                # if 'char' is a name character
                elif char.isupper() and char.isalpha() or char == '_':
                    current_word += char
                else:
                    # If 'current_word' exists
                    if current_word:
                        # Save the word in the list
                        words.append(current_word)
                        # Erase the word
                        current_word = ''
                    if char in cls.SPECIAL_CHARACTERS:
                        # Save the character in the list
                        words.append(char)
                    elif char != ' ':
                        raise InvalidCharacter(f"The invalid character '{char}' has been found")
            if current_word:
                # Save the word in the list
                words.append(current_word)
            if words:
                # Save the characters list in the list of lists
                word_matrix.append(words)

        # :: List[List[str]]: Process the word matrix to handle syntax definitions
        processed_matrix = []

        # :: List[str]
        current_line = []
        for words in word_matrix:
            if len(words) > 1 and words[1] == ':':
                if current_line:
                    processed_matrix.append(current_line)
                # Save the current line
                current_line = words
            else:
                # Extend the current line
                current_line += words
        if current_line:
            processed_matrix.append(current_line)

        return processed_matrix

    @staticmethod
    def build_words(block: str):
        """
        Populates the provided dictionary with word definitions extracted from the given block of text.

        Args:
        block (str): A string block defining words and their associated values or patterns formatted as
        'identifier: value'.

        Returns:
        Dict[str, Union[str, re.Pattern]]: The updated dictionary containing all the word definitions.

        Raises:
        Exception: If a line is missing a definition or if a word identifier is already defined.
        """
        # :: (Dict[str, Union[str, re.Pattern]]): The dictionary to populate with word identifiers as keys and
        # their associated strings or regex patterns as values.
        dictionary = {}
        lines = block.split('\n')
        for line in lines:
            separator_index = line.find(': ')
            if separator_index == -1:
                if re.search(r'\S', line):
                    raise BNFSyntaxError(f'Line without definition (": ") not empty.\nLine: "{line}"')
            else:
                key = line[:separator_index]
                value = line[separator_index + 2:]
                if key in dictionary:
                    raise BNFSyntaxError(f"Word identifier '{key}' already defined")
                else:
                    dictionary[key] = value
        return dictionary

    def build_syntax(self, words: List[List[str]]):
        """
        Builds sentence types and syntax rules from the parsed word matrix.

        Args:
        words (List[List[str]]): A matrix of words representing syntax rules.

        Returns:
        Tuple[Set[str], List[SyntaxRule]]: A tuple containing a set of sentence types and a list of
        SyntaxRule instances.

        Raises:
        SyntaxError: For various syntax errors such as unexpected characters or missing elements.
        """

        # :: Set[String]: Types of the sentences on the language
        sentence_types = set()
        # :: List[SyntaxRule]
        syntax_rules = []
        # :: Set[String]: Types of the sentences that are referenced before being defined
        forward_definitions = set()

        for i, line_words in enumerate(words):
            if len(line_words) < 3:
                raise BNFSyntaxError('Syntax rules must have at least 3 words')
            elif line_words[0] in Language.SPECIAL_CHARACTERS:
                raise BNFSyntaxError(f"The special character '{line_words[0]}' is not expected")
            elif line_words[0] in sentence_types:
                raise BNFSyntaxError(f"The word '{line_words[0]}' is already defined")
            elif line_words[1] != ':':
                raise BNFSyntaxError("The colon (':') is missing")
            else:
                sentence_type = line_words[0]
                sentence_types.add(sentence_type)
                sentences = [Sentence()]

                formula = line_words[2:]
                j = 0
                while j < len(formula):
                    word = formula[j]
                    if word == '|':
                        sentences[-1].add_or()
                    elif word == '[':
                        sentence = Sentence()
                        sentences.append(sentence)
                    elif word == ']':
                        if len(sentences) == 1:
                            raise SyntaxError('A right bracket is not expected')
                        else:
                            closed_sentence = sentences.pop()
                            if j + 1 < len(formula):
                                next_word = formula[j + 1]
                                if next_word in Sentence.CARDINALITY_CHARACTERS:
                                    closed_sentence.set_cardinality(next_word)
                                    j += 1
                            if closed_sentence.is_empty():
                                raise BNFSyntaxError(
                                    "Empty brackets ('[]') and empty content between '|' and ']' are not allowed")
                            elif closed_sentence.has_single_nested_sentence():
                                raise BNFSyntaxError("Nested brackets with a single element ('[[...]]')"
                                                     " are not allowed")
                            else:
                                sentences[-1].add_element(closed_sentence)
                    elif word == ':':
                        raise BNFSyntaxError("A colon (':') is not expected")
                    elif word == '!':
                        raise BNFSyntaxError("An exclamation mark ('!') is not expected")
                    elif word in Sentence.CARDINALITY_CHARACTERS:
                        raise BNFSyntaxError(f"The cardinality character '{word}' is not expected"
                                             f" at position {j + 3} in line {i + 1}")
                    elif word not in sentence_types | self.word_types:
                        if j + 1 < len(formula) and formula[j + 1] == '!':
                            forward_definitions.add(word)
                            j += 1
                        else:
                            raise BNFSyntaxError(f"The word '{word}' is used but not defined")
                    else:
                        sentences[-1].add_element(word)
                    j += 1

                if len(sentences) > 1:
                    raise BNFSyntaxError('A right bracket is missing')
                else:
                    main_sentence = sentences.pop()
                    syntax_rules.append(SyntaxRule(sentence_type, main_sentence))

        # :: Set[String]
        undefined_types = forward_definitions - sentence_types
        if undefined_types:
            raise BNFSyntaxError(f"There are sentence types that are referenced but never defined: "
                                 f"{', '.join(undefined_types)}")

        return sentence_types, syntax_rules

    def to_string(self):
        """
        Converts the language definition to a string representation.

        Returns:
        str: A string representation of the constant words, variable words, and syntax rules.
        """
        block = Block('· Constant words')
        for key in self.constant_words:
            block.append(f'{key}: {self.constant_words[key]}')
        block.append('\n· Variable words')
        for key in self.variable_words:
            block.append(f'{key}: {self.variable_words[key]}')
        block.append('\n· Syntax rules')
        for syntax_rule in self.syntax_rules:
            block.append(syntax_rule.to_string())
        return block.content


class Block:
    """
    Represents a block of text content.

    Attributes:
    content (str): The string that makes up the block.
    """

    def __init__(self, first_line: str):
        """
        Store the content in a private attribute
        """
        self._content = first_line

    def append(self, line: str):
        """
        Modify the content stored in the private attribute
        """
        self._content += '\n' + line

    @property
    def content(self):
        """
        Getter to access the content
        """
        return self._content


class Sentence:
    """
    Represents a sentence structure with optional cardinality and alternative constructions.

    Attributes:
    or_constructions (List[Union[str, 'Sentence']]): A list where each element is either a string belonging to
        Language.instance.word or another Sentence object.
    cardinality (str): Represents the cardinality of the sentence. The possible values are:
        - '?' for [0, 1]
        - '*' for [0, N]
        - '+' for [1, N]
    """

    # :: Set[str]: Set of cardinality characters
    CARDINALITY_CHARACTERS = {'?', '+', '*'}

    def __init__(self):
        # Initialize with a list containing an empty list for the first construction
        self.or_constructions = [[]]
        self.cardinality = None  # Cardinality is initially not set

    def set_cardinality(self, cardinality: str):
        """Set the cardinality of the sentence."""
        if cardinality not in Sentence.CARDINALITY_CHARACTERS:
            raise BNFSyntaxError(f"The word '{cardinality}' not represents cardinality")
        else:
            self.cardinality = cardinality

    def add_element(self, element: Union[str, 'Sentence']):
        """Add an element (string or nested Sentence) to the current construction."""
        self.or_constructions[-1].append(element)

    def add_or(self):
        """Add a new 'or' construction. Raises an error if the current construction is empty."""
        if len(self.or_constructions[-1]) == 0:
            raise BNFSyntaxError("An element must precede the 'or' operator ('|')")
        else:
            self.or_constructions.append([])

    def is_empty(self):
        """Check if the current construction is empty."""
        return len(self.or_constructions[-1]) == 0

    def has_single_nested_sentence(self):
        """
        Check if there is a single nested Sentence within the current construction.

        Returns:
        bool: True if there is exactly one Sentence object in the first construction, False otherwise.
        """
        return len(self.or_constructions) == 1 and len(
            self.or_constructions[0]) == 1 and isinstance(self.or_constructions[0][0], Sentence)

    def to_string(self):
        """
        Convert the sentence structure to a string representation.

        Returns:
        str: The string representation of the sentence.
        """
        # Start with the cardinality and opening parenthesis
        string = ''
        if self.cardinality:
            string += self.cardinality
        string += '('

        for i, construction in enumerate(self.or_constructions):
            if i > 0:
                string += ' | '
            for element in construction:
                if isinstance(element, str):
                    string += element
                # element :: Sentence
                else:
                    # Recursively call to_string() for nested Sentence objects
                    string += element.to_string()
        string += ')'
        return string


class SyntaxRule:
    """
    Represents a syntax rule in the language definition.

    Attributes:
    defined_word (str): The defined word in the language, which is a valid word according to Language.instance.word.
    main_sentence (Sentence): The main sentence associated with this syntax rule, represented as an instance of the
    Sentence class.

    Methods:
    to_string() -> str:
        Returns a string representation of the syntax rule in the format '{defined_word}: {main_sentence_string}'.
    """

    def __init__(self, defined_word: str, main_sentence: 'Sentence'):
        """
        Initializes a SyntaxRule instance.

        Args:
        defined_word (str): The string representing the defined word, which must be a valid word according to
        Language.instance.word.
        main_sentence (Sentence): An instance of the Sentence class representing the main sentence associated with
        the syntax rule.
        """
        self.defined_word = defined_word
        self.main_sentence = main_sentence

    def to_string(self) -> str:
        """
        Converts the syntax rule to a string representation.

        Returns:
        str: A string representation of the syntax rule in the format '{defined_word}: {main_sentence_string}'.
        """
        return f'{self.defined_word}: {self.main_sentence.to_string()}'
