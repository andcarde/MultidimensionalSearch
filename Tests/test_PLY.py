

# Prueba basada en el vídeo "LEX, YACC EN PYTHON"
# con dirección https://www.youtube.com/watch?v=9fjtkTbHbO4

from ParetoLib.CommandLanguage.Parser import parser
from ply.yacc import yacc

# instanciamos el analizador sintactico
parser = yacc.yacc()

def prueba_sintactica(data):
    global resultado_gramatica
    resultado_gramatica.clear()

    for item in data.splitlines():
        if item:
            gram = parser.parse(item)
            if gram:
                resultado_gramatica.append(str(gram))
            else: print("data vacia")

        print("result: ", resultado_gramatica)

if __name__ == '__main__':
    while True:
        try:
            s = input(' ingresa dato >>>')
        except EOFError:
            continue
        if not s: continue

        prueba_sintactica(s)