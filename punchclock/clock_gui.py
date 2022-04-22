from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime, timedelta
from os import path
import sys
import clock_cli, setup_db

def main(username:str=None):
    app = QApplication(sys.argv)
    window = MainWindow(username)
    window.show()
    app.exec()

class MainWindow(QMainWindow):
    def __init__(self, username:str=None):
        super().__init__()
        self.setWindowTitle("Personal Punch Clock")
        self.setFixedSize(400, 133,)
        
        #getting style sheet   
        style_file = open(path.dirname(__file__)+'\guistyle.css')
        gui_style = style_file.read()
        self.setStyleSheet(gui_style)
        
        self.db_connect() #creates self.conn, self.cur
        self.get_punch_status()
        self.set_username_field(username=username)
        self.set_time_clock()
        self.set_clock_button()
        self.set_layouts()

    def db_connect(self):
        #establishing database connection
        self.db_link = path.dirname(__file__)+'\data\shifts.db'
        self.conn = clock_cli.create_connection(self.db_link)
        if self.conn == None:
            setup_db.setup_db()
            self.db_connect()
        self.cur = self.conn.cursor()

    def get_punch_status(self):
        #getting status of punched in or punched out
        self.cur.execute('SELECT shift_end FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
        punched_out = self.cur.fetchall()
        #will be [] if new table, [None] if clocked in, [str] if clocked out
        if len(punched_out) == 0: 
            punched_out.append([True])#preventing indexerror
        self.punched_out = punched_out[0][0]
        
    def set_username_field(self, username:str=None):
        if not username:
            self.cur.execute('SELECT name FROM shifts where id = (SELECT MAX(ID) FROM shifts)')
            username = self.cur.fetchall()
            if not username: 
                username = 'Default'
            else: 
                username = username[0][0]
    
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(32)
        self.name_input.setText(username)
    
    def set_time_clock(self):
        if not self.punched_out:
            #get time already spent working and set it to ticking timer
            self.cur.execute('SELECT shift_start FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
            shift_start_time = self.cur.fetchall()[0][0]
            shift_start_time = datetime.strptime(shift_start_time, '%H:%M:%S')
            current_time = datetime.now()
            shift_amount = abs(shift_start_time - current_time)
            #int representing a large amount of seconds
            self.seconds_count = shift_amount.seconds          
            self.name_input.setReadOnly(True)
        else:
            self.seconds_count = 0
            self.name_input.setReadOnly(False)
        timetext = self.delta_to_string()

        self.timer_label = QLabel()
        self.timer_label.setGeometry(75, 100, 250, 70)
        self.timer_label.setText(str(timetext.time()))

        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(1000)
        
    def set_clock_button(self):
        self.punch_button = QPushButton()
        self.punch_button.setDefault(True)
        self.punch_button.clicked.connect(self.hit_punchclock)
        if self.punched_out:
            self.punch_button.setText("Punch In")
        else:
            self.punch_button.setText("Punch Out")

    def set_layouts(self):
        button_and_text_box_layout = QVBoxLayout()
        button_and_text_box_layout.addWidget(self.name_input)
        button_and_text_box_layout.addWidget(self.punch_button)
        button_and_text_box = QWidget()
        button_and_text_box.setLayout(button_and_text_box_layout)
        all_widgets_layout = QHBoxLayout()
        all_widgets_layout.addWidget(self.timer_label)
        all_widgets_layout.addWidget(button_and_text_box)
        all_widgets = QWidget()
        all_widgets.setLayout(all_widgets_layout)
        self.setCentralWidget(all_widgets)

    def hit_punchclock(self, buttonState:bool):#button state needed for syntax
        if self.punched_out: 
            name = self.name_input.text()
            clock_cli.punch_in(self.conn, name)
            self.punch_button.setText("Punch Out")
            self.punched_out = False
            self.name_input.setReadOnly(True)
        else:
            clock_cli.punch_out(self.conn)
            self.punch_button.setText("Punch In")
            self.punched_out = True
            self.seconds_count = 0
            self.name_input.setReadOnly(False)

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