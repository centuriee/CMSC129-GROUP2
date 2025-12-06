import os
import sys
from PySide6.QtWidgets import QFileDialog, QMessageBox
from utils.lexer import Lexer
from utils.parser import Parser


def new_file(main_window): # Function for the creation of new file
    main_window.code_editor.clear()
    main_window.console_output.clear()
    main_window.variable_table.clear() # clear all text display area
    main_window.variable_table.setHorizontalHeaderLabels(["Type", "Name"]) # add headers again
    main_window.setWindowTitle("Lexical Analyzer - New File") 
    main_window.current_file = None  # Removes any reference to a file, new file output is saved when save option is selected


def open_file(main_window): # Opens file with .iol extension
    file_path, _ = QFileDialog.getOpenFileName(main_window, "Open Source File", "", "Source Files (*.iol)")
    if file_path:
        with open(file_path, "r") as f:
            main_window.code_editor.setPlainText(f.read()) # Load the file contents into the code editor
        main_window.setWindowTitle(f"Lexical Analyzer - {file_path}")
        main_window.current_file = file_path # Sets reference to current open file


def save_file(main_window): # Function for the saving of the current file
    if not main_window.current_file:
        save_file_as(main_window) # Calls save as function if no open file reference has been made
        return
    with open(main_window.current_file, "w") as f:
        f.write(main_window.code_editor.toPlainText()) # Write contents of the editor to the current file
    main_window.console_output.append("File saved successfully.")


def save_file_as(main_window):
    file_path, _ = QFileDialog.getSaveFileName(main_window, "Save Source File", main_window.main_dir, "Source Files (*.iol)")  # Prompts user to select the destination of the current file
    if file_path:
        main_window.current_file = file_path  # Sets reference to current save as file
        save_file(main_window)
    
def show_tokenized(main_window):
    main_window.variable_table.clear()
    main_window.variable_table.setHorizontalHeaderLabels(["Type", "Name"]) # add headers again
    """Process the input text according to specification"""
    input_content = main_window.code_editor.toPlainText().strip()
    if not input_content:
        QMessageBox.warning(main_window, "Warning", "Please enter some text to process!")
        return

    try:
        lines = input_content.split('\n')
        output_content = ""

        error_lexes = []
        for line_no, line in enumerate(lines):
            print(line)
            lexer = Lexer(line)
            token_stream = lexer.tokenize()

            for token in token_stream:
                if token.name is None:
                    output_content += f"({token.type}, {token.value})"
                else:
                    output_content += f"({token.type}, {token.name}, {token.value})"
            
            output_content += "\n" # newline for clean printing
            #Haskel's line processing comment moved to compile_code function

        output_path = os.path.join(main_window.main_dir, "tokens.tkn")
        with open(output_path, "w", encoding = "utf-8") as f:
            f.write(output_content)

        QMessageBox.information(main_window, "Success", f"Tokenized output saved to:\n{output_path}")

    except Exception as e:
        QMessageBox.critical(main_window, "Processing Error", f"An error occurred while processing:\n{e}")

def compile_code(main_window):
    # (1) RUN LEXER
    main_window.variable_table.clear()
    main_window.variable_table.setHorizontalHeaderLabels(["Type", "Name"]) # add headers again
    main_window.console_output.clear()

    """Process the input text according to specification"""
    input_content = main_window.code_editor.toPlainText().strip()
    if not input_content:
        QMessageBox.warning(main_window, "Warning", "Please enter some text to process!")
        return

    try:
        lines = input_content.split('\n')
        lexical_errors = []
        lexer_output = ""
        
        for line_no, line in enumerate(lines):
            print(line)
            lexer = Lexer(line)
            token_stream = lexer.tokenize()

            for token in token_stream:
                if token.name is None:
                    lexer_output += f"({token.type}, {token.value})"
                else:
                    lexer_output += f"({token.type}, {token.name}, {token.value})"
            
            lexer_output += "\n" # newline for clean printing

            # lexical error detector
            if token.type == "ERR_LEX":
                lexical_errors.append(
                    f"Line {line_no + 1}: Invalid token '{token.value}'"
                )

        # lexical error checker
        if lexical_errors:
            main_window.console_output.clear()
            main_window.console_output.append(
                "Lexical analysis failed:<br>" + "<br>".join(lexical_errors)
            )
            return
        
        else:
            main_window.console_output.append("Lexical analysis successful!")
            # save tokens.tkn
            output_path = os.path.join(main_window.main_dir, "tokens.tkn")

            with open(output_path, "w", encoding = "utf-8") as f:
                f.write(lexer_output)


    except Exception as e:
        QMessageBox.critical(main_window, "Processing Error", f"An error occurred while processing:\n{e}")

    # (2) RUN PARSER
    parser = Parser(True, main_window = main_window)  # Pass main_window reference to parser
    if parser.semantic_errors:
        main_window.console_output.append("Parsing failed:")
        for err in parser.semantic_errors:
            main_window.console_output.append(err)
        return
    else:
        main_window.console_output.append("Parsing successful!")

    # (3) "EXECUTE" PROGRAM
    parser = Parser(False, main_window = main_window)  # Pass main_window reference to parser
    if parser.semantic_errors:
        main_window.console_output.append("Execution failed:")
        for err in parser.semantic_errors:
            main_window.console_output.append(err)
    else:
        main_window.console_output.append("Program Terminated")