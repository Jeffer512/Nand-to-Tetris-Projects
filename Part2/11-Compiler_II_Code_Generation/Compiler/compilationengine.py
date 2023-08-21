from tokenizer import Tokenizer
from symboltable import SymbolTable
from vmwriter import VMWriter

# Token type of constants and variables
terminal = ['integerConstant', 'identifier', 'keyword']
# Keywords for statements
statements = ['while', 'if', 'let', 'do', 'return']
# Keywords for subroutines
subroutines = ['method', 'function', 'constructor']
# Operations
op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
# Jack OS classes
os_classes = ['Math', 'Screen', 'Memory', 'String', 'Keyboard', 'Array', 'Output']


class CompilationEngine:
    """ Handles the compilation of a file written in Jack to VM code.

    The compile_class method is called on a CompilationEngine object, and it starts a loop until it finishes compiling.

    Attributes:
        data: A Tokenizer object used to tokenize the input file and advance through the tokens.
        symbolTable: A SymbolTable object used to keep track of symbols in the Jack program.
        vm: A VMWriter object used to write VM code.
        functions: A dictionary of all functions in the file with the format {function_name: [kind, data_type]}.
        classname: The name of the current class being compiled.
        subroutine: The type of the current subroutine being compiled (method, function, or constructor).
        subroutine_name: The name of the current subroutine being compiled.
        label_num: A counter used to generate unique labels for control structures.
    """

    def __init__(self, file):
        """
        Initializes a CompilationEngine object.

        :param file: The jack file with the source code
        """

        self.data = Tokenizer(file)
        self.symbolTable = SymbolTable()
        self.vm = VMWriter()
        self.functions = {self.data.data[i+2]: (self.data.data[i], self.data.data[i+1]) for i
                          in range(len(self.data.data)) if self.data.data[i] in ['method', 'function', 'constructor']}
        self.classname = ''
        self.subroutine = ''
        self.subroutine_name = ''
        self.label_num = 0

    def compile_class(self, cnt=0):
        """
        Start a loop and call the appropriate function based on the current token.

        :param cnt: whether to continue in the loop or return (assuming there are still tokens), 0 = stop, 1 = continue.
        It should be called with cnt = 1 to start compilation, default value is 0.
        """

        cont = 1
        while self.data.has_tokens() and cont:
            cont = cnt * cont
            if self.data.token in subroutines:
                self.symbolTable.define_symbol(self.data.data[self.data.next_token] + '.' +
                                               self.data.data[self.data.next_token+1],
                                               self.data.token, 'subroutine')
                if self.data.token == 'method':
                    self.symbolTable.define_symbol('this', self.classname, 'argument')
                self.data.advance()
                self.compile_subroutinedec()
            elif self.data.token in statements:
                self.compile_statements()
            else:
                self.compile_term()
        if cont == 1:
            self.compile_term()

    def compile_term(self):
        """ Add XML code for current token, advance to next token and call the appropriate method when needed."""

        if self.data.token in subroutines:
            self.compile_class()
            return
        elif self.data.token == 'static' or self.data.token == 'field':
            self.data.advance()
            self.compile_classvardec()
            return
        elif self.data.token in statements:
            self.compile_class()
            return
        elif self.data.token_type() == 'stringConstant':
            # Remove double quotes
            string = self.data.token.replace('"', '')
            # Add VM code to create a string of size len(string)
            size = len(string)
            self.vm.vmcode.append(f'push constant {size}')
            self.vm.vmcode.append(f'call String.new 1')
            for character in string:
                # Get ASCII code of character and write VM code to append it to the string
                binary_code = ord(character)
                self.vm.vmcode.append(f'push constant {binary_code}')
                self.vm.vmcode.append(f'call String.appendChar 2')
        else:
            # If self.data.token is '(' or '.' what follows is a subroutine call (subroutine declarations are handled
            # by compile_subroutinedec and expressions in parentheses by compile_expression)
            # If self.data.token is '[' what follows is an expression
            if self.data.token in ['(', '[', '.']:
                last_token = self.data.data[self.data.next_token - 2]
                if self.data.token == '[':
                    self.data.advance()
                    self.compile_expression()
                    self.vm.write_arithmetic('+')
                    self.vm.vmcode.append('pop pointer 1')
                    self.vm.vmcode.append('push that 0')
                    return
                elif self.data.token == '(':
                    self.data.advance()
                    # If the subroutine being compiled is a method add 'push pointer 0' to VM code and add 1 to num_arg
                    # to account for the object on which the method acts
                    if last_token in self.functions and self.functions[last_token][0] == 'method':
                        self.vm.vmcode.append('push pointer 0')
                        num_arg = self.compile_expressionlist() + 1
                    else:
                        num_arg = self.compile_expressionlist()
                    self.vm.write_call(f'call {self.classname}.{last_token} {num_arg}')
                    return
                elif self.data.token == '.':
                    next_token = self.data.data[self.data.next_token]
                    self.data.advance()
                    self.data.advance()
                    self.data.advance()
                    if last_token in self.symbolTable.subTable or last_token in self.symbolTable.classTable:
                        self.vm.write_push(self.symbolTable.kindof(last_token),
                                           self.symbolTable.indexof(last_token))
                        num_arg = self.compile_expressionlist()
                        num_arg = str(int(num_arg) + 1)
                        self.vm.write_call(f'call {self.symbolTable.dtypeof(last_token)}.{next_token} {num_arg}')
                        return
                    else:
                        num_arg = self.compile_expressionlist()
                        self.vm.write_call(f'call {last_token}.{next_token} {num_arg}')
                    return
            elif self.data.token in ['true', 'false', 'null']:
                self.vm.write_push(0, 0, self.data.token)
            elif self.data.token == 'class':
                self.classname = self.data.data[self.data.next_token]
        self.data.advance()

    def compile_subroutinedec(self):
        """
        Compile a subroutine declaration.

        Process the tokens for a subroutine declaration, including its parameter list and body.
        Drops subroutine symbol table when finished.
        """
        self.data.advance()
        self.subroutinename = f'{self.classname}.{self.data.token}'
        self.subroutine = self.data.data[self.data.next_token-3]
        self.data.advance()
        self.data.advance()
        self.compile_parameterlist()
        self.data.advance()
        self.data.advance()
        self.compile_subroutinebody()
        self.symbolTable.finish_subroutine()

    def compile_subroutinebody(self):
        """
        Compile a subroutine body.

        Process the tokens for a subroutine body, including any variable declarations and statements.
        """

        while self.data.token == 'var':
            self.data.advance()
            self.compile_vardec()
        self.vm.write_function(self.subroutine, self.subroutinename, self.symbolTable.numbers['local'])
        print(self.symbolTable.subroutines_dict)
        print(self.data.token)
        if self.subroutine == 'method':
            self.vm.vmcode.append('push argument 0')
            self.vm.vmcode.append('pop pointer 0')
        # If the subroutine being compiled is a constructor add VM code to allocate as many registers as fields in
        # the object class
        elif self.subroutine == 'constructor':
            self.vm.vmcode.append(f"push constant {self.symbolTable.numbers['field']}")
            self.vm.write_call('call Memory.alloc 1')
            self.vm.vmcode.append('pop pointer 0')
        while self.data.token != '}':
            self.compile_term()
        self.compile_term()

    def compile_statements(self):
        """
        Call the appropriate compile_statement function based on the current token.

        self.data.token should be in 'statements' when called.
        compile_statement methods are only called by compile_statements.
        """

        while self.data.token in statements:
            if self.data.token == 'while':
                self.compile_while_statement()
            elif self.data.token == 'if':
                self.compile_if_statement()
            elif self.data.token == 'do':
                self.compile_do_statement()
            elif self.data.token == 'return':
                self.compile_return_statement()
            elif self.data.token == 'let':
                self.compile_let_statement()

    def compile_if_statement(self):
        """
        Compile an if statement by generating VM code for the if statement and its branches. Update self.label_num.

        Get label number from self.label_num so each label is unique.
        self.data.token should be 'if' when called.
        """

        label = self.label_num
        self.data.advance()
        self.data.advance()
        self.compile_expression(')')
        self.vm.write_if(f'IF_TRUE{label}')
        self.vm.write_goto(f'IF_FALSE{label}')
        self.label_num += 1
        self.data.advance()
        self.vm.write_label(f'IF_TRUE{label}')
        self.compile_statements()
        self.data.advance()
        self.vm.write_goto(f'IF_END{label}')
        self.vm.write_label(f'IF_FALSE{label}')
        if self.data.token == 'else':
            self.data.advance()
            self.data.advance()
            self.compile_statements()
            self.data.advance()
        self.vm.write_label(f'IF_END{label}')

    def compile_while_statement(self):
        """
        Compile a while statement by generating VM code for the while statement and its body. Update self.label_num.

        Get label number from self.label_num so each label is unique.
        self.data.token should be 'while' when called.
        """
        label = self.label_num
        self.data.advance()
        self.data.advance()
        self.vm.write_label(f'WHILE_START{label}')
        self.label_num += 1
        self.compile_expression(')')
        self.vm.vmcode.append('not')
        self.vm.write_if(f'WHILE_END{label}')
        self.data.advance()
        self.compile_statements()
        self.vm.write_goto(f'WHILE_START{label}')
        self.data.advance()
        self.vm.write_label(f'WHILE_END{label}')

    def compile_let_statement(self):
        """
        Compile a let statement by generating VM code for the let statement and its assignment.

        self.data.token should be 'let' when called.
        """
        self.data.advance()
        pop = self.data.token
        self.data.advance()
        if self.data.token == '=':
            self.data.advance()
            self.compile_expression(';}]')
            if self.vm.vmcode[-1] == 'pop temp 0':
                self.vm.vmcode.pop(-1)
            self.vm.write_pop(self.symbolTable.kindof(pop), self.symbolTable.indexof(pop))
        else:
            self.vm.write_push(self.symbolTable.kindof(pop), self.symbolTable.indexof(pop))
            self.data.advance()
            self.compile_expression(';}]')
            self.vm.write_arithmetic('+')
            self.data.advance()
            self.compile_expression(';}')
            self.vm.vmcode.append('pop temp 0')
            self.vm.write_pop('temp', 0)
            self.vm.vmcode.append('pop pointer 1')
            self.vm.vmcode.append('push temp 0')
            self.vm.vmcode.append('pop that 0')

    def compile_do_statement(self):
        """
        Compile a do statement by calling compile_term until a ';' is found.

        Add 'pop temp 0' to VM code because do statements do not assign variables.
        """

        self.data.advance()
        while self.data.token != ';':
            self.compile_term()
        self.compile_term()
        self.vm.vmcode.append('pop temp 0')

    def compile_return_statement(self):
        """
        Compiles a return statement by generating VM code for the return statement and its expression.

        If there is no return value, write VM code to push the constant 0 onto the stack.
        If the return value is 'this', write VM code to push pointer 0 onto the stack.
        """

        self.data.advance()
        if self.data.token == ';':
            self.vm.vmcode.append('push constant 0')
            self.compile_term()
        elif self.data.token == 'this' and self.data.data[self.data.next_token] == ';':
            self.vm.vmcode.append('push pointer 0')
        else:
            self.compile_expression(';')
        self.vm.vmcode.append('return')

    def compile_expressionlist(self):
        """
        Compile an expression list by calling compile_expression until the end of the expression list.

        :return: number of arguments in expression list.
        """

        num_arg = 0
        while not (self.data.token == ')'):
            self.compile_expression(',)')
            num_arg += 1
        self.data.advance()
        return num_arg

    def compile_expression(self, final=')]'):
        """
        Compiles an expression by generating VM code, handling operations, unary operators, nested expressions, etc.

        :param final: A string containing the characters that mark the end of the expression. The default value is ')]'.
        """

        operation = ''
        while not (self.data.token in final):
            if self.data.token_type() in terminal or self.data.token == '(' or self.data.token in '-~=':
                # If the current token is '(' call compile expression
                if self.data.token == '(':
                    self.data.advance()
                    self.compile_expression(')')
                # If the current token is a unary operator compile the token and call compile expression
                elif self.data.token in '-~=':
                    if self.data.token == '-':
                        self.compile_term()
                        self.compile_expression(')unary;')
                        self.vm.vmcode.append('neg')
                    elif self.data.token == '~':
                        self.compile_term()
                        self.compile_expression(')unary;')
                        self.vm.vmcode.append('not')
                    else:
                        self.compile_term()
                        self.compile_expression(')unary;')
                        self.vm.vmcode.append('eq')
                # Compile terms until the end of the expression or an operation is found
                while self.data.token not in ';]),' and self.data.token not in op:
                    if self.data.token.isdigit():
                        self.vm.write_push('constant', 0, self.data.token)
                    elif self.data.token in self.symbolTable.subTable or self.data.token in self.symbolTable.classTable:
                        self.vm.write_push(self.symbolTable.kindof(self.data.token),
                                           self.symbolTable.indexof(self.data.token),
                                           self.data.token)
                    self.compile_term()
                if operation:
                    if operation == '-':
                        self.vm.vmcode.append('sub')
                    else:
                        self.vm.write_arithmetic(operation)
                    operation = ''
                elif self.data.data[self.data.next_token-3] == '=' and '}' not in final:
                    self.vm.write_arithmetic(operation)
                    operation = ''
                if self.data.token in op:
                    operation = self.data.token
                    self.compile_term()
            else:
                self.compile_term()
        # If 'unary' is in 'final' the term that follows at this point should not be compiled, because it is not
        # the end of the current expression, but the end of the previous one or an operation
        if 'unary' not in final:
            # If ',' is in final compile_expression was called by compile_expressionlist, which will be left in an
            # infinite loop if compile_expression compiles the closing parenthesis
            if ',' not in final or self.data.token == ',':
                self.compile_term()
            if self.data.token == '}':
                return

    def compile_parameterlist(self):
        """
            Compiles a parameter list.

            self.data.token should be the one right after the opening parentheses when called
        """
        while self.data.token != ')':
            # If current_token is not ',', it should be a data type followed by the name of the parameter
            if self.data.token != ',':
                self.symbolTable.define_symbol(self.data.data[self.data.next_token], self.data.token, 'argument')
                self.compile_term()
                self.compile_term()
            else:
                self.compile_term()
        return

    def compile_vardec(self):
        """
        Compiles local variable declarations.

        self.data.token should be a data type when called (e.g. int, boolean, array)
        """
        dtype = self.data.token
        while self.data.token != ';':
            self.compile_term()
            if self.data.token_type() == 'identifier':
                self.symbolTable.define_symbol(self.data.token, dtype, 'local')
        self.compile_term()

    def compile_classvardec(self):
        """
        Compiles field and static variable declarations.

        self.data.token should be a data type when called (e.g. int, boolean, array)
        """
        dtype = self.data.token
        kind = self.data.data[self.data.next_token-2]
        while self.data.token != ';':
            self.compile_term()
            if self.data.token_type() == 'identifier':
                self.symbolTable.define_symbol(self.data.token, dtype, kind)
        self.compile_term()
