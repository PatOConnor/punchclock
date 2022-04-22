from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer
from datetime import datetime, timedelta
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
        self.setFixedSize(400, 150,)
        #getting style sheet   
        style_file = open(path.dirname(__file__)+'\guistyle.css')
        gui_style = style_file.read()
        self.setStyleSheet(gui_style)
        #establishing database connection
        db_link = path.dirname(__file__)+'\data\shifts.db'
        self.conn = clock_cli.create_connection(db_link)        
        #getting status of punched in or punched out
        cur = self.conn.cursor()
        cur.execute('SELECT shift_end FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
        punched_out = cur.fetchall()
        #will be [] if new table, [None] if clocked in, [str] if clocked out
        if len(punched_out) == 0: 
            punched_out.append([True])#preventing indexerror
        self.punched_out = punched_out[0][0]

        
        if not self.punched_out:
            cur.execute('SELECT shift_start FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
            shift_start_time = cur.fetchall()[0][0]
            shift_start_time = datetime.strptime(shift_start_time, '%H:%M:%S')
            current_time = datetime.now()
            shift_amount = abs(shift_start_time - current_time)
            self.seconds_count = shift_amount.seconds
            print(self.seconds_count)
            self.punch_button = QPushButton("Punch Out")
        else:
            self.seconds_count = 0
            self.punch_button = QPushButton("Punch In")
        self.punch_button.setDefault(True)
        self.punch_button.clicked.connect(self.hit_punchclock)       
       

        timetext = self.delta_to_string()
        self.timer_label = QLabel()
        self.timer_label.setGeometry(75, 100, 250, 70)
        self.timer_label.setText(str(timetext.time()))
        
        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)
        
        button_and_clock = QHBoxLayout()
        button_and_clock.addWidget(self.timer_label)
        button_and_clock.addWidget(self.punch_button)
        button_widget = QWidget()
        button_widget.setLayout(button_and_clock)
        
        self.setCentralWidget(button_widget)

    def hit_punchclock(self, buttonState:bool):#button state needed for syntax
        if self.punched_out: 
            clock_cli.punch_in(self.conn)
            self.punch_button.setText("Punch Out")
            self.punched_out = False
        else:
            clock_cli.punch_out(self.conn)
            self.punch_button.setText("Punch In")
            self.punched_out = True
            self.seconds_count = 0
    
    def show_time(self):
        if not self.punched_out:
            self.seconds_count += 1
        timetext = self.delta_to_string()
        self.timer_label.setText(str(timetext.time()))

    def delta_to_string(self):
        hours_count = self.seconds_count // 3600
        minutes_count = self.seconds_count // 60 - hours_count * 60
        seconds_count = self.seconds_count % 60
        #set leading zeros if neccesary
        if hours_count < 10: hours_count = '0'+str(hours_count)
        if minutes_count < 10: minutes_count = '0'+str(minutes_count)
        if seconds_count < 10: seconds_count = '0'+str(seconds_count)
        timetext = datetime.strptime(str(hours_count)+':'+str(minutes_count)+':'+
                                     str(seconds_count), '%H:%M:%S')
        return timetext

if __name__=='__main__':
    main()