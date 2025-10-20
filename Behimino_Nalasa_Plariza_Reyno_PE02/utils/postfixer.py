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

    keywords = {
        "IOL", "LOI", "INT", "STR", "INTO",
        "IS", "BEG", "PRINT", "NEWLN"
    }

    operators = {
        "ADD", "SUB", "MULT", "DIV", "MOD"
    }

    precedence = {
        'MOD': 2,
        'MULT': 2,
        'DIV': 2,
        'ADD': 1,
        'SUB': 1
    }

    # currently no support for parenthesis
    for token in token_stream:
        
        type = token.type
        # add numbers and variables to tokens_out
        if type in ("INT_LIT", "IDENT"):
            tokens_out.append(token)
        
        # do some checking if not
        elif type in operators or token.value in precedence:
            
            # determine operator symbol (either from token.value or token.type)
            op = token.value if type in operators else token.type

            # pop operators of higher or equal precedence
            while (operator_stack and
                   precedence.get(operator_stack[-1].value, 0) >= precedence[op]):
                tokens_out.append(operator_stack.pop())

            # push the current operator
            operator_stack.append(token)

        elif type == "NEWLN":
            continue

        elif type in keywords:
            tokens_out.append(token)
    
        else:
            raise ValueError(f"Invalid token {token} passed to postfixer function.")
    
    # at end, empty stack and add to tokens_out
    while len(operator_stack) != 0:
        tokens_out.append(operator_stack.pop())

    return tokens_out