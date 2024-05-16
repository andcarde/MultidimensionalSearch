# Directive
test_mode_active = True


class Printer:
    def __init__(self, name, father):
        self.name = name
        self.father = father
        self.subclasses = []
        pass

    def add_subclass(self, subclass):
        subclass_printer = Printer(subclass, self)
        self.subclasses.append(subclass_printer)
        return subclass_printer

    def generate_header(self):
        header = ''
        if self.name != 'init':
            actual_printer = self
            stack = []
            while actual_printer.name != 'init':
                stack.append(actual_printer.name)
                actual_printer = actual_printer.father
            for i in range(len(stack)):
                header += '[' + stack[len(stack) - 1 - i] + '] '
        return header

    def print(self, to_print):
        print(self.generate_header() + to_print)


if test_mode_active:
    initial_printer = Printer('init', None)
