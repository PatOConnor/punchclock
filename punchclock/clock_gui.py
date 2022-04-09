from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout
from os import path
import sys
import clock_cli

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pat's Punch Clock")

        db_link = path.dirname(__file__)+'\data\shifts.db'
        self.conn = clock_cli.create_connection(db_link)

        punch_in_button = QPushButton("Punch In")
        punch_in_button.setDefault(True)
        punch_in_button.clicked.connect(self.punch_in_gui)

        punch_out_button = QPushButton("Punch Out")
        punch_out_button.setDefault(True)
        punch_out_button.clicked.connect(self.punch_out_gui)
        
        both_buttons = QHBoxLayout()
        both_buttons.addWidget(punch_in_button)
        both_buttons.addWidget(punch_out_button)
        button_widget = QWidget()
        button_widget.setLayout(both_buttons)
        
        self.setCentralWidget(button_widget)

    def punch_in_gui(self, buttonState: bool):
        #buttonState is passed by QPushButton and is not used
        clock_cli.punch_in(self.conn)

    def punch_out_gui(self, buttonState: bool):
        clock_cli.punch_out(self.conn)

if __name__=='__main__':
    main()