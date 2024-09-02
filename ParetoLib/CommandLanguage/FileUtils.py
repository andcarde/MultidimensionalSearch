"""
<FileUtils.py>
Exports: create_and_write_to_file, read_file, create_empty_file functions
"""

import tempfile


def create_and_write_to_file(text: str):
    """
    Parameters:
        text :: str

    Returns:
        text :: str
    """
    # file: Union[_TemporaryFileWrapper, _TemporaryFileWrapper[str]]
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as file:
        if text is None:
            text = ''
        file.write(text + '\n')
        # :: str
        filepath = file.name
        return filepath


def read_file(filepath: str):
    """
    Parameters:
        filepath :: str

    Returns:
        text :: str
    """
    with open(filepath, 'r') as file:
        # :: str
        text = file.read()
        text = text.rstrip('\n\r\t ')
        return text


def create_empty_file():
    """
    Returns:
        filepath :: str
    """
    # :: _TemporaryFileWrapper
    file = tempfile.NamedTemporaryFile(delete=False)
    file.close()
    # :: str
    filepath = file.name
    return filepath
