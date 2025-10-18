import re

class Token:
    # why does python have to be cringe like that man
    # give me my lazy multiple constructors back
    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            self.type = args[0]
            self.value = args[1]
            self.name = None
        elif len(args) == 3:
            self.type = args[0]
            self.name = args[1]
            self.value = args[2]
        else:
            raise TypeError("Invalid number of arguments. Takes 2 or 3 only")

    def __repr__(self):
        if self.name == None:
            return f"Token({self.type}, {self.value})"
        else:
            return f"Token({self.type}, {self.name}, {self.value})"
    
class Error:
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Error({self.type}, {self.value})"

class Lexer:
    NUMBER = r"\d+\.?\d*|\.\d+"
    VARIABLE = r"[a-zA-Z_][a-zA-Z0-9_]*"
    INVALID_VARIABLE_NAME = r"\d+[a-zA-Z_][a-zA-Z0-9_]*"
    OPERATOR = r"[+\-/*%]"
    ASSIGNMENT = r"="
    SKIP = r"[ \t]+"

    # C keywords
    KEYWORDS = {
        "int", "float", "char", "double", "if", "else", "while",
        "for", "return", "void", "struct", "break", "continue"
    }

    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> list[Token]:
        token_spec = [
            ("VARIABLE", self.VARIABLE),
            ("INVALID_VARIABLE_NAME", self.INVALID_VARIABLE_NAME),
            ("NUMBER", self.NUMBER),
            ("OPERATOR", self.OPERATOR),
            ("ASSIGNMENT", self.ASSIGNMENT),
            ("SKIP", self.SKIP),
        ]
        tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
        get_token = re.compile(tok_regex).finditer

        tokens = []

        for match in get_token(self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == "SKIP":
                continue

            if kind == "INVALID_VARIABLE_NAME":
                tokens.append(Error("INVALID_VARIABLE_NAME", value))

            elif kind == "VARIABLE":
                if value in self.KEYWORDS:
                    tokens.append(Error("RESERVED_KEYWORD", value))
                else:
                    tokens.append(Token("VARIABLE", value, None))

            else:
                tokens.append(Token(kind, value))

        return tokens

