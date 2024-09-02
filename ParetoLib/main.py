
# <main.py>

import sys

DEBUG_MODE = False

if __name__ == '__main__':
    print(sys.argv[1])
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        DEBUG_MODE = True
        print(DEBUG_MODE)
    else:
        DEBUG_MODE = False
    import ParetoLib.GUI.GUI
    ParetoLib.GUI.GUI.execute_gui()
