import re

class Token:
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"
    
class Error:
    def __init__(self, type_: str, value: str):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Error({self.type}, {self.value})"



class Lexer:
    NUMBER = r"\d+\.?\d*|\.\d+"
    VARIABLE = r"[a-zA-Z_][a-zA-Z0-9_]*"
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
            ("NUMBER", self.NUMBER),
            ("OPERATOR", self.OPERATOR),
            ("ASSIGNMENT", self.ASSIGNMENT),
            ("SKIP", self.SKIP),
        ]
        tok_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in token_spec)
        get_token = re.compile(tok_regex).finditer

        tokens = []
        pos = 0

        for match in get_token(self.text):
            kind = match.lastgroup
            value = match.group()
            start, end = match.span()

            # Skip whitespace
            if kind == "SKIP":
                pos = end
                continue

            # Handle variable names
            if kind == "VARIABLE":
                if value in self.KEYWORDS:
                    tokens.append(Error("RESERVED_KEYWORD", value))
                else:
                    tokens.append(Token("VARIABLE", value))

            # Handle other tokens
            else:
                tokens.append(Token(kind, value))

            pos = end

        return tokens
