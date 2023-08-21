class SymbolTable:
    """
    A symbol table for keeping track of symbols in a Jack program.

    It provides methods for defining symbols, retrieving information about symbols, and resetting the
    subroutine-level symbol table when a subroutine is finished.

    Attributes:
        classTable: A dictionary representing the symbol table for class-level symbols.
        subTable: A dictionary representing the symbol table for subroutine-level symbols.
        subroutines_dict: A dictionary containing information about subroutines in the Jack program.
        numbers: A dictionary containing counts of the number of symbols of each kind (e.g., local, field).
        classname: The name of the current class being compiled.
    """

    def __init__(self):
        self.classTable = {}
        self.subTable = {}
        self.subroutines_dict = {}
        self.numbers = {'class': 0, 'field': 0, 'static': 0, 'local': 0, 'argument': 0}
        self.classname = ''

    def define_symbol(self, token, dtype, kind):
        """ Add a new token to the appropriate symbol table (based on the kind of symbol) if is not already there."""
        if kind == 'static' or kind == 'field':
            if token in self.classTable:
                return
            else:
                self.classTable[token] = (dtype, kind, self.numbers[kind])
                self.numbers[kind] += 1
        elif token in self.subTable:
            return
        else:
            if kind == 'local':
                self.subTable[token] = (dtype, kind, self.numbers[kind])
                self.numbers[kind] += + 1
            elif kind == 'argument':
                self.subTable[token] = (dtype, 'argument', self.numbers['argument'])
                self.numbers[kind] += 1
            elif kind == 'class':
                self.classTable[token] = (dtype, 'class', self.numbers['class'])
                self.numbers['class'] += 1
                self.classname = token
            elif kind == 'subroutine':
                self.subroutines_dict[token.split('.')[1]] = (dtype, token.split('.')[0])

    def finish_subroutine(self):
        """ Reset subroutine level symbol table."""
        self.subTable = {}
        self.numbers['local'] = 0
        self.numbers['argument'] = 0

    def varcount(self, kind):
        """ Return how many symbols of kind 'kind' (e.g. local, field) are already in the symbol table"""
        return self.numbers[kind]

    def kindof(self, token):
        """ Return the kind of token if it is in the symbol table, otherwise return the token."""
        if token in self.subTable:
            return self.subTable[token][1]
        elif token in self.classTable:
            if self.classTable[token][1] == 'field':
                return 'this'
            else:
                return self.classTable[token][1]
        else:
            return token

    def dtypeof(self, token):
        """ Return the data type of token if it is in the symbol table, otherwise return the token."""
        if token in self.subTable:
            return self.subTable[token][0]
        elif token in self.classTable:
            return self.classTable[token][0]
        else:
            return token

    def indexof(self, token):
        """ Return the index of the token if it is in the symbol table, otherwise return the token."""
        if token in self.subTable:
            return self.subTable[token][2]
        elif token in self.classTable:
            return self.classTable[token][2]
        else:
            return token
