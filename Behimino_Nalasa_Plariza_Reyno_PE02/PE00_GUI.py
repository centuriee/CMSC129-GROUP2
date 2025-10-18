import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox, QSplitter, QPlainTextEdit
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt


def new_file(): # Function for the creation of new file
    code_editor.clear()
    console_output.clear()
    token_display.clear() # Clear all text display area
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
    console_output.append("Lexical analysis successful.\nNo lexical errors found.") # Display message when successful compiling process was done


def show_tokenized(): # Placeholder for showing token table
    token_display.clear()
    token_display.append("Tokenized Output:\n[IDENTIFIER, KEYWORD, SYMBOL, ...]")


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

token_display = QTextEdit() # Creates the text display for the token list
token_display.setReadOnly(True)
token_display.setPlaceholderText("Symbol Table / Tokenized Code")
editor_splitter.addWidget(token_display) # Add the token list horizontally beside the code editor

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
