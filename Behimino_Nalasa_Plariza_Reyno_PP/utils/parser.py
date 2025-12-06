import re, os

class Parser:
    def __init__(self, filename = "tokens.tkn"):
        # create path relative to parser.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(os.path.dirname(current_dir), filename)
        self.raw_file = self.read_file()
        self.lines = self.raw_file.splitlines()  # store raw lines for error reporting
        self.content = self.load_tokens()
        self.pos = 0
        self.semantic_errors = []

        self.result = None
        try:
            self.result = self.parse()
        except Exception as e:
            self.semantic_errors.append(str(e))

    # file reading
    def read_file(self):
        try:
            with open(self.filename, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
        except Exception as e:
            print(f"Error reading file: {e}")

    # token loading
    def load_tokens(self):
        all_tokens = []
        pattern = r"\(\s*([A-Za-z_]+)\s*,\s*([A-Za-z0-9_]+)\s*\)"

        for line_number, line in enumerate(self.lines, start = 1):
            matches = re.findall(pattern, line)
            for typ, val in matches:
                all_tokens.append((typ, val, line_number))

        return all_tokens

    # for printing
    def print_tokens(self):
        print(self.content)

    def print_raw_file(self):
        print(self.raw_file)

    # token utilities
    def current(self):
        if self.pos < len(self.content):
            return self.content[self.pos]
        return ("EOF", "EOF", -1)

    def match(self, expected_type):
        token_type, _, line_num = self.current()
        if token_type == expected_type:
            self.pos += 1
            return
        else:
            self.semantic_errors.append(
                f"Line {line_num}: Expected {expected_type}, got {token_type}"
            )
            self.sync()
            return
    
    # panic mode recovery
    def sync(self):
        safe_tokens = {"INT", "STR", "BEG", "INTO", "PRINT", "NEWLN", "LOI", "EOF"}

        while self.pos < len(self.content):
            token_type, _, _ = self.current()
            print(token_type)
            if token_type in safe_tokens:
                return
            self.pos += 1  # always advance
        

    # GRAMMAR
    # KEYWORDS: "IOL", "LOI", "INT", "STR", "INTO", "IS", "BEG", "PRINT", "ADD", "SUB", "MULT", "DIV", "MOD", "NEWLN"
    # var_name = ident?
    # expr = variable (var_name), literal & numerical expression (NUMBER)
    
    # program -> IOL stmts LOI
    def IOL(self):
        # ensures program starts with IOL
        token_type, _, line_num = self.current()
        if token_type != "IOL":
            self.semantic_errors.append(
                f"Line {line_num}: Program must start with 'IOL', started with {token_type}"
            )
            self.sync()
            return

        self.match("IOL")  # consume IOL
        self.stmts()       # parse statements
        self.match("LOI")  # consume LOI

        # ensure program ends with EOF
        token_type, _, _ = self.current()
        if token_type != "EOF":
            self.semantic_errors.append(
                f"Line {line_num}: Program must end with 'LOI', ended with {token_type}"
            )
            self.sync()
            return

    # stmts -> stmt stmts | e
    def stmts(self):
        while True:
            token_type, _, _ = self.current()
            if token_type in ("LOI", "IOL", "EOF"):
                break
            self.stmt()

    # stmt -> INT | STR | BEG | INTO | NEWLN | PRINT | operation
    def stmt(self):
        token_type, _, _ = self.current()

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
        else:
            _, _, line_num = self.current()

            self.semantic_errors.append(
                f"Line {line_num}: Unexpected token {token_type}"
            )
            self.sync()
            return

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
            _, _, line_num = self.current()
            self.semantic_errors.append(
                f"Line {line_num}: Expected IDENT, INT_LIT, or OPERATION, got {token_type}"
            )
            self.sync()
            return

    # operation -> (ADD | SUB | MULT | DIV | MOD) number number
    def operation(self):
        token_type, _ = self.current()

        if token_type not in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            _, _, line_num = self.current()
            self.semantic_errors.append(
                f"Line {line_num}: Expected operator, got {token_type}"
            )
            self.sync()
            return

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
            _, _, line_num = self.current()
            line_values = [val for _, val, ln in self.content if ln == line_num]
            raw_line = " ".join(line_values)
            raise SyntaxError(
                f"Expected number (INT_LIT, OPERATION) at line {line_num}:\n"
                f"{raw_line}\n"
                f"Got {token_type}"
            )
    """ DEPRECATED FUNC, idk if needed still since meron na ang expr() """


    # parsing function
    def parse(self):
        self.IOL()

        if self.current()[0] != "EOF":
            self.semantic_errors.append("Extra tokens at end")

        # return parser object itself for convenience
        return self
    
parser = Parser()
# parser.print_raw_file()
parser_output = parser.parse()
if parser.semantic_errors:
    print("Errors:", parser.semantic_errors)
else:
    print("Parse successful:", parser.result)