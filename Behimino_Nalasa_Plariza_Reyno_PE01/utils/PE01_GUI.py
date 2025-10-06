import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, 
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt


def main_window():
    window = QWidget()
    window.setWindowTitle("PE01 - Strings and DFA")
    window.resize(900, 450)

    # UI Components
    transition_label = QLabel("Transition Table")
    transition_table = QTableWidget(0, 4)
    transition_table.setHorizontalHeaderLabels(["", "State", "0", "1"])
    transition_table.verticalHeader().setVisible(False)
    transition_table.setEditTriggers(QTableWidget.NoEditTriggers)

    input_label = QLabel("Input")
    input_text = QTextEdit()
    input_text.setPlaceholderText("Input strings will display here...")
    input_text.setReadOnly(True)

    output_label = QLabel("Output")
    output_text = QTextEdit()
    output_text.setPlaceholderText("Output results will display here...")
    output_text.setReadOnly(True)

    status_label = QLabel("STATUS: Waiting for input.")
    status_label.setStyleSheet("font-weight: bold;")

    load_button = QPushButton("Load File")
    process_button = QPushButton("Process")
    process_button.setEnabled(False)

    # Flags for loaded files
    dfa_loaded = False
    input_loaded = False

    # DFA data containers
    state_dict = {}
    char_0, char_1 = None, None

    # DFA Logic Integration
    def process_input(states, inp, char_0, char_1):
        current_state = "NONE"
        for state_name, state_params in states.items():
            if state_params[0] == '-':  # start state
                if current_state != "NONE":
                    raise Exception("Multiple start states detected")
                current_state = state_name
                break

        for char in inp:
            if char == char_0:
                current_state = states[current_state][1]
            elif char == char_1:
                current_state = states[current_state][2]
            else:
                raise Exception(f"Invalid input character '{char}' detected")
            
        if states[current_state][0] == '+':
            return "VALID"
        else:
            return "INVALID"

    def load_file():
        nonlocal dfa_loaded, input_loaded, state_dict, char_0, char_1
        file_name, _ = QFileDialog.getOpenFileName(
            window,
            "Open Input File",
            "",
            "Input Files (*.in *.dfa *.txt);;All Files (*)"
        )

        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]

            if file_name.endswith(".in") or "strings" in file_name:
                # Input strings file
                input_text.setPlainText("\n".join(lines))
                input_loaded = True
                status_label.setText("STATUS: Input strings loaded successfully.")

            elif file_name.endswith(".dfa") or "transitions" in file_name:
                # DFA transitions file
                state_dict.clear()
                char_0, char_1 = lines[0].split(',')
                for line in lines[1:]:
                    parts = line.split(',')
                    if len(parts) == 4:
                        state_type, state_name, t0, t1 = parts
                        state_dict[state_name] = (state_type, t0, t1)

                # Type, State, Input 0, Input 1
                transition_table.setHorizontalHeaderLabels(["", "State", f"{char_0}", f"{char_1}"])
                transition_table.setRowCount(len(state_dict))
                for r, (state, params) in enumerate(state_dict.items()):
                    state_type, t0, t1 = params

                    # Create QTableWidgetItems
                    item_type = QTableWidgetItem(state_type)
                    item_state = QTableWidgetItem(state)
                    item_0 = QTableWidgetItem(t0)
                    item_1 = QTableWidgetItem(t1)

                    # Center align all text
                    for item in [item_type, item_state, item_0, item_1]:
                        item.setTextAlignment(Qt.AlignCenter)

                    # Add to table
                    transition_table.setItem(r, 0, item_type)
                    transition_table.setItem(r, 1, item_state)
                    transition_table.setItem(r, 2, item_0)
                    transition_table.setItem(r, 3, item_1)

                dfa_loaded = True
                status_label.setText("STATUS: DFA transitions loaded successfully.")

            process_button.setEnabled(dfa_loaded and input_loaded)

        except Exception as e:
            QMessageBox.critical(window, "Error", f"Failed to load file:\n{e}")
            status_label.setText("STATUS: Error loading file.")

    def process_data():
        nonlocal state_dict, char_0, char_1
        input_data = input_text.toPlainText().strip()
        if not input_data:
            QMessageBox.warning(window, "Warning", "No input data to process.")
            return
        if not state_dict:
            QMessageBox.warning(window, "Warning", "No DFA transitions loaded.")
            return

        results = []
        for line in input_data.splitlines():
            try:
                result = process_input(state_dict, line.strip(), char_0, char_1)
                results.append(f"{result}")
            except Exception as e:
                results.append(f"ERROR ({e})")

        # Display results
        output_text.setPlainText("\n".join(results))

        # Save to strings.out
        try:
            with open("strings.out", "w", encoding="utf-8") as f:
                f.write("\n".join(results))
            status_label.setText("STATUS: Processing complete. Output saved to strings.out.")
        except Exception as e:
            QMessageBox.warning(window, "Warning", f"Could not save output: {e}")
            status_label.setText("STATUS: Processing complete, but failed to save output.")

        QMessageBox.information(window, "Processing Complete", "DFA simulation complete!")

    # Layouts
    load_button.clicked.connect(load_file)
    process_button.clicked.connect(process_data)

    button_layout = QHBoxLayout()
    button_layout.addWidget(load_button)
    button_layout.addWidget(process_button)

    display_layout = QGridLayout()
    display_layout.addWidget(transition_label, 0, 0)
    display_layout.addWidget(input_label, 0, 1)
    display_layout.addWidget(output_label, 0, 2)
    display_layout.addWidget(transition_table, 1, 0)
    display_layout.addWidget(input_text, 1, 1)
    display_layout.addWidget(output_text, 1, 2)

    display_layout.setColumnStretch(0, 5)  # Transition table column (wider)
    display_layout.setColumnStretch(1, 3)  # Input column
    display_layout.setColumnStretch(2, 3)  # Output column

    main_layout = QVBoxLayout()
    main_layout.addLayout(button_layout)
    main_layout.addLayout(display_layout)
    main_layout.addWidget(status_label)

    window.setLayout(main_layout)
    return window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = main_window()
    win.show()
    sys.exit(app.exec())
