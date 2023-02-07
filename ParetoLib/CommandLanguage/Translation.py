import numpy

'''
Funciones
- Se traducirá el lenguaje CPN a STLE
- Encargarse de que sale una variable una solo vez
- Asegurarse de que tengan sentido las expresiones
    - Si asignamos un valor Tipo1 (ej: Entero) un valor Tipo2 (ej: Boolean) será incorrecto.
- Contruir la string en lenguage STL
'''


class NameChecker:
    names = []

    def checkName(name):
        for n in NameChecker.names:
            if n == name:
                return False
        return True

    def addName(name):
        NameChecker.names.add(name);


# Diccionario de preposiciones atomicas
ap = {}


# STLCommand
def translate(cpnTree):
    stleTree
    tipoVar = cpnTree[0]
    # Igual no hay switch en Python
    if tipoVar == max:
        stleTree = generateNumber(cpnTree)
    elif tipoVar == 'min':
        stleTree = generateFormula(cpnTree)
    stleFormula = generateFormula(stleTree)
    return stleFormula


def buildString(tree):
    string = ""
    check(tree, string)
    return string


def check(nodo_actual, string):
    if nodo_actual.left != None:
        check(nodo_actual.left, string)
    string = string + nodo_actual.raiz;
    if nodo_actual.left != None:
        check(nodo_actual.right, string)


# <NUMBER> ::= Floating-point number | inf | -inf
def generateNumber(string):


# <BOOLEAN> ::= false | true
def generateBoolean(string):


# <INTERVAL> ::= (<NUMBER> <NUMBER>)
def generateInterval(string):


# <VARIABLE> ::= x<INTEGER>
def generateVariable(string):


# Input: treeSTLE (tuple)
#     (<VARIABLE>, )  |
#     (<NUMBER>, )    |
#     (<BOOLEAN>, )   |
#     (<FUNCTION> <FORMULA>*)   |
#     (F, <INTERVAL>, <FORMULA>)  |
#     (G, <INTERVAL>, <FORMULA>)"  |
#     (UNTIL, <INTERVAL>, <FORMULA>, <FORMULA>)

# Output: (str)
# <FORMULA> ::=
#     <VARIABLE>  |
#     <NUMBER>    |
#     <BOOLEAN>   |
#     (<FUNCTION> <FORMULA>*)   |
#     "(F <INTERVAL> <FORMULA>)"  |
#     "(G <INTERVAL> <FORMULA>)"  |
#     "(StlUntil <INTERVAL> <FORMULA> <FORMULA>)"

def generate_formula(tree_stle: tuple) -> str:
    string = ''
    if len(tree_stle) == 1:
        string = "{0}".format(tree_stle[0])
    elif len(tree_stle) == 3:
        "[a, b], a <= b"
        op, intv, form = tree_stle
        string = "({0} {1} {2})".format(op, intv, form)
    elif len(tree_stle) == 4:
        op, intv, form1, form2 = tree_stle
        string = "({0} {1} {2} {3})".format(op, intv, form1, form2)
    else:
        # (<FUNCTION> <FORMULA>*)

    return string


#########################################
    formula = generateVariable(string)
    if formula is None:
        formula = generateNumber(string)
        if formula is None:
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
def generateF(string):
    sol = '('
    sol += 'F'
    sol += generateInterval(string)
    sol += generateFormula(string)
    sol += ')'
    return sol


# (G <INTERVAL> <FORMULA>)
def generateG(treeCPN):
    sol = '('
    sol += 'G'
    sol += generateInterval(string)
    sol += generateFormula(string)
    sol += ')'
    return sol


# Precondition: treeCPN := treeCPN[0]='F', treeCPN[1]=<TreeInterval>;
# <TreeInterval> := <TreeInterval>[0]=INTERVAL, <TreeInterval>[1] = <name>, <TreeInterval>[2] = <name>
# stringCPN: 'F[<value>,<value>]', <value> = <name> | <integer>, <name> = r{[a-zA-Z][a-zA-Z]*[0-9]*}, <integer> = r{[0-9]+}
# (StlUntil <INTERVAL> <FORMULA> <FORMULA>)
def generateU(treeCPN):
    treeSTLE = '('
    treeSTLE += 'StlUntil'
    treeSTLE += generateInterval(treeCPN)
    treeSTLE += generateFormula(treeCPN)
    treeSTLE += generateFormula(treeCPN)
    treeSTLE += ')'
    return treeSTLE


'''
PARAM: let param PARAM_LIST
SIGNAL: let signal SIGNAL_LIST
PROBSIGNAL: let probabilistic signal PROBSIGNAL_LIST

PARAM_LIST: ID_LIST;
SIGNAL_LIST: ID_LIST;
PROBSIGNAL_LIST: ID_LIST;

ID_LIST: ID |
		ID, ID_LIST

INTVL: LBRACKET NUMBER COMMA NUMBER RBRACKET
INTVL_LIST: ID in INTVL |
		ID in INTVL, INTVL_LIST

PROP: ID := PHI | PSI

SIG: ID | CONSTANT_SIGNAL
CONSTANT_SIGNAL: NUMBER

FUNC: SIG BIN_COND SIG | SIG BIN_OP SIG
PHI : ID | FUNC | NOT PHI | PROB PHI | PHI BIN_BOOL_OP PHI | F[INTVL]? PHI | G[INTVL]? PHI | PHI U[INTVL]? PHI | ON[INTVL] PSI | LPAR PHI RPAR
PSI : MIN PHI | MAX PHI | INTEGRAL PHI | DER PHI

EVAL: eval ID on SIGNAL_LIST with INTVL_LIST

SPEC_FILE:
	[DEF_SIGNAL | DEF_PROBSIGNAL]?
	[DEF_PARAM]?
	[PROP]+
	[EVAL]+

? = 0, 1
+ = 1...N
* = 0...N
'''
