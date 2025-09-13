from lexer.lexer import Lexer

lexer = Lexer("sexy=6+9")
tokens = lexer.tokenize()
print(tokens)