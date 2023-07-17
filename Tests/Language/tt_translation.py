
from ParetoLib.CommandLanguage.Parser import parser
from ParetoLib.CommandLanguage.Translation import translate

# Alojamos cada test junto con su salida

# Mapa [archivo STLE1] ->[archivo STLE2]
tests = []

# Test 1
class Test:
   def __init__(self, stle2, param, stle1):
      self.stle2 = stle2
      self.param = param
      self.stle1 = stle1
   def to_test(self, translate):
      sol_param, sol_stle1 = translate(stle2)
      correcto = True
      if sol_param != self.param:
         fallo = False
         print("Test nº" + self.id + " fallido.")
         print("param_deseado: \n" + self.param)
         print("param_obtenido: \n" + sol_param)
      if sol_stle1 != self.stle1:
         if (correcto):
            print("Test nº" + self.id + " fallido.")
         print("param_deseado: \n" + self.param)
         print("param_obtenido: \n" + sol_param)

# Test 1 -- STLE2
stle2 = "let param p1, p2;" + "\n"
+ "let signal s1;" + "\n"
+ "prop1 := G [8, 12] p1 and p2" + "\n"
+ "eval prop1 with p1 in [5, 8], p2 with [7, inf]"

# Test 1 -- STLE1
param = "p1 5 8" + "/n"
"p2 7"
stle1 = "G ( 8 12 ) ( and p1 p2 )"

def total_translation(stle2):
   stle2_tree = parser.parse(stle2)

# Ejecuta el conjunto de tests de traducción
def test_translation():
   for test in tests:
      test.to_test(total_translation)

### tt_translation.py EXECUTE
test_translation()
