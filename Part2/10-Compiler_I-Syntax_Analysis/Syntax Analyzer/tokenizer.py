keywords = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
            'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']

symbols = ['(', ')', ';', '=', '+', '-', '*', '/', '[', ']', '{', '}', '.', ',', '&', '<', '>', '|', '~']


class Tokenizer:

    def __init__(self, file):
        """
        Creates a list with all the tokens in the file.

        :param file: the jack file with the source code.
        """

        # Create a list of lists of tokens (with a list for each line)
        self.data = [i.replace(';', ' ; ').replace('(', ' ( ').replace(')', ' ) ').replace('[', ' [ ').replace
                     (']', ' ] ').replace('.', ' . ').replace('-', ' - ').replace('~', ' ~ ').replace(',', ' , ')
                     .split('//')[0].strip().split() for i in file if i.lstrip() != '' and i.lstrip()[0] not in '/*']

        # Join the list of lists into a single list of tokens
        self.data = [item for sublist in self.data for item in sublist]

        # Join each string constant into a single token
        for i in range(len(self.data)):
            if i < len(self.data):
                if self.data[i][0] == '"':
                    x = i + 1
                    while self.data[x][-1] != '"':
                        x += 1
                    self.data[i:x+1] = [' '.join(self.data[i:x+1])]
        self.next_token = 1
        self.current_token = self.data[0]

    def has_tokens(self):
        if self.next_token < len(self.data):
            return True
        else:
            return False

    def advance(self):
        """
        Advances to the next token in the list of tokens.

        :return: The next token in the list if there are more tokens left to process, otherwise the current token.
        """
        if self.has_tokens():
            self.current_token = self.data[self.next_token]
            self.next_token += 1
            return self.current_token
        else:
            return self.current_token

    def token_type(self):
        if self.current_token in keywords:
            return 'keyword'
        elif self.current_token in symbols:
            return 'symbol'
        elif self.current_token.startswith('"'):
            return 'stringConstant'
        elif self.current_token.isdigit():
            return 'integerConstant'
        else:
            return 'identifier'
