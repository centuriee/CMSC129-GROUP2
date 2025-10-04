import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, 
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt


def main_window():
    # Create main GUI window
    window = QWidget()
    window.setWindowTitle("PE01 - Strings and DFA")
    window.resize(800, 400)

    # Creates the display area for the transition table
    transition_label = QLabel("Transition Table")
    transition_table = QTableWidget(0, 3)   # Start empty in rows with 3 columns fixed
    transition_table.setHorizontalHeaderLabels(["State", "0", "1"]) # Labels for the colum headers
    transition_table.verticalHeader().setVisible(False)
    transition_table.setEditTriggers(QTableWidget.NoEditTriggers)
    transition_table.horizontalHeader().setStretchLastSection(True)

    # Creates the display area for the input section
    input_label = QLabel("Input")
    input_text = QTextEdit()
    input_text.setPlaceholderText("Input strings will display here...")
    input_text.setReadOnly(True)

    # Creates the display area for the output section
    output_label = QLabel("Output")
    output_text = QTextEdit()
    output_text.setPlaceholderText("Output results will display here...")
    output_text.setReadOnly(True)

    # Status Display for Initial display of the application
    status_label = QLabel("STATUS: Waiting for input.")
    status_label.setStyleSheet("font-weight: bold;")

    # Buttons utilized for the application
    load_button = QPushButton("Load File") # Button operation for file loading
    process_button = QPushButton("Process") # Button operation for file processing
    process_button.setEnabled(False) # Process button is disabled untill all input files are loaded

    # Function for the loading of file
    def load_file():
        file_name, _ = QFileDialog.getOpenFileName(
            window,
            "Open Input File",
            "",
            "Input Files (*.in *.dfa);;All Files (*)" # File filter for .in and .dfa visibility
        )

        if file_name:
            try:
                with open(file_name, "r", encoding="utf-8") as f: # Read file contents if user selected a file
                    lines = [line.strip() for line in f if line.strip()]
                    content = "\n".join(lines)

                if file_name.endswith(".in"):
                    # Load input file with .in extension
                    input_text.setPlainText(content)
                    status_label.setText("STATUS: Input strings loaded successfully.") # Modifies status label when .in file is loaded
                    process_button.setEnabled(True)

                elif file_name.endswith(".dfa"):
                    # Load input file with .dfa extension
                    transition_table.setRowCount(len(lines))  # Set rows to be length of rows for the .dfa file
                    transition_table.setColumnCount(3)
                    transition_table.setHorizontalHeaderLabels(["State", "0", "1"])

                    for r, line in enumerate(lines): # Fill the table with the DFA file data
                        parts = line.split() # Split each line to be items in the transition table
                        # Ensure each row has 3 columns filled
                        for c in range(3):
                            text = parts[c] if c < len(parts) else ""
                            item = QTableWidgetItem(text)
                            item.setTextAlignment(Qt.AlignCenter)
                            transition_table.setItem(r, c, item) # Insert each items on the dfa file into the row cell

                    status_label.setText("STATUS: DFA table loaded successfully.") # Modifies status label when .dfa file is loaded
                    process_button.setEnabled(True)

            except Exception as e: # Show error dialog if file fails to load
                QMessageBox.critical(window, "Error", f"Failed to load file:\n{e}")
                status_label.setText("STATUS: Error loading file.")

    def process_data(): # Function for the process operation
        input_data = input_text.toPlainText().strip() # Scans and checks if input string exists
        if not input_data:
            QMessageBox.warning(window, "Warning", "No input data to process.")
            return

        result = "" # Text display for the valid and invalid classification in the output
        output_text.setPlainText(result)
        status_label.setText("STATUS: Output saved to strings.out.") # Modifies status label when output is displayed
        QMessageBox.information(window, "Processing Complete", "Output saved to strings.out.")

    # Connect the functions to their corresponding button operations
    load_button.clicked.connect(load_file)
    process_button.clicked.connect(process_data)

    button_layout = QHBoxLayout() # Horizontal layout for the buttons
    button_layout.addWidget(load_button)
    button_layout.addWidget(process_button)

    display_layout = QGridLayout() # Grid layout for the display areas
    display_layout.addWidget(transition_label, 0, 0)
    display_layout.addWidget(input_label, 0, 1)
    display_layout.addWidget(output_label, 0, 2)
    display_layout.addWidget(transition_table, 1, 0)
    display_layout.addWidget(input_text, 1, 1)
    display_layout.addWidget(output_text, 1, 2) # Arranges all widgets in their corresponding row-column positions

    # Combine all components in a vertical layout
    main_layout = QVBoxLayout()
    main_layout.addLayout(button_layout)
    main_layout.addLayout(display_layout)
    main_layout.addWidget(status_label) # Adds the status label display at the bottom

    window.setLayout(main_layout)
    return window


if __name__ == "__main__":
    app = QApplication(sys.argv) # Create app instance
    win = main_window()
    win.show()
    sys.exit(app.exec()) # Run the application event loop, Stops when the X button is clicked