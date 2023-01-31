
'''
Funciones

- Encargarse de que sale una variable una solo vez
- Asegurarse de que tengan sentido las expresiones
    - Si asignamos un valor Tipo1 (ej: Entero) un valor Tipo2 (ej: Boolean) será incorrecto.
- Contruir la string en lenguage STL
'''

class NameChecker :
    names = []
    def checkName(name) :
        for n in NameChecker.names :
            if n == name :
                return False
        return True
    def addName(name) :
        NameChecker.names.add(name);

# Diccionario de preposiciones atomicas
ap = {}

# STLCommand
def translate(tree) :
    string = buildString(tree)
    sol = generateFormula(string)
    return sol
def buildString(tree) :
    string = ""
    check(tree, string)
    return string
def check(nodo_actual, string) :
        if nodo_actual.left != None
            check(nodo_actual.left, string)
        string = string + nodo_actual.raiz;
        if nodo_actual.left != None
            check(nodo_actual.right, string)

# <NUMBER> ::= Floating-point number | inf | -inf
def generateNumber(string) :


# <BOOLEAN> ::= false | true
def generateBoolean(string) :

# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generateInterval(string) :

#<VARIABLE> ::= x<INTEGER>
def generateVariable(string) :


# <FORMULA> ::=
#     <VARIABLE>  |
#     <NUMBER>    |
#     <BOOLEAN>   |
#     (<FUNCTION> <FORMULA>*)   |
#     (F <INTERVAL> <FORMULA>)  |
#     (G <INTERVAL> <FORMULA>)  |
#     (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generateFormula(string) :
    formula = generateVariable(string)
    if formula is None :
        formula = generateNumber(string)
        if formula is None :
            formula = generateBoolean()
            if formula is None:
                formula = generateFunction()
                if formula is None:
                    formula = generateF()
                    if formula is None:
                        formula = generateG()
                        if formula is None:
                            formula = generateG()
    sol = '('
    sol += formula
    sol += ')'
    return sol

# (F <INTERVAL> <FORMULA>)
def generateF(string) :
    sol = '('
    sol += 'F'
    sol += generateInterval(string)
    sol += generateFormula(string)
    sol += ')'
    return sol
# (G <INTERVAL> <FORMULA>)
def generateG(string):
    sol = '('
    sol += 'G'
    sol += generateInterval(string)
    sol += generateFormula(string)
    sol += ')'
    return sol
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generateU(string):
    sol = '('
    sol += 'StlUntil'
    sol += generateInterval(string)
    sol += generateFormula(string)
    sol += generateFormula(string)
    sol += ')'
    return sol