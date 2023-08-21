from tokenizer import Tokenizer

# Token type of constants and variables
terminal = ['stringConstant', 'integerConstant', 'identifier', 'keyword']
# Keywords for statements
statements = ['while', 'if', 'let', 'do', 'return']
# Keywords for subroutines
subroutines = ['method', 'function', 'constructor']
# XML code of symbols
symbols = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}
# Operations
op = ['+', '-', '*', '/', '&', '|', '<', '>', '=']


class CompilationEngine:
    """ Handles the compilation of a file written in Jack to XML code.

    The compile_class method is called on a CompilationEngine object, and it starts a loop until it finishes compiling.

    The `indent` parameter is used in all methods to control the level of indentation for the generated XML code.
    The value of `indent` should be an integer, where each increment of 1 represents an additional level of indentation.
    """

    def __init__(self, file):
        """
        Initializes a CompilationEngine object.

        :param file: The jack file with the source code
        """

        self.data = Tokenizer(file)
        self.xml_data = []
        self.indentation = '    '
        self.last_type = ''
        self.xml_data.append('<class>')

    def compile_class(self, indent=1, cnt=0):
        """
        Start a loop and call the appropriate function based on the current token.

        If the current token is a subroutine add '<subroutineDec>' to XML_data.

        :param cnt: whether to continue in the loop or return (assuming there are still tokens), 0 = stop, 1 = continue.
        It should be called with cnt = 1 to start compilation, default value is 0.
        """

        cont = 1
        while self.data.has_tokens() and cont == 1:
            cont = cnt * cont
            if self.data.current_token in subroutines:
                self.xml_data.append(self.indentation * indent + '<subroutineDec>')
                self.xml_data.append(f'{(indent+1) * self.indentation}<{self.data.token_type()}>'
                                     f' {self.data.current_token} </{self.data.token_type()}>')
                self.data.advance()
                self.compile_subroutinedec(indent)
            elif self.data.current_token in statements:
                self.compile_statements(indent)
            else:
                self.compile_term(indent)
        if cont == 1:
            self.compile_term(indent)
            self.xml_data.append('</class>')

    def compile_term(self, indent=1):
        """ Add XML code for current token, advance to next token and call the appropriate method when needed.

        Called by all other methods directly or indirectly, it is the only method that advances to the next token.
        """

        if self.data.current_token in subroutines:
            self.compile_class(indent)
            return
        elif self.data.current_token == 'var':
            self.xml_data.append(self.indentation * indent + '<varDec>')
            self.xml_data.append(f'{(indent+1) * self.indentation}<{self.data.token_type()}>'
                                 f' {self.data.current_token} </{self.data.token_type()}>')
            self.last_type = self.data.token_type()
            self.data.advance()
            self.compile_vardec(indent)
            return
        elif self.data.current_token == 'static' or self.data.current_token == 'field':
            self.xml_data.append(self.indentation * indent + '<classVarDec>')
            self.xml_data.append(f'{(indent+1)  * self.indentation}<{self.data.token_type()}>'
                                 f' {self.data.current_token} </{self.data.token_type()}>')
            self.last_type = self.data.token_type()
            self.data.advance()
            self.compile_classvardec(indent)
            return
        elif self.data.current_token in statements:
            self.last_type = self.data.token_type()
            self.compile_class(indent)
            return
        elif self.data.current_token in symbols:
            self.xml_data.append(f'{indent * self.indentation}<{self.data.token_type()}>'
                                 f' {symbols[self.data.current_token]} </{self.data.token_type()}>')
        elif self.data.current_token.startswith('"'):
            self.xml_data.append(f"{indent * self.indentation}<{self.data.token_type()}>"
                                 f" {self.data.current_token[1:-1]} </{self.data.token_type()}>")
        else:
            self.xml_data.append(f'{indent * self.indentation}<{self.data.token_type()}>'
                                 f' {self.data.current_token} </{self.data.token_type()}>')
            # If the last token was an identifier and the current token is '(' or '[' then what follows is an
            # expression, expression list or parameter list.
            if self.last_type == 'identifier' and self.data.current_token in '( [ .':
                if self.data.current_token == '(':
                    # If the last token was an identifier and the token before it was '.' or 'do' what follows is an
                    # expression list
                    if self.data.data[self.data.next_token-3] in 'do .':
                        self.last_type = self.data.token_type()
                        self.data.advance()
                        self.compile_expressionlist(indent)
                        self.compile_term(indent)
                        return
                    else:
                        self.last_type = self.data.token_type()
                        self.data.advance()
                        self.compile_parameterlist(indent)
                        return
                elif self.data.current_token == '[':
                    self.last_type = self.data.token_type()
                    self.data.advance()
                    self.compile_expression(indent)
                    return
                elif self.data.current_token == '.':
                    self.last_type = self.data.token_type()
                    self.data.advance()
                    self.compile_term(indent)
                    return
        self.last_type = self.data.token_type()
        if self.data.has_tokens():
            self.data.advance()
        else:
            return

    def compile_subroutinedec(self, indent=1):
        """Compile subroutine by calling compile term until a '{' indicates the start of the subroutine body"""
        while self.data.current_token != '{' and self.data.has_tokens():
            self.compile_term(indent + 1)
        self.compile_subroutinebody(indent+1)
        self.xml_data.append(self.indentation * indent + '</subroutineDec>')


    def compile_subroutinebody(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<subroutineBody>')
        self.compile_term(indent+1)
        while self.data.current_token != '}':
            self.compile_term(indent+1)
        self.compile_term(indent+1)
        self.xml_data.append(self.indentation * indent + '</subroutineBody>')

    def compile_statements(self, indent=1):
        """ Add XML code for 'statements' and call the appropriate compile_statement method"""
        self.xml_data.append(self.indentation * indent + '<statements>')
        while self.data.current_token in statements:
            if self.data.current_token == 'while':
                self.compile_while_statement(indent+1)
            elif self.data.current_token == 'if':
                self.compile_if_statement(indent+1)
            elif self.data.current_token == 'do':
                self.compile_do_statement(indent+1)
            elif self.data.current_token == 'return':
                self.compile_return_statement(indent+1)
            elif self.data.current_token == 'let':
                self.compile_let_statement(indent+1)
        self.xml_data.append(self.indentation * indent + '</statements>')

    def compile_if_statement(self, indent=1):
        """
        Compile if statement by adding XML code for if statement, and calling compile term, expression and statement.

        If there is an else compile it before closing the if statement.
        """

        self.xml_data.append(self.indentation * indent + '<ifStatement>')
        self.xml_data.append(f'{(indent + 1) * self.indentation}<{self.data.token_type()}>'
                             f' {self.data.current_token} </{self.data.token_type()}>')
        self.data.advance()
        self.compile_term(indent+1)
        self.compile_expression(indent+1, ')')
        self.compile_term(indent+1)
        self.compile_statements(indent+1)
        self.compile_term(indent+1)
        if self.data.current_token == 'else':
            self.compile_term(indent+1)
            self.compile_term(indent+1)
            self.compile_statements(indent + 1)
            self.compile_term(indent+1)
        self.xml_data.append(self.indentation * indent + '</ifStatement>')

    def compile_while_statement(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<whileStatement>')
        self.xml_data.append(f'{(indent + 1) * self.indentation}<{self.data.token_type()}>'
                             f' {self.data.current_token} </{self.data.token_type()}>')
        self.data.advance()
        self.compile_term(indent+1)
        self.compile_expression(indent+1, ')')
        self.compile_term(indent+1)
        self.compile_statements(indent+1)
        self.compile_term(indent+1)
        self.xml_data.append(self.indentation * indent + '</whileStatement>')

    def compile_let_statement(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<letStatement>')
        self.xml_data.append(f'{(indent + 1) * self.indentation}<{self.data.token_type()}>'
                             f' {self.data.current_token} </{self.data.token_type()}>')
        self.data.advance()
        while self.data.current_token != '=':
            self.compile_term(indent + 1)
        self.compile_term(indent + 1)
        # call compile expression with ';' as the 'final' parameter
        self.compile_expression(indent+1, ';')
        self.xml_data.append(self.indentation * indent + '</letStatement>')

    def compile_do_statement(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<doStatement>')
        self.xml_data.append(f'{(indent + 1) * self.indentation}<{self.data.token_type()}>'
                             f' {self.data.current_token} </{self.data.token_type()}>')
        self.data.advance()
        while self.data.current_token != ';':
            self.compile_term(indent + 1)
        self.compile_term(indent+1)
        self.xml_data.append(self.indentation * indent + '</doStatement>')

    def compile_return_statement(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<returnStatement>')
        self.xml_data.append(f'{(indent + 1) * self.indentation}<{self.data.token_type()}>'
                             f' {self.data.current_token} </{self.data.token_type()}>')
        self.data.advance()
        if self.data.current_token == ';':
            self.compile_term(indent+1)
        else:
            self.compile_expression(indent+1, ';')
        self.xml_data.append(self.indentation * indent + '</returnStatement>')

    def compile_expressionlist(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<expressionList>')
        while not (self.data.current_token in ')'):
            self.compile_expression(indent+1, ',)')
        self.xml_data.append(self.indentation * indent + '</expressionList>')

    def compile_expression(self, indent=1, final=')]'):
        """
        Add XML code for 'expression' and call compile term until the end of the expression.

        :param final: A string containing the characters that mark the end of the expression. The default value is ')]'.
        """

        if 'unary' not in final:
            self.xml_data.append(self.indentation * indent + '<expression>')
        while not (self.data.current_token in final):
            # If current_token is '(', a unary operator or is in 'terminal', then it is a new term, add XML code
            # for term and call compile_expression
            if self.data.token_type() in terminal or self.data.current_token == '(' or \
                    (self.data.current_token in '-~' and self.last_type != 'identifier'):
                self.xml_data.append(f'{(indent + 1) * self.indentation}<term>')
                if self.data.current_token == '(':
                    self.compile_term(indent+2)
                    self.compile_expression(indent+2, ')')
                # If current_token is a unary operator call expression with unary in 'final' so XML code for another
                # expression is not added
                elif self.data.current_token in '-~':
                    self.compile_term(indent+2)
                    self.compile_expression(indent+2, ')unary')
                while self.data.current_token not in ';]),' and self.data.current_token not in op:
                    self.compile_term(indent+2)
                self.xml_data.append(f'{(indent+1) * self.indentation}</term>')
                if self.data.current_token in op:
                    self.compile_term(indent+1)
            else:
                self.compile_term(indent+1)
        # If 'unary' is in 'final' the term that follows at this point should not be compiled, because it is not
        # the end of the current expression, but the end of the previous one or an operation
        if 'unary' not in final:
            self.xml_data.append(self.indentation * indent + '</expression>')
            # If ',' is in final compile_expression was called by compile_expressionlist, which will be left in an
            # infinite loop if compile_expression compiles the closing parenthesis
            if ',' not in final or self.data.current_token == ',':
                self.compile_term(indent)
            if self.data.current_token == '}':
                return

    def compile_parameterlist(self, indent=1):
        self.xml_data.append(self.indentation * indent + '<parameterList>')
        while self.data.current_token != ')':
            self.compile_term(indent+1)
        self.xml_data.append(self.indentation * indent + '</parameterList>')

    def compile_vardec(self, indent=1):
        while self.data.current_token != ';':
            self.compile_term(indent+1)
        self.compile_term(indent + 1)
        self.xml_data.append(self.indentation * indent + '</varDec>')

    def compile_classvardec(self, indent=1):
        while self.data.current_token != ';':
            self.compile_term(indent+1)
        self.compile_term(indent + 1)
        self.xml_data.append(self.indentation * indent + '</classVarDec>')
