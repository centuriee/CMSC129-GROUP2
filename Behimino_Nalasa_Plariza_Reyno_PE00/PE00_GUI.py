import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QTextEdit,
    QPushButton, QHBoxLayout, QVBoxLayout
)


def main_window():
   
    window = QWidget() #Create main window for GUI
    window.setWindowTitle("PE00: Expression Evaluation")
    window.resize(800, 400)

   
    input_text = QTextEdit() #Defines text area for input
    input_text.setPlaceholderText("Input Text Area")

    load_button = QPushButton("Load File") #Creates Button for load file

    input_layout = QVBoxLayout() #Creates vertical box layout for the definition of input layout
    input_layout.addWidget(input_text)
    input_layout.addWidget(load_button)

 
    output_text = QTextEdit() #Defines text area for output
    output_text.setPlaceholderText("Output Text Area")
    output_text.setReadOnly(True)

    process_button = QPushButton("Process") #Creates Button for the process operation

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



