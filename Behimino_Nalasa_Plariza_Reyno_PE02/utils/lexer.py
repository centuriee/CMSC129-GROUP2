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
    # okay look i want the thing to see 1.2 as a pure error
    # hence the space to act as delimiter
    # also included is the newline and the tab
    INT_LIT = r"\d+[\n\s\t]"
    IDENT = r"[a-zA-Z][a-zA-Z0-9]*[\n\s\t]"
    SKIP = r"[ \t]+"
    ERR_LEX = r"[^\n\s\t]+[\n\s\t]"

    # IOL KEYWORDS
    KEYWORDS = {
        "IOL", "LOI", "INT", "STR", "INTO", "IS", "BEG", "PRINT", "ADD", "SUB",
        "MULT", "DIV", "MOD", "NEWLN"
    }

    def __init__(self, text: str):
        self.text = text + ' '

    def tokenize(self) -> list[Token]:
        token_spec = [
            ("INT_LIT", self.INT_LIT),
            ("IDENT", self.IDENT),
            ("SKIP", self.SKIP),
            ("ERR_LEX", self.ERR_LEX)
        ]
        tok_regex = "|".join(
            f"(?P<{name}>{pattern})" for name, pattern in token_spec)
        get_token = re.compile(tok_regex).finditer

        tokens = []

        for match in get_token(self.text):
            kind = match.lastgroup
            value = match.group()[:-1]
            # purge the last character?

            if kind == "SKIP":
                continue

            if kind == "INVALID_VARIABLE_NAME":
                tokens.append(Token("ERR_LEX", value))

            elif kind == "IDENT":
                if value in self.KEYWORDS:
                    tokens.append(Token(value, value))
                else:
                    tokens.append(Token("IDENT", value))

            elif kind == "INT_LIT":
                tokens.append(Token(kind, value))

            else:
                tokens.append(Token("ERR_LEX", value))

        return tokens

