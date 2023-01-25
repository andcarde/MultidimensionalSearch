
'''
Funciones

- Encargarse de que sale una variable una solo vez
- Asegurarse de que tengan sentido las expresiones
'''

class NameChecker {
    names = []
    def checkName(name) :
        for (n in names) :
            if (n == name)
                return false
        return true
    def addName(name) :
        names.add(name);
}

# Diccionario de preposiciones atomicas
ap = {}

# STLCommand
string;

def buildString(tree) :
    string = ""
    check(tree, string)
    return string
def check(nodo_actual, string) :
        if (nodo_actual.left != null)
            check(nodo_actual.left, string)
        string = string + nodo_actual.raiz;
        if (nodo_actual.left != null)
            check(nodo_actual.right, string)
