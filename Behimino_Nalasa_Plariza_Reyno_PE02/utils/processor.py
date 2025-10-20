import sys
import re

from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit,
    QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
)

from utils.postfixer import restring, postfixer
from utils.lexer import Lexer, Token


class Processor:
    def __init__(self):
        self.saved_token_variables = []
        self.errors = []
        self.in_block = False
        self.pending_tokens = [] # for IOL and LOI
        self.in_program_block = False  # track if we're between IOL and LOI
    
    # rewrote evaluate_postfix to work with gian's tokens
    def evaluate_postfix_tokens(self, postfix_tokens):
        stack = []
        keywords = {
            "IOL", "LOI", "INT", "STR", "INTO",
            "IS", "BEG", "PRINT", "NEWLN"
        }

        for token in postfix_tokens:
            
            type = token.type

            # numeric literal
            if type == "INT_LIT":
                stack.append(int(token.value))

            # var / identifier
            elif type == "IDENT":
                found_token = None
                for saved in self.saved_token_variables:
                    if saved.name == token.name:
                        found_token = saved
                        break

                if found_token is None:
                    raise ValueError(f"Undefined variable '{token.name}'")
                
                stack.append(float(found_token.value))
            
            # operators
            elif type in {"ADD", "SUB", "MULT", "DIV", "MOD"}:
                if len(stack) < 2:
                    raise ValueError(f"Syntax error: missing operand before or after '{token.type}'")

                b = stack.pop()
                a = stack.pop()

                if type == "ADD":
                    stack.append(a + b)
                elif type == "SUB":
                    stack.append(a - b)
                elif type == "MULT":
                    stack.append(a * b)
                elif type == "DIV":
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    stack.append(a / b)
                elif type == "MOD":
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    stack.append(a % b)

            # ignore keywords that might appear in expression
            elif type in keywords:
                continue

            else:
                raise ValueError(f"Unexpected token '{type}' in expression")
                
        if len(stack) != 1:
            raise ValueError("Invalid expression structure")
    
        return stack[0]

    def process_tokens(self, token_stream, line_number):
        try:
            # initialize state
            if not hasattr(self, "in_block"):
                self.in_block = False
            if not hasattr(self, "pending_tokens"):
                self.pending_tokens = []

            # helper to safely get token name or value
            def get_token_name(token):
                return getattr(token, "name", None) or getattr(token, "value", None)

            # code should start with IOL
            if len(token_stream) == 1 and token_stream[0].type == "IOL":
                if self.in_block:
                    raise ValueError(f"Unexpected 'IOL': already inside a code block.")
                self.in_block = True
                self.pending_tokens.clear()
                return "[Token(IOL, IOL)]", f"Program start detected."

            # code should end with LOI
            if len(token_stream) == 1 and token_stream[0].type == "LOI":
                if not self.in_block:
                    raise ValueError(f"Missing 'IOL': code must begin with IOL.")
                self.in_block = False
                self.pending_tokens.clear()
                return "[Token(LOI, LOI)]", f"Program block ended successfully."

            # handle lines *inside* IOL … LOI
            if self.in_block:

                # store line tokens
                self.pending_tokens.append(token_stream)

                # validate keyword capitalization
                valid_keywords = {"IOL", "LOI", "INT", "STR", "INTO", "IS", "BEG", "PRINT", "NEWLN"}
                for token in token_stream:
                    if token.value.upper() in valid_keywords and token.value != token.value.upper():
                        raise ValueError(f"Syntax error: invalid keyword '{token.value}' (did you mean '{token.value.upper()}'?)")
                    
                # double identifier or double keyword
                for i in range(len(token_stream) - 1):
                    curr = token_stream[i]
                    nxt = token_stream[i + 1]

                    # Two identifiers in a row (e.g. "num num") — invalid
                    if curr.type == "IDENT" and nxt.type == "IDENT":
                        raise ValueError(f"Syntax error: unexpected identifier '{nxt.value}' after '{curr.value}'")

                    # Keyword immediately followed by another keyword (e.g. "INT INT") — invalid
                    if curr.type in {"INT", "STR", "PRINT", "IOL", "LOI"} and nxt.type in {"INT", "STR", "PRINT", "IOL", "LOI"}:
                        raise ValueError(f"Syntax error: unexpected keyword '{nxt.type}' after '{curr.type}'")

                # search for all "assignment" type tokens
                assignments = [t for t in token_stream if t.type == "IS"]
                
                # throw an error if number of assignments in one line > 1
                if len(assignments) > 1:
                    raise ValueError(f"Invalid input: multiple assignments in one line.")
                
                elif len(assignments) == 1:
                    # assignment found — get position
                    assign_index = next(i for i, t in enumerate(token_stream) if t.type == "IS")

                    if assign_index < 2:
                        raise ValueError(f"Invalid assignment syntax.")

                    # handle int declaration: e.g. INT num IS 0
                    declared_type = None
                    if len(token_stream) >= 3 and token_stream[0].type in {"INT", "STR"}:
                        declared_type = token_stream[0].type

                    # target variable is before IS
                    target_token = token_stream[assign_index - 1]
                    target_token.name = get_token_name(target_token)
                    target_token.type = declared_type or target_token.type

                    rhs_tokens = token_stream[assign_index + 1:]

                    # evaluate RHS
                    postfix_expr = postfixer(rhs_tokens)
                    value = self.evaluate_postfix_tokens(postfix_expr)
                    target_token.value = value

                    # check if variable already exists
                    existing = next((v for v in self.saved_token_variables if v.name == target_token.name), None)
                    if existing:
                        existing.value = value
                        msg = f"Reassigned variable {target_token.name} to {target_token.value}"
                    else:
                        self.saved_token_variables.append(target_token)
                        msg = f"Added variable {target_token.name} with value {target_token.value}"

                    return restring(postfix_expr), msg
                
                # handle STR declaration
                if len(token_stream) == 2 and token_stream[0].type == "STR":
                    var_token = token_stream[1]

                    # ensure the second token is a valid identifier
                    if var_token.type != "IDENT":
                        raise ValueError(f"Syntax error: expected identifier after STR, got '{var_token.value}'")

                    # ensure variable not already declared
                    if any(v.name == var_token.value for v in self.saved_token_variables):
                        raise ValueError(f"Variable '{var_token.value}' already declared")

                    # declare string variable
                    var_token.name = var_token.value
                    var_token.type = "STR"
                    var_token.value = ""

                    self.saved_token_variables.append(var_token)
                    return f"[STR {var_token.name}]", f"Declared string variable '{var_token.name}' with default value \"\""
                
                # handle prefix operations (ADD, SUB, MULT, DIV, MOD)
                if len(token_stream) >= 3 and token_stream[0].type in {"ADD", "SUB", "MULT", "DIV", "MOD"}:
                    op_token = token_stream[0]
                    operand_tokens = token_stream[1:]

                    # exactly two operands required
                    if len(operand_tokens) != 2:
                        raise ValueError(f"Operator '{op_token.type}' requires exactly 2 operands, got {len(operand_tokens)}.")

                    # get operand values
                    values = []
                    for tok in operand_tokens:
                        if tok.type == "IDENT":
                            tok.name = getattr(tok, "name", None) or getattr(tok, "value", None)
                            existing_var = next((v for v in self.saved_token_variables if v.name == tok.name), None)
                            if not existing_var:
                                raise ValueError(f"Undefined variable '{tok.name}' used in '{op_token.type}' operation.")
                            values.append(existing_var.value)
                        elif tok.type == "INT_LIT":
                            values.append(int(tok.value))
                        else:
                            raise ValueError(f"Invalid operand '{tok.value}' for operator '{op_token.type}'.")

                # handle PRINT keyword
                elif len(token_stream) >= 2 and token_stream[0].type == "PRINT":
                    ident_token = token_stream[1]
                    ident_token.name = get_token_name(ident_token)
                    existing = next((v for v in self.saved_token_variables if v.name == ident_token.name), None)
                    if not existing:
                        raise ValueError(f"Undefined variable '{ident_token.name}'")
                    return f"[PRINT {ident_token.name}]", f"Output: {existing.value}"

                # handle BEG keyword
                elif len(token_stream) == 2 and token_stream[0].type == "BEG":
                    target_name = get_token_name(token_stream[1])
                    existing = next((v for v in self.saved_token_variables if v.name == target_name), None)
                    if not existing:
                        raise ValueError(f"Undefined variable '{target_name}' in BEG statement.")

                    # simulate user input (could later be replaced by actual input)
                    simulated_value = 0 if existing.type == "INT" else "SimulatedInput"
                    existing.value = simulated_value
                    return f"[BEG {target_name}]", f"Simulated input stored in {target_name}: {simulated_value}"

                # otherwise, treat as expression
                else:
                    postfix_expr = postfixer(token_stream)
                    result = self.evaluate_postfix_tokens(postfix_expr)
                    return restring(postfix_expr), f"Expression evaluated to {result}"

            # if code is outside IOL…LOI
            raise ValueError(f"Missing 'IOL': code must begin with IOL.")

        except Exception as e:
            # store error as an object for structured reporting
            error_obj = {
                "line": line_number,
                "message": str(e),
                "tokens": restring(token_stream)
            }
            self.errors.append(error_obj)

            return f"Error processing: {token_stream}", f"Error on line {line_number}: {e}"