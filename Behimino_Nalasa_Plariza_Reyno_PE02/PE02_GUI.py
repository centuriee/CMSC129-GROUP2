"""
!!!--- RECENT CHANGES ---!!!
As of Oct 19 - 12:22PM:
1. renamed and moved main file from main.py to expressionProcessor.py
2. GUI removed in this file. Integrated the new GUI to current code
3. Haskel's commmented code moved to compile_code() function in PE02_GUI.py ---> Reason: ExpressionProcessor is needed there.
4. token stream output moved and integrated to show_tokenized() function in PE02_GUI.py

Missing code functions:
1. Haskel's commmented code in compile_code() function in PE02_GUI.py has been integrated, but was only tested on error input code.
2. Need general checking of new changes. 
3. Table of variables section might need an actual table output similar to previous PEs.

Commented by: King (KanadeTachie)
CHANGE THIS PART AS NEEDED. 
Reduces time trying to find what was changed and what else is missing.
"""
# shouldn't this be a commit description? - Haskel (One-L)

import os
import sys
import re
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox, QSplitter, QPlainTextEdit,
    QLabel, QTableWidget, QHeaderView, QTableWidgetItem
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from utils.postfixer import restring, postfixer
from utils.lexer import Lexer
from utils.processor import Processor
from utils.expressionProcessor import ExpressionProcessor


def new_file(): # Function for the creation of new file
    code_editor.clear()
    console_output.clear()
    variable_table.clear() # Clear all text display area
    window.setWindowTitle("Lexical Analyzer - New File") 
    globals()['current_file'] = None  # Removes any reference to a file, new file output is saved when save option is selected


def open_file(): # Opens file with .iol extension
    file_path, _ = QFileDialog.getOpenFileName(window, "Open Source File", "", "Source Files (*.iol)")
    if file_path:
        with open(file_path, "r") as f:
            code_editor.setPlainText(f.read()) # Load the file contents into the code editor
        window.setWindowTitle(f"Lexical Analyzer - {file_path}")
        globals()['current_file'] = file_path # Sets reference to current open file


def save_file(): # Function for the saving of the current file
    if not globals().get('current_file'):
        save_file_as() # Calls save as function if no open file reference has been made
        return
    with open(globals()['current_file'], "w") as f:
        f.write(code_editor.toPlainText()) # Write contents of the editor to the current file
    console_output.append("File saved successfully.")


def save_file_as(): 
    file_path, _ = QFileDialog.getSaveFileName(window, "Save Source File", "", "Source Files (*.iol)") # Prompts user to select the destination of the current file
    if file_path:
        globals()['current_file'] = file_path  # Sets reference to current save as file
        save_file()


def compile_code(): # Initializes the compiling process of the code
    source = code_editor.toPlainText()
    if not source.strip():
        QMessageBox.warning(window, "Error", "No code to compile.") # Shows error message if code editor is empty
        return
    console_output.append("Compiling code...")

    input_content = code_editor.toPlainText().strip()
    processor = Processor()
    output_content = ""
    lines = input_content.split('\n')

    # Process each line
    line_number = 1
    for line in lines:
        if line.strip():
            lexer = Lexer(line)
            token_stream = lexer.tokenize()
            print(token_stream)

            postfixed, evaluation = processor.process_tokens(token_stream, line_number)
            if token_stream:
                output_content += f"Line {line_number}: {line.strip()}\n"
                output_content += f"Postfix: {postfixed}\n"
                output_content += f"Result: {evaluation}\n"
        line_number += 1

    if processor.in_block:
        processor.errors.append({
            "line": len(lines),
            "message": "Missing 'LOI': program block was never closed.",
            "tokens": "EOF"
        })
    
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
            output_content += f"Line {error['line']}: {error['message']}\n"
    else:
        output_content += "None\n"

    if not processor.errors:
        console_output.setPlainText("Code compiled successfully!")
        # --- Update variable (symbol) table ---
        variable_table.setRowCount(0)  # Clear old entries
        for var in processor.saved_token_variables:
            row = variable_table.rowCount()
            variable_table.insertRow(row)
            variable_table.setItem(row, 0, QTableWidgetItem(getattr(var, "type", "UNKNOWN")))
            variable_table.setItem(row, 1, QTableWidgetItem(getattr(var, "name", "UNKNOWN")))
            variable_table.setItem(row, 2, QTableWidgetItem(str(getattr(var, "value", "None"))))

    else:
        error_display = "Compilation failed. Errors found:\n\n"
        for error in processor.errors:
            error_display += f"Line {error['line']}: {error['message']}\n"
        
        console_output.setPlainText(error_display)
    
def show_tokenized():
    variable_table.clear()
    """Process the input text according to specification"""
    input_content = code_editor.toPlainText().strip()
    if not input_content:
        QMessageBox.warning(window, "Warning", "Please enter some text to process!")
        return

    try:
        lines = input_content.split('\n')
        output_content = ""

        for line in lines:
            print(line)
            lexer = Lexer(line)
            token_stream = lexer.tokenize()

            for token in token_stream:
                output_content += f"({token.type}, {token.value})"
            
            output_content += "\n" # newline for clean printing
            #Haskel's line processing comment moved to compile_code function

        if getattr(sys, 'frozen', False):
            # Running as compiled .exe
            script_dir = os.path.dirname(sys.executable)
        else:
            # Running as normal Python script
            script_dir = os.path.dirname(os.path.abspath(__file__))

        output_path = os.path.join(script_dir, "tokens.tkn")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_content)

        QMessageBox.information(window, "Success", f"Tokenized output saved to:\n{output_path}")

    except Exception as e:
        QMessageBox.critical(window, "Processing Error", f"An error occurred while processing:\n{e}")


app = QApplication(sys.argv) # Initialize main application
window = QMainWindow() # Creates the main window of the GUI
window.setWindowTitle("Lexical Analyzer")
window.resize(1000, 700)

central_widget = QWidget() # Creates widget to hold the main components
main_layout = QVBoxLayout(central_widget)
window.setCentralWidget(central_widget)

main_splitter = QSplitter(Qt.Vertical) # Split the code editor and console vertically

editor_splitter = QSplitter(Qt.Horizontal) # Split the code editor and token list horizontally

code_editor = QPlainTextEdit() # Creates the text editor
code_editor.setPlaceholderText("Write your source code here...")
editor_splitter.addWidget(code_editor) # Adds the code editor to the horizontal split

variable_label = QLabel("Variable Table")
variable_table = QTableWidget(0, 3)
variable_table.setHorizontalHeaderLabels(["Type", "Name", "Value"])
variable_table.verticalHeader().setVisible(False)
variable_table.setEditTriggers(QTableWidget.NoEditTriggers)
variable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
editor_splitter.addWidget(variable_table) # Add the variable table beside the code editor

console_output = QTextEdit() # Creates the console display
console_output.setReadOnly(True)
console_output.setPlaceholderText("Compilation / Runtime Output...") 

main_splitter.addWidget(editor_splitter) # Creates the horizontal top section split
main_splitter.addWidget(console_output) # Creates the vertical section split with the console section at the bottom

main_splitter.setStretchFactor(0, 3)
main_splitter.setStretchFactor(1, 1)

main_layout.addWidget(main_splitter) # Add all the split section in to the main window of GUI
current_file = None # Track currently opened file path

menu_bar = window.menuBar() # Creates the menu bar

file_menu = menu_bar.addMenu("File") # Adds the file operations to the menu bar

new_action = QAction("New File", window) # Creates option New file 
new_action.triggered.connect(new_file) # Connects it with the new_file function when interacted
file_menu.addAction(new_action)

open_action = QAction("Open File", window) # Creates option OPen file 
open_action.triggered.connect(open_file) # Connects it with the open_file function when interacted
file_menu.addAction(open_action)

save_action = QAction("Save", window) # Creates option Save file 
save_action.triggered.connect(save_file) # Connects it with the save_file function when interacted
file_menu.addAction(save_action)

save_as_action = QAction("Save As", window) # Creates option Save As file 
save_as_action.triggered.connect(save_file_as) # Connects it with the save_file_as function when interacted
file_menu.addAction(save_as_action)

compile_menu = menu_bar.addMenu("Compile") # Adds the compile operations to the menu bar

compile_action = QAction("Compile Code", window) # Creates option for Compile operation of code
compile_action.triggered.connect(compile_code)  # Connects it with the compile_code function when interacted
compile_menu.addAction(compile_action)

show_tokens_action = QAction("Show Tokenized Code", window) # Creates option for show token list of code
show_tokens_action.triggered.connect(show_tokenized)  # Connects it with the show_tokenized function when interacted
compile_menu.addAction(show_tokens_action)


exec_menu = menu_bar.addMenu("Execute") # Adds the execute operation to the menu bar for later implementation of syntax analysis

window.show() # Display the main application window
sys.exit(app.exec())

if __name__ == "__main__": #Creates the GUI application when program is run
    app = QApplication(sys.argv)
    win = main_window() #Displays the GUI window
    win.show()
    sys.exit(app.exec())
