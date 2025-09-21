import sys
import re

from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit,
    QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox
)
from utils.postfixer import restring, postfixer
from utils.lexer import Lexer
from utils.processor import Processor


class ExpressionProcessor:
    def __init__(self):
        self.variables = {}
        self.saved_token_variables = []
        self.errors = []
        self.used_variables = set()
    
    def is_valid_variable(self, var_name):
        """Check if variable name follows C naming rules (no underscore, no keywords)"""
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', var_name):
            return False
        
        # C keywords to check against
        keywords = {
            "int", "float", "char", "double", "if", "else", "while",
            "for", "return", "void", "struct", "break", "continue"
        }
        return var_name not in keywords
    
    def tokenize_expression(self, expression):
        """Tokenize expression into numbers, variables, and operators"""
        tokens = []
        pattern = r'(\d+\.?\d*|\.\d+|[a-zA-Z][a-zA-Z0-9]*|[+\-*/%()]|\S)'
        
        for match in re.finditer(pattern, expression):
            token = match.group().strip()
            if token:
                tokens.append(token)
        return tokens
    
    def infix_to_postfix(self, tokens):
        """Convert infix expression to postfix notation"""
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2}
        output = []
        operators = []
        
        for token in tokens:
            if re.match(r'^\d+\.?\d*$', token):  # Number
                output.append(token)
            elif re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', token):  # Variable
                output.append(token)
                self.used_variables.add(token)
            elif token in precedence:  # Operator
                while (operators and operators[-1] != '(' and
                       operators[-1] in precedence and
                       precedence[operators[-1]] >= precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if operators:
                    operators.pop()  # Remove '('
        
        while operators:
            output.append(operators.pop())
        
        return output
    
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

    def evaluate_postfix(self, postfix_tokens):
        """Evaluate postfix expression"""
        stack = []
        
        for token in postfix_tokens:
            if re.match(r'^\d+\.?\d*$', token):  # Number
                stack.append(float(token))
            elif re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', token):  # Variable
                if token not in self.variables:
                    raise ValueError(f"Undefined variable {token}")
                stack.append(self.variables[token])
            elif token in ['+', '-', '*', '/', '%']:
                if len(stack) < 2:
                    raise ValueError("Invalid expression")
                
                b = stack.pop()
                a = stack.pop()
                
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ZeroDivisionError("Division by zero")
                    stack.append(a / b)
                elif token == '%':
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
                        return postfixer(token_stream[2:]), f"Reassigned variable {token.name} to {token.value}"
                
                self.saved_token_variables.append(target_token)
                return postfixer(token_stream[2:]), f"Added variable {target_token.name} with value {target_token.value}"
            else:
                return postfixer(token_stream), self.evaluate_postfix_tokens(postfixer(token_stream))
        
        except Exception as e:
            self.errors.append(f"Invalid input code: {restring(token_stream)}")
            return f"Error processing {token_stream}", f"Error processing: {token_stream}"

    def process_line(self, line):
        """Process a single line of code"""
        line = line.strip()
        if not line:
            return None
        
        try:
            # Check if it's an assignment statement
            if '=' in line:
                parts = line.split('=', 1)
                if len(parts) != 2:
                    raise ValueError("Invalid input code")
                
                var_name = parts[0].strip()
                expression = parts[1].strip()
                
                if not self.is_valid_variable(var_name):
                    raise ValueError("Invalid variable name")
                
                # Process expression
                tokens = self.tokenize_expression(expression)
                postfix = self.infix_to_postfix(tokens)
                
                try:
                    result = self.evaluate_postfix(postfix)
                    self.variables[var_name] = result
                    self.used_variables.add(var_name)
                    
                    # Format output
                    postfix_str = ' '.join(postfix)
                    result_line = f"{var_name} = {result}"
                    
                    return postfix_str, result_line
                    
                except ZeroDivisionError as e:
                    # Keep previous value if exists
                    self.errors.append(str(e))
                    postfix_str = ' '.join(postfix)
                    if var_name in self.variables:
                        result_line = f"{var_name} = {self.variables[var_name]} (previous value retained)"
                    else:
                        result_line = f"{var_name} = undefined (division by zero)"
                    return postfix_str, result_line
                    
            else:
                # It's just an expression
                tokens = self.tokenize_expression(line)
                postfix = self.infix_to_postfix(tokens)
                result = self.evaluate_postfix(postfix)
                
                postfix_str = ' '.join(postfix)
                result_line = str(result)
                
                return postfix_str, result_line
                
        except Exception as e:
            self.errors.append(f"Invalid input code: {line}")
            return f"Error processing: {line}", "Invalid"


def main_window():
   
    window = QWidget() #Create main window for GUI
    window.setWindowTitle("PE00: Expression Evaluation")
    window.resize(800, 400)

   
    input_text = QTextEdit() #Defines text area for input
    input_text.setPlaceholderText("Input Text Area")

    load_button = QPushButton("Load File") #Creates Button for load file

    def load_file(): # Function to load an input file when load button is interacted
        file_name, _ = QFileDialog.getOpenFileName(
            window,
            "Open Input File",
            "",
            "Input Files (*.in);;All Files (*)" #Filters files visible to be of .in extension
        )
        if file_name:  
            if file_name.endswith(".in"): #
                try:
                    with open(file_name, "r", encoding="utf-8") as f: #Reads the file contents when selected
                        lines = f.readlines()
                        input_text.setPlainText("".join(lines))  #Displays file contents in the input text area
                except Exception as e:
                    QMessageBox.critical(window, "Error", f"Failed to load file:\n{e}") #Error trap when file is not loaded properly
    load_button.clicked.connect(load_file)

    input_layout = QVBoxLayout() #Creates vertical box layout for the definition of input layout
    input_layout.addWidget(input_text)
    input_layout.addWidget(load_button)

    output_text = QTextEdit() #Defines text area for output
    output_text.setPlaceholderText("Output Text Area")
    output_text.setReadOnly(True)

    process_button = QPushButton("Process") #Creates Button for the process operation

    def process_text():
        """Process the input text according to specification"""
        input_content = input_text.toPlainText().strip()

        if not input_content:
            QMessageBox.warning(window, "Warning", "Please enter some text to process!")
            return

        try:
            lexer = Lexer(input_content)
            token_stream = lexer.tokenize()

            processor = Processor()
            output_content = ""
            lines = input_content.split('\n')
            
            # Process each line
            for line in lines:
                if line.strip():
                    lexer = Lexer(line)
                    token_stream = lexer.tokenize()
                    print(token_stream)

                    postfixed, evaluation = processor.process_tokens(token_stream)
                    if token_stream:
                        output_content += f"Line: {line.strip()}\n"
                        output_content += f"Postfix: {postfixed}\n"
                        output_content += f"Result: {evaluation}\n"
                        
                    '''
                    if result:
                        postfix, evaluation = result
                        output_content += f"Result: {evaluation}\n\n"
                    '''
            
            # Add separator line
            output_content += "-" * 40 + "\n"
            
            # Add variables used section
            output_content += "Variables used:\n"
            for var in processor.saved_token_variables:
                output_content += f"{var.name}: {var.value}\n"

            output_content += "-" * 40 + "\n"
            
            # Add errors section
            output_content += "Errors found:\n"
            if processor.errors:
                for error in processor.errors:
                    output_content += f"{error}\n"
            else:
                output_content += "None\n"
            
            # Display results
            output_text.setPlainText(output_content)

        except Exception as e:
            QMessageBox.critical(window, "Processing Error", f"An error occurred while processing:\n{e}")

    process_button.clicked.connect(process_text)

    output_layout = QVBoxLayout() #Creates vertical box layout for the definition of output layout
    output_layout.addWidget(output_text)
    output_layout.addWidget(process_button)


    main_layout = QHBoxLayout()  #Displays the left and right layout side by side
    main_layout.addLayout(input_layout)
    main_layout.addLayout(output_layout)

    window.setLayout(main_layout)
    return window

if __name__ == "__main__": #Creates the GUI application when program is run
    app = QApplication(sys.argv)
    win = main_window() #Displays the GUI window
    win.show()
    sys.exit(app.exec())