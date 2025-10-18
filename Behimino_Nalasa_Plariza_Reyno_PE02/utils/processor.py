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
    
    # rewrote evaluate_postfix to work with gian's tokens
    def evaluate_postfix_tokens(self, postfix_tokens):
        stack = []

        for token in postfix_tokens:
            if token.type == "NUMBER":
                stack.append(float(token.value))
            elif token.type == "VARIABLE":
                found_token = None
                for saved in self.saved_token_variables:
                    if saved.name == token.name:
                        found_token = saved
                
                if found_token is None:
                    raise ValueError(f"Undefined variable {token.name}")
                
                stack.append(float(found_token.value))
            elif token.type == "OPERATOR":
                if len(stack) < 2:
                    raise ValueError("Invalid Expression")
                
                b = stack.pop()
                a = stack.pop()
                
                if token.value == '+':
                    stack.append(a + b)
                elif token.value == '-':
                    stack.append(a - b)
                elif token.value == '*':
                    stack.append(a * b)
                elif token.value == '/':
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    stack.append(a / b)
                elif token.value == '%':
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    stack.append(a % b)
                
        if len(stack) != 1:
            raise ValueError("Invalid expression")
    
        return stack[0]

    def process_tokens(self, token_stream):
        try:
            # search for all "assignment" type tokens
            assignments = list(filter(lambda x: x.type == "ASSIGNMENT", token_stream))
            
            # throw an error if number of assignments in one line > 1
            if len(assignments) > 1:
                raise ValueError("Invalid input code")
            elif len(assignments) == 1:
                # assignment is not in the right position
                if token_stream.index(assignments[0]) != 1:
                    raise ValueError("Invalid input code")
                
                # NOTE: LATER, THIS NEEDS TO BE REWORKED. 
                # NO SCOPE SAVED SO ITS ALL GOING TO REPLACE EACH OTHER

                # search saved variables and see if existing token
                target_token = token_stream[0]
                target_token.value = self.evaluate_postfix_tokens(postfixer(token_stream[2:]))
                for token in self.saved_token_variables:
                    if token.name == target_token.name:
                        token.value = target_token.value
                        return restring(postfixer(token_stream[2:])), f"Reassigned variable {token.name} to {token.value}"
                
                self.saved_token_variables.append(target_token)
                return restring(postfixer(token_stream[2:])), f"Added variable {target_token.name} with value {target_token.value}"
            else:
                return restring(postfixer(token_stream)), self.evaluate_postfix_tokens(postfixer(token_stream))
        
        except Exception as e:
            self.errors.append(str(e))
            self.errors.append(f"Invalid input code: {restring(token_stream)}")
            return f"Error processing: {token_stream}", f"Error processing: {token_stream}"
