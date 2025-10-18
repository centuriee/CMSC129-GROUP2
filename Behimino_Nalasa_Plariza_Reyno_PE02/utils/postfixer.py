def restring(token_stream):
    # takes incoming token stream and converts back to readable string
    if token_stream is None:
        return None

    token_values = []
    for token in token_stream:
        if token.type == "VARIABLE":
            token_values.append(str(token.name))
        else:
            token_values.append(str(token.value))

    return ' '.join(token_values)

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
            
            # check precedence of highest element, if greater pop. when not push.
            while len(operator_stack) != 0 and precedence[operator_stack[len(operator_stack) - 1].value] >= precedence[token.value]:
                tokens_out.append(operator_stack.pop())
            operator_stack.append(token)
    
        else:
            Exception("WARNING: Invalid token class passed to postfixer function.")
    
    # at end, empty stack and add to tokens_out
    while len(operator_stack) != 0:
        tokens_out.append(operator_stack.pop())

    return tokens_out