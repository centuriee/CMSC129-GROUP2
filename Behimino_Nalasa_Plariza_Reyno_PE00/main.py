from lexer.lexer import Lexer

lexer = Lexer("1char=6")
tokens = lexer.tokenize()
print(tokens)