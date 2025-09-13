import re

class Token:
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


class Lexer:
    NUMBER     = r"\d+\.?\d*|\.\d+"          # numbers: 123, 3.14, .5
    VARIABLE   = r"[a-zA-Z]+[0-9a-zA-Z]*"    # var names: x, var1
    OPERATOR   = r"[+\-/*%]"                 # operators: + - * / %
    ASSIGNMENT = r"="                        # assignment operator

    def __init__(self, text: str):
        self.text = text

    def tokenize(self) -> list[Token]:
        token_spec = [
            ("NUMBER", self.NUMBER),
            ("VARIABLE", self.VARIABLE),
            ("OPERATOR", self.OPERATOR),
            ("ASSIGNMENT", self.ASSIGNMENT),
        ]

        # Create one big regex with named groups
        token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
        get_token = re.compile(token_regex).finditer

        tokens = []

        for match in get_token(self.text):
            type = match.lastgroup
            value = match.group()
            tokens.append(Token(type, value))
        return tokens