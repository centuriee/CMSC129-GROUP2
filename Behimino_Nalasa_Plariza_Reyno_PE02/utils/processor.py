import sys
import re

from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit,
    QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
)

from utils.postfixer import restring, postfixer
from utils.lexer import Lexer


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

    def process_tokens(self, token_stream):
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

                # search for all "assignment" type tokens
                assignments = [t for t in token_stream if t.type == "IS"]
                
                # throw an error if number of assignments in one line > 1
                if len(assignments) > 1:
                    raise ValueError(f"Invalid input — multiple assignments in one line.")
                
                elif len(assignments) == 1:
                    # assignment found — get position
                    assign_index = next(i for i, t in enumerate(token_stream) if t.type == "IS")

                    if assign_index < 2:
                        raise ValueError(f"Invalid assignment syntax.")

                    # target variable is before IS
                    target_token = token_stream[assign_index - 1]

                    # ensure variable name is extracted properly
                    target_token.name = get_token_name(target_token)

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

                # handle PRINT keyword
                elif len(token_stream) >= 2 and token_stream[0].type == "PRINT":
                    ident_token = token_stream[1]
                    ident_token.name = get_token_name(ident_token)
                    existing = next((v for v in self.saved_token_variables if v.name == ident_token.name), None)
                    if not existing:
                        raise ValueError(f"Undefined variable '{ident_token.name}'")
                    return f"[PRINT {ident_token.name}]", f"Output: {existing.value}"

                # otherwise, treat as expression
                else:
                    postfix_expr = postfixer(token_stream)
                    result = self.evaluate_postfix_tokens(postfix_expr)
                    return restring(postfix_expr), f"Expression evaluated to {result}"

            # if code is outside IOL…LOI
            raise ValueError(f"Missing 'IOL': code must begin with IOL.")

        except Exception as e:
            # save error for review and return message
            self.errors.append(str(e))
            self.errors.append(f"Invalid input code: {restring(token_stream)}")
            # fix: show error on this line, not delayed
            return f"Error processing: {token_stream}", f"Error: {e}"

