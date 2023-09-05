# <FileUtils.py>
# Exports: create_and_write_to_file, read_file functions
import tempfile


def create_and_write_to_file(text):
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as file:
        file.write(text + '\n')
        return file.name


def read_file(file_name):
    with open(file_name, 'r') as file:
        text = file.read()
        return text
