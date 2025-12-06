import re, os

class ParserError(Exception):
    """exception raised when a semantic or syntax error occurs."""
    pass

class SemanticError(Exception):
    """Exception raised when a semantic error occurs"""
    pass

class SyntaxError(Exception):
    """Excpetion raised when a syntax error occurs"""
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
    def __init__(self, compile_mode, filename = "tokens.tkn", main_window = None, ):
        # create path relative to parser.py

        # value to check if we're in compile mode
        self.compile_mode = compile_mode
        # only run certain checks if in execute

        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(os.path.dirname(current_dir), filename)
        self.raw_file = self.read_file()
        self.lines = self.raw_file.splitlines()  # store raw lines for error reporting
        self.content = self.load_tokens()
        self.pos = 0
        self.semantic_errors = []
        self.symbol_table = Symbol_Table()
        self.main_window = main_window  # Store reference to GUI

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
            tkn_to_return = self.current()
            self.pos += 1
            return tkn_to_return
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
        _, var_name, _ = self.match("IDENT")

        next_token = self.current()
        if next_token[0] == "IS":
            self.match("IS")
            _, returned_value, _ = self.expr()

            if not self.compile_mode:
                if type(returned_value) != int:
                    ParserError(f"Value {returned_value} cannot be assigned to \
                        variable {var_name} of type INT_LIT")
                self.symbol_table.create_var(var_name, returned_value, 'INT_LIT')
            else:
                self.symbol_table.create_var(var_name, None, 'INT_LIT')
        else:
            self.symbol_table.create_var(var_name, None, 'INT_LIT')

    # STR -> STR IDENT
    def STR(self):
        self.match("STR")
        _, var_name, _ = self.match("IDENT")

        if not self.compile_mode:
            self.symbol_table.create_var(var_name, "", 'STR')
        else:
            self.symbol_table.create_var(var_name, None, 'STR')

    # BEG -> BEG IDENT
    def BEG(self):
        self.match("BEG")
        _, variable_name, line_num = self.match("IDENT")

        # Check if variable exists
        if variable_name not in self.symbol_table.entries:
            raise ParserError(
                f"Line {line_num}: SEMANTIC ERROR; Variable '{variable_name}' must be declared before using BEG"
            )

        # ONLY EXECUTE IF NOT IN COMPILE MODE
        if not self.compile_mode:
            # Get variable type to determine what kind of input to expect
            var_type = self.symbol_table.get_var_type(variable_name)

            # Show input dialog if GUI is available
            if self.main_window is not None:
                user_input = self.main_window.show_input_dialog(variable_name)
                
                if user_input is None:
                    raise ParserError(
                        f"Line {line_num}: User cancelled input for variable '{variable_name}'"
                    )
                
                # Type conversion based on variable type
                try:
                    if var_type == 'INT_LIT':
                        value = int(user_input)
                    elif var_type == 'STR':
                        value = str(user_input)
                    else:
                        raise ParserError(
                            f"Line {line_num}: SEMANTIC ERROR; Unknown variable type '{var_type}'"
                        )
                    
                    self.symbol_table.assign_var(variable_name, value)
                    
                    # Log to console
                    if self.main_window is not None:
                        self.main_window.console_output.append(
                            f"User input for '{variable_name}': {value}"
                        )
                        
                except ValueError:
                    raise ParserError(
                        f"Line {line_num}: SEMANTIC ERROR; Invalid input for variable '{variable_name}' of type {var_type}. Expected a valid {var_type} value."
                    )
            else:
                # Fallback to console input if no GUI
                print(f"Enter value for '{variable_name}' ({var_type}): ", end='')
                user_input = input()
                
                try:
                    if var_type == 'INT_LIT':
                        value = int(user_input)
                    elif var_type == 'STR':
                        value = str(user_input)
                    else:
                        raise ParserError(
                            f"Line {line_num}: SEMANTIC ERROR; Unknown variable type '{var_type}'"
                        )
                    
                    self.symbol_table.assign_var(variable_name, value)
                    
                except ValueError:
                    raise ParserError(
                        f"Line {line_num}: SEMANTIC ERROR; Invalid input for variable '{variable_name}' of type {var_type}"
                    )

    # INTO -> INTO IDENT IS expr
    def INTO(self):
        self.match("INTO")
        _, var_name, _ = self.match("IDENT")
        self.match("IS")
        _, new_value, _ = self.expr()

        self.symbol_table.assign_var(var_name, new_value)

    # PRINT -> PRINT expr
    def PRINT(self):
        self.match("PRINT")
        var_type, var, _ = self.expr()

        if not self.compile_mode:
            if(var_type == 'IDENT'):
                var = self.symbol_table.get_var_value(var)
            elif(var_type == 'INT_LIT'):
                pass
            else:
                ParserError(f"Line {_}: Unexpected token type intercepted {var_type}")
            
            # Print to GUI console if available
            if self.main_window is not None:
                self.main_window.console_output.append(f"Output: {var}")
            else:
                print(var)

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

        # match the operator token
        self.match(token_type)

        if self.compile_mode:
            self.expr()  # first operand
            self.expr()  # second operand
            # compiler can generate AST node here instead of computing
            return ("INT_LIT", None, None)  # placeholder value for compiler

        token_type_1, var_1, line_num = self.expr()
        token_type_2, var_2, line_num = self.expr()

        if token_type_1 == "IDENT":
            if self.symbol_table.get_var_type(var_1) != "INT_LIT":
                ParserError(f"Line {line_num}: SEMANTIC ERROR; ADD \
                            works only with variables of type INT_LIT \
                            got {self.symbol_table.get_var_value(var_1)}")
            var_1 = self.symbol_table.get_var_value(var_1)

        if token_type_2 == "IDENT":
            if self.symbol_table.get_var_type(var_2) != "INT_LIT":
                ParserError(f"Line {line_num}: SEMANTIC ERROR; ADD \
                            works only with variables of type INT_LIT \
                            got {self.symbol_table.get_var_value(var_2)}")
            var_2 = self.symbol_table.get_var_value(var_2)

        var_1 = int(var_1)
        var_2 = int(var_2)

        if token_type == "ADD":
            return ("INT_LIT", var_1 + var_2, line_num)
        elif token_type == "SUB":
            return ("INT_LIT", var_1 - var_2, line_num)
        elif token_type == "MULT":
            return ("INT_LIT", var_1 * var_2, line_num)
        elif token_type == "DIV":
            return ("INT_LIT", int(var_1 / var_2), line_num)
        elif token_type == "MOD":
            return ("INT_LIT", var_1 % var_2, line_num)
        else:
            raise ParserError(f"Line {line_num}: SYNTAX ERROR; Expected \
                            operator, got {token_type}")



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