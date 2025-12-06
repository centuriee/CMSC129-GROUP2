import sys
import os
from PySide6.QtWidgets import QApplication
from gui import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # pass main directory
    if getattr(sys, 'frozen', False):
        main_dir = os.path.dirname(sys.executable)
    else:
        main_dir = os.path.dirname(os.path.abspath(__file__))
    
    window = MainWindow(main_dir = main_dir)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()