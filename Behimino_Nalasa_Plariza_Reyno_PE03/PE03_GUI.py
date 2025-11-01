from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QGroupBox, QInputDialog
)
import csv, sys, os

# Global variable for input file tracking
prod_file = None
ptbl_file = None

def load_file(): # Function for the loading of input files
    global prod_file, ptbl_file
    file_path, _ = QFileDialog.getOpenFileName(window, "Select File", "", "CSV Files (*.prod *.ptbl)")
    if not file_path:
        QMessageBox.information(window, "Cancelled", "File loading cancelled.")
        return

    file_name = os.path.basename(file_path)
    loaded_label.setText(f"LOADED: {file_name}")

    if file_path.endswith(".prod"):
        prod_file = file_path
        prod_label.setText(f"Productions: {file_name}")
        load_csv_to_table(prod_table, file_path)

    elif file_path.endswith(".ptbl"):
        ptbl_file = file_path
        ptbl_label.setText(f"Parse Table: {file_name}")
        load_csv_to_table(parse_table, file_path)
    else:
        QMessageBox.warning(window, "Invalid File", "Please select a .prod or .ptbl file.")
        return

    # Enable Parse button if both files are loaded
    if prod_file and ptbl_file:
        parse_button.setEnabled(True)

def load_csv_to_table(table_widget, file_path): # Display CSV contents to each corresponding table displays
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

    if not data:
        return

    table_widget.setRowCount(len(data))
    table_widget.setColumnCount(len(data[0]))
    for r, row in enumerate(data):
        for c, cell in enumerate(row):
            table_widget.setItem(r, c, QTableWidgetItem(cell.strip()))
    table_widget.resizeColumnsToContents()

def parse_input(): # Implements the parse logic based on the entered token sequence
    tokens = input_field.text().strip()
    if not tokens:
        QMessageBox.warning(window, "Missing Input", "Please enter a token sequence.")
        return

    # Parsing logic
    steps = [

    ]

    parsing_table.setRowCount(len(steps))
    parsing_table.setColumnCount(3)
    parsing_table.setHorizontalHeaderLabels(["STACK", "INPUT", "ACTION"]) # Populate the table with the data row by row
    for i, (stack, inp, act) in enumerate(steps):
        parsing_table.setItem(i, 0, QTableWidgetItem(stack))
        parsing_table.setItem(i, 1, QTableWidgetItem(inp))
        parsing_table.setItem(i, 2, QTableWidgetItem(act))

    parsing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # result_label.setText("PARSING: Valid. Please see test_rules.prsd.")  # Parsing Validation Logic
    result_label.setStyleSheet("font-weight: bold; color: green;")

app = QApplication(sys.argv) # Initializes the application
window = QWidget() # Creates the main application window
window.setWindowTitle("Non-Recursive Predictive Parser")
window.setMinimumSize(950, 700)

main_layout = QVBoxLayout() 

tables_layout = QHBoxLayout() # Horizontal layout for the tables to be displayed side by side

prod_box = QGroupBox("Productions") # Creates the section for the table display of Grammar Productions
prod_layout = QVBoxLayout()
prod_label = QLabel("Productions: None")
prod_table = QTableWidget()
prod_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
prod_layout.addWidget(prod_label)
prod_layout.addWidget(prod_table)
prod_box.setLayout(prod_layout)

parse_box = QGroupBox("Parse Table") # Creates the section for the table display of Parse Table
parse_layout = QVBoxLayout()
ptbl_label = QLabel("Parse Table: None")
parse_table = QTableWidget()
parse_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
parse_layout.addWidget(ptbl_label)
parse_layout.addWidget(parse_table)
parse_box.setLayout(parse_layout)

tables_layout.addWidget(prod_box) # Displays both tables horizontally side by side
tables_layout.addWidget(parse_box)

load_layout = QHBoxLayout() # Creates the button for the loading operation of files
loaded_label = QLabel("LOADED: None")
load_button = QPushButton("Load")
load_button.clicked.connect(load_file)
load_layout.addWidget(loaded_label)
load_layout.addWidget(load_button)

input_layout = QHBoxLayout() # Creates the text area for the initialization of parse operation
input_label = QLabel("INPUT:")
input_field = QLineEdit()
input_field.setPlaceholderText("Enter token sequence")
parse_button = QPushButton("Parse")
parse_button.setEnabled(False)
parse_button.clicked.connect(parse_input)
input_layout.addWidget(input_label)
input_layout.addWidget(input_field)
input_layout.addWidget(parse_button)

result_label = QLabel("PARSING: Not started.") 
result_label.setStyleSheet("font-weight: bold; color: #007acc;")

parsing_table = QTableWidget() # Creates table display for the parsing result table
parsing_table.setColumnCount(3)
parsing_table.setHorizontalHeaderLabels(["STACK", "INPUT BUFFER", "ACTION"])
parsing_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
parsing_table.verticalHeader().setVisible(False)

main_layout.addLayout(tables_layout)  # Adds all created components and arranged it in the main application
main_layout.addLayout(load_layout)
main_layout.addLayout(input_layout)
main_layout.addWidget(result_label)
main_layout.addWidget(parsing_table)

window.setLayout(main_layout)
window.show()
sys.exit(app.exec())
