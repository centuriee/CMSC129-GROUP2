import re

class Parser:
    def __init__(self, filename = "tokens.tkn"):
        self.filename = filename
        self.raw_file = self.read_file()
        self.content = self.load_tokens()
        self.pos = 0

    def read_file(self):
        try:
            with open(self.filename, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
        except Exception as e:
            print(f"Error reading file: {e}")

    def load_tokens(self):
        tokens = self.read_file()

        # regex to extract tokens of form (TYPE, value)
        pattern = r"\(\s*([A-Za-z_]+)\s*,\s*([A-Za-z0-9_]+)\s*\)"
        matches = re.findall(pattern, tokens)

        return [(typ, val) for typ, val in matches]

    # for printing
    def print_tokens(self):
        print(self.content)

    def print_raw_file(self):
        print(self.raw_file)


    # parsing logic
    def current(self):
        if self.pos < len(self.content):
            return self.content[self.pos]
        return ("EOF", "EOF")

    def match(self, expected_type):
        token_type, token_val = self.current()
        if token_type == expected_type:
            self.pos += 1
        else:
            raise SyntaxError(
                f"Expected {expected_type}, got {token_type} at token index {self.pos}"
            )
        

    # GRAMMAR
    # KEYWORDS: "IOL", "LOI", "INT", "STR", "INTO", "IS", "BEG", "PRINT", "ADD", "SUB", "MULT", "DIV", "MOD", "NEWLN"
    # var_name = ident?
    # expr = variable (var_name), literal & numerical expression (NUMBER)
    
    # program -> IOL stmts LOI
    def IOL(self):
        # ensures program starts with IOL
        token_type, token_val = self.current()
        if token_type != "IOL":
            raise SyntaxError(f"Program must start with 'IOL', got '{token_val}' ({token_type}) at index {self.pos}")

        self.match("IOL")
        self.stmts()
        self.match("LOI")

        # ensures program ends with LOI
        token_type, _ = self.current()
        if token_type != "EOF":
            raise SyntaxError(
                f"Unexpected token after LOI: {token_type} at index {self.pos}"
            )

    # stmts -> stmt stmts | e
    def stmts(self):
        while True:
            token_type, _ = self.current()
            if token_type == "LOI":
                break
            self.stmt()

    # stmt -> INT | STR | BEG | INTO | NEWLN | PRINT | operation
    def stmt(self):
        token_type, _ = self.current()

        if token_type == "INT":
            self.INT()
        elif token_type == "STR":
            self.STR()
        elif token_type == "BEG":
            self.BEG()
        elif token_type == "INTO":
            self.INTO()
        elif token_type == "PRINT":
            self.PRINT()
        elif token_type in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            self.operation()
        elif token_type == "NEWLN":
            self.match("NEWLN")

    """ 
        changed last statement from number to expr. main issue with this is type compatibility
        but i think its fine bc it should be handled by the execution phase
    """
    # INT -> INT IDENT IS NUMBER
    def INT(self):
        self.match("INT")
        self.match("IDENT")
        self.match("IS")
        self.expr()

    # STR -> STR IDENT
    def STR(self):
        self.match("STR")
        self.match("IDENT")

    # BEG -> BEG IDENT
    def BEG(self):
        self.match("BEG")
        self.match("IDENT")

    # INTO -> INTO IDENT IS expr
    def INTO(self):
        self.match("INTO")
        self.match("IDENT")
        self.match("IS")
        self.expr()

    # PRINT -> PRINT expr
    def PRINT(self):
        self.match("PRINT")
        self.expr()

    # helper functions
    # expr -> IDENT | INT_LIT | operation
    def expr(self):
        token_type, _ = self.current()

        if token_type == "IDENT":
            self.match("IDENT")

        elif token_type == "INT_LIT":
            self.match("INT_LIT")

        elif token_type in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            self.operation()

        else:
            raise SyntaxError(f"Expected expr (IDENT, INT_LIT, OPERATION), got {token_type}")
    
    # operation -> (ADD | SUB | MULT | DIV | MOD) number number
    def operation(self):
        # operator
        token_type, _ = self.current()

        if token_type not in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            raise SyntaxError(f"Expected OPERATOR, got {token_type}")

        self.match(token_type)

        # operand 1
        self.expr()

        # operand 2
        self.expr()

    """ DEPRECATED FUNC, idk if needed still since meron na ang expr() """
    # number -> INT_LIT | operation
    def number(self):
        token_type, _ = self.current()

        if token_type == "INT_LIT":
            self.match("INT_LIT")

        elif token_type in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            self.operation()

        else:
            raise SyntaxError(f"Expected number (INT_LIT or OPERATION), got {token_type}")
    """ DEPRECATED FUNC, idk if needed still since meron na ang expr() """


    # parsing function
    def parse(self):
        self.IOL()
        if self.current()[0] != "EOF":
            raise SyntaxError("Extra tokens at end")
        return "no errors"
    

def main():
    parser = Parser()
    parser.print_raw_file()
    print(parser.parse())

if __name__ == "__main__":
    main()