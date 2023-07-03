
"""
--- Tests / Language ---
El modulo Tests/Language es un visualizador de árboles (estructuras de datos). Su utilidad en este proyecto es la de
comprobar la correcta traducción entre los lenguajes STLE1 y STLE3 (aplicación de STLE2).

--- launcher.py ---
Desacopla a los árboles de test de la vista como tal.
"""

from enum import Enum
from gui import init_gui
from tree import create_tree


def get_file_path():
    class File(Enum):
        STLE1Ex1 = "STLE1Ex1"
        STLE1Ex2 = "STLE1Ex2"
        STLE1Ex3 = "STLE1Ex3"
        STLE3Ex1 = "STLE3Ex1"
        STLE3Ex2 = "STLE1Ex2"
        STLE3Ex3 = "STLE3Ex3"

    # Parámetros de configuración manual del test
    file = File.STLE3Ex1

    import os

    # Obtener la ruta absoluta de la carpeta raíz de Tests
    root_path = os.path.abspath("..")

    # Crear la ruta completa del archivo
    file_path = os.path.join(root_path, "Language", "examples", file._value_ + ".txt")

    return file_path


def main():
    file_path = get_file_path()
    with open(file_path, "r") as file:
        texto = file.read()
    tree = create_tree(texto)
    print(tree.to_string())
    init_gui(tree)


if __name__ == "__main__":
    main()
