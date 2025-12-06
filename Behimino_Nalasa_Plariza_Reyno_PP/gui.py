import os
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox, QSplitter, QPlainTextEdit,
    QLabel, QTableWidget, QHeaderView, QTableWidgetItem
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from utils.file_operations import new_file, open_file, save_file, save_file_as, show_tokenized, compile_code

class MainWindow(QMainWindow):
    def __init__(self, main_dir = None):
        super().__init__()
        self.current_file = None  # Track currently opened file path
        self.main_dir = main_dir or os.getcwd()
        self.setup_UI()
        self.create_menus()

    def setup_UI(self):
            self.setWindowTitle("Lexical Analyzer")
            self.resize(1000, 700)

            self.central_widget = QWidget() # Creates widget to hold the main components
            self.main_layout = QVBoxLayout(self.central_widget)
            self.setCentralWidget(self.central_widget)

            self.main_splitter = QSplitter(Qt.Vertical) # Split the code editor and console vertically

            self.editor_splitter = QSplitter(Qt.Horizontal) # Split the code editor and token list horizontally

            self.code_editor = QPlainTextEdit() # Creates the text editor
            self.code_editor.setPlaceholderText("Write your source code here...")
            self.editor_splitter.addWidget(self.code_editor) # Adds the code editor to the horizontal split

            self.variable_label = QLabel("Potential Detected Variable Table")
            self.variable_table = QTableWidget(0, 2)
            self.variable_table.setHorizontalHeaderLabels(["Type", "Name"])
            self.variable_table.verticalHeader().setVisible(False)
            self.variable_table.setEditTriggers(QTableWidget.NoEditTriggers)
            self.variable_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.editor_splitter.addWidget(self.variable_table) # Add the variable table beside the code editor

            self.console_output = QTextEdit() # Creates the console display
            self.console_output.setReadOnly(True)
            self.console_output.setPlaceholderText("Compilation / Runtime Output...") 

            self.main_splitter.addWidget(self.editor_splitter) # Creates the horizontal top section split
            self.main_splitter.addWidget(self.console_output) # Creates the vertical section split with the console section at the bottom

            self.main_splitter.setStretchFactor(0, 3)
            self.main_splitter.setStretchFactor(1, 1)

            self.main_layout.addWidget(self.main_splitter) # Add all the split section in to the main window of GUI

    def create_menus(self):
            self.menu_bar = self.menuBar() # Creates the menu bar

            self.file_menu = self.menu_bar.addMenu("File") # Adds the file operations to the menu bar

            self.new_action = QAction("New File", self) # Creates option New file 
            self.new_action.triggered.connect(self.new_file) # Connects it with the new_file function when interacted
            self.file_menu.addAction(self.new_action)

            self.open_action = QAction("Open File", self) # Creates option OPen file 
            self.open_action.triggered.connect(self.open_file) # Connects it with the open_file function when interacted
            self.file_menu.addAction(self.open_action)

            self.save_action = QAction("Save", self) # Creates option Save file 
            self.save_action.triggered.connect(self.save_file) # Connects it with the save_file function when interacted
            self.file_menu.addAction(self.save_action)

            self.save_as_action = QAction("Save As", self) # Creates option Save As file 
            self.save_as_action.triggered.connect(self.save_file_as) # Connects it with the save_file_as function when interacted
            self.file_menu.addAction(self.save_as_action)

            self.compile_menu = self.menu_bar.addMenu("Compile") # Adds the compile operations to the menu bar

            self.compile_action = QAction("Compile Code", self) # Creates option for Compile operation of code
            self.compile_action.triggered.connect(self.compile_code)  # Connects it with the compile_code function when interacted
            self.compile_menu.addAction(self.compile_action)

            self.show_tokens_action = QAction("Show Tokenized Code", self) # Creates option for show token list of code
            self.show_tokens_action.triggered.connect(self.show_tokenized)  # Connects it with the show_tokenized function when interacted
            self.compile_menu.addAction(self.show_tokens_action)


            self.exec_menu = self.menu_bar.addMenu("Execute") # Adds the execute operation to the menu bar for later implementation of syntax analysis


    def new_file(self): 
        new_file(self)

    def open_file(self): 
        open_file(self)

    def save_file(self): 
        save_file(self)

    def save_file_as(self): 
        save_file_as(self)
        
    def show_tokenized(self):
        show_tokenized(self)

    def compile_code(self):
        compile_code(self)