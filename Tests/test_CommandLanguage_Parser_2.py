from ParetoLib.CommandLanguage.Parser import parser


def manual_syntactic_test(data):
    """
    Video "LEX, YACC EN PYTHON" based test with https://www.youtube.com/watch?v=9fjtkTbHbO4 address

    :param data:
    :return:
    """

    for line in data.splitlines():
        if line:
            grammar = parser.parse(line)
            if not grammar:
                grammar = 'Empty Data'
            print("Result: ", grammar)


if __name__ == '__main__':
    while True:
        try:
            string = input(' enter data >>>')
        except EOFError:
            continue
        if not string:
            continue

        manual_syntactic_test(string)
