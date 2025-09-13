from lexer.lexer import Lexer

lexer = Lexer("char=6")
tokens = lexer.tokenize()
print(tokens)