symbols = {'<': 'lt', '>': 'gt', '"': '&quot;', '&': 'and', '-': 'neg', '+': 'add', '~': 'not',
           '=': 'eq', '|': 'or', '*': 'call Math.multiply 2', '/': 'call Math.divide 2'}


class VMWriter:
    """
    A class for generating VM code from a parsed Jack program.

    This class provides methods for writing various types of VM commands, including push, pop, arithmetic,
    label, goto, if-goto, call, and function commands. It also includes a dictionary of symbols that maps Jack
    operators to their corresponding VM commands.

    Attributes:
        vmcode: A list of strings representing the generated VM code.
    """

    def __init__(self):
        self.vmcode = []

    def write_push(self, kind, index, token=''):
        if token.isdigit():
            self.vmcode.append(f'push constant {token}')
        elif token == 'true':
            self.vmcode.append(f'push constant 1')
            self.vmcode.append(f'neg')
        elif token == 'null' or token == 'false':
            self.vmcode.append(f'push constant 0')
        else:
            self.vmcode.append(f'push {kind} {index}')

    def write_pop(self, kind, index):
        self.vmcode.append(f'pop {kind} {index}')

    def write_arithmetic(self, token):
        self.vmcode.append(f'{symbols[token]}')

    def write_label(self, label):
        self.vmcode.append(f'label {label}')

    def write_goto(self, label):
        self.vmcode.append(f'goto {label}')

    def write_if(self, label):
        self.vmcode.append(f'if-goto {label}')

    def write_call(self, token):
        self.vmcode.append(token)

    def write_function(self, subroutine, name, num_arg):
        self.vmcode.append(f'function {name} {num_arg}')

