
"""
--- Tests / Language ---
El modulo Tests/Language es un visualizador de árboles (estructuras de datos). Su utilidad en este proyecto es la de
comprobar la correcta traducción entre los lenguajes STLE1 y STLE3 (aplicación de STLE2).

--- tree.py ---
Desacopla a la estructura de datos del test de la lectura del árbol y de la gui
"""


class TreeNode:
    def __init__(self, data):
        # Nombre del nodo
        self.data = data
        # Lista para almacenar los nodos hijos
        self.children = []
    def to_string(self):
        string = self.data
        if len(self.children) > 0:
            string += " " + "[" + " "
            for child in self.children:
                string += child.to_string()
                if child is not self.children[len(self.children) - 1]:
                    string += ", "
            string += " " + "]"


def read_word(texto, index):
    while index < len(texto) and texto[index] == " ":
        index += 1
    word = ""
    while index < len(texto) and texto[index] != " ":
        word = word + texto[index]
        index += 1
    return word, index


# Función auxiliar para construir el árbol recursivamente
def build_tree(data, texto, index):
    # Crear el nodo actual
    node = TreeNode(data)

    # Leer la siguiente palabra
    word, index = read_word(texto, index)

    # Comprobamos si es un nodo hoja o un nodo nudo
    if word != "[":
        return node, index, word
    else:
        # Recorrer el texto para construir los nodos hijos
        while index < len(texto):
            if word == "[":
                word, index = read_word(texto, index)
            elif word == "]":
                # Fin del nodo actual
                return node, index, None
            else:
                # Crear un nodo hijo
                child, index, next_word = build_tree(word, texto, index)
                node.children.append(child)
                if next_word is None:
                    word, index = read_word(texto, index)

        return node, index, None


def create_tree(texto):
    # Intercambiar saltos de línea por espacios en blanco
    texto = texto.replace("\n", " ")

    index = 0
    word, index = read_word(texto, index)

    # Llamar a la función auxiliar para construir el árbol
    root, _, _ = build_tree(word, texto, index)

    return root
