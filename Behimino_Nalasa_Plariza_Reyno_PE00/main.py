from lexer.lexer import Lexer

def postfixer(token_stream):
    
    tokens_out = []
    operator_stack = []

    precedence = {
        '%': 2,
        '*': 2,
        '/': 2,
        '+': 1,
        '-': 1
    }

    # currently no support for parenthesis
    for token in token_stream:
        
        # add numbers and variables to tokens_out
        if token.type == "VARIABLE" or token.type == "NUMBER":
            tokens_out.append(token)
        
        # do some checking if not
        elif token.type == "OPERATOR":
            
            # empty stack, push as normal (prevents errors)
            if len(operator_stack) == 0:
                operator_stack.append(token)

            # check precedence of highest element, if equal or greater pop until empty
            elif precedence[operator_stack[len(operator_stack) - 1].value] >= precedence[token.value]:
                while len(operator_stack) != 0:
                    tokens_out.append(operator_stack.pop())
                operator_stack.append(token)

            # otherwise push as normal
            else:
                operator_stack.append(token)
        
        else:
            Exception("WARNING: Invalid token class passed to postfixer function.")
    
    # at end, empty stack and add to tokens_out
    while len(operator_stack) != 0:
        tokens_out.append(operator_stack.pop())

    return tokens_out

lexer = Lexer("1char=6")
tokens = lexer.tokenize()
print(tokens)

example1 = Lexer("a+b*c+d")
tokens_1 = example1.tokenize()
print(tokens_1)
print(postfixer(tokens_1))