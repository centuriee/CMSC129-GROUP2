import re, os

class ParserError(Exception):
    """exception raised when a semantic or syntax error occurs."""
    pass


class Symbol_Table:
    def __init__(self, entries = {}):
        self.entries = entries

    # call to create a new variable
    def create_var(self, name, value, var_type):
        # basically overrides old value, no checking lmao
        self.entries[name] = (var_type, value)
            
    # call to replace variable
    def assign_var(self, name, new_value):
        var = self.entries.get(name)

        # if does not exist, throw error
        if var is None:
            raise ParserError(f"SEMANTIC ERROR; Variable {name} does not exist.")
        else:
            python_type = int if var[0] == 'INT_LIT' else str if var[0] == 'STR' else None

            if(type(new_value) != python_type):
                Exception(f"SEMANTIC ERROR; Cannot assign {new_value} to variable {name} with type {var[0]}")
            else:
                self.entries[name] = (var[0], new_value)

    def get_var_type(self, name):
        var = self.entries.get(name)

        if var is not None:
            return var[0]
        else:
            raise ParserError(f"SEMANTIC ERROR; Variable {name} does not exist.")
        
    def get_var_value(self, name):
        var = self.entries.get(name)

        if var is not None:
            return var[1]
        else:
            raise ParserError(f"SEMANTIC ERROR; Variable {name} does not exist.")
        
    def get_var(self, name):
        var = self.entries.get(name)

        if var is not None:
            return var
        else:
            raise ParserError(f"SEMANTIC ERROR; Variable {name} does not exist.")

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
        self.symbol_table = Symbol_Table()

        self.result = None
        try:
            self.result = self.parse()
        except ParserError as e:
            self.semantic_errors.append(str(e))

    # file reading
    def read_file(self):
        with open(self.filename, 'r') as file:
            return file.read()

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
        return ("EOF", "EOF", len(self.lines))

    def match(self, expected_type):
        token_type, token_val, line_num = self.current()
        if token_type == expected_type:
            self.pos += 1
            return self.current()
        else:
            raise ParserError(
                f"Line {line_num}: SYNTAX ERROR; Expected {expected_type}, "
                f"got {token_type} (value: {token_val})"
            )
        

    # GRAMMAR
    # KEYWORDS: "IOL", "LOI", "INT", "STR", "INTO", "IS", "BEG", "PRINT", "ADD", "SUB", "MULT", "DIV", "MOD", "NEWLN"
    # var_name = ident?
    # expr = variable (var_name), literal & numerical expression (NUMBER)
    
    # program -> IOL stmts LOI
    def IOL(self):
        # ensures program starts with IOL
        token_type, _, line_num = self.current()
        if token_type != "IOL":
            raise ParserError(
                f"Line {line_num}: SYNTAX ERROR; Program must start with 'IOL', started with {token_type}"
            )

        self.match("IOL")  # consume IOL
        self.stmts()       # parse statements
        self.match("LOI")  # consume LOI

        # ensure program ends with EOF
        token_type, _, _ = self.current()
        if token_type != "EOF":
            raise ParserError(
                f"Line {line_num}: SYNTAX ERROR; Program must end with 'LOI', ended with {token_type}"
            )

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

            raise ParserError(
                f"Line {line_num}: SYNTAX ERROR; Unexpected token {token_type}"
            )

    """ 
        changed last statement from number to expr. main issue with this is type compatibility
        but i think its fine bc it should be handled by the execution phase
    """
    # INT -> INT IDENT IS NUMBER
    def INT(self):
        self.match("INT")
        var_name = self.match("IDENT")

        next_token = self.current()
        if next_token[0] == "IS":
            self.match("IS")
            _, returned_value, _ = self.expr()

            if type(returned_value) != int:
                Exception(f"Value {returned_value} cannot be assigned to \
                    variable {var_name} of type INT_LIT")

            self.symbol_table.create_var(var_name[1], returned_value[1], 'INT_LIT')
        else:
            self.symbol_table.create_var(var_name[1], 0, 'INT_LIT')

    # STR -> STR IDENT
    def STR(self):
        self.match("STR")
        token_to_create = self.match("IDENT")

        # token type, token val, line num
        self.symbol_table.create_var(token_to_create[1], None, 'STR')

    # BEG -> BEG IDENT
    def BEG(self):
        self.match("BEG")
        variable_to_assign = self.match("IDENT")

        # add code to call a window to ask user for value

    # INTO -> INTO IDENT IS expr
    def INTO(self):
        self.match("INTO")
        var_name = self.match("IDENT")
        self.match("IS")
        new_value = self.expr()

        self.symbol_table.assign_var(var_name, new_value)

    # PRINT -> PRINT expr
    def PRINT(self):
        self.match("PRINT")
        self.expr()

    # helper functions
    # expr -> IDENT | INT_LIT | operation
    def expr(self):
        token_type, _, _ = self.current()

        if token_type == "IDENT":
            return self.match("IDENT")

        elif token_type == "INT_LIT":
            return self.match("INT_LIT")

        elif token_type in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            return self.operation()

        else:
            _, _, line_num = self.current()
            raise ParserError(
                f"Line {line_num}: SYNTAX ERROR; Expected IDENT, INT_LIT, or OPERATION, got {token_type}"
            )

    # operation -> (ADD | SUB | MULT | DIV | MOD) number number
    def operation(self):
        token_type, _, _ = self.current()

        if token_type not in ("ADD", "SUB", "MULT", "DIV", "MOD"):
            _, _, line_num = self.current()
            raise ParserError(
                f"Line {line_num}: SYNTAX ERROR; Expected operator, got {token_type}"
            )
        elif token_type == "ADD":
            self.match(token_type)
            _, var_1, line_num = self.expr()
            _, var_2, line_num = self.expr()

            
            return ("INT_LIT")


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
        token_type, _, line_num = self.current()
        if token_type != "EOF":
            raise ParserError(f"Line {line_num}: SYNTAX ERROR; Extra tokens at end")

        # return parser object itself for convenience
        return self