import sqlite3
from sqlite3 import Error
from os import path, mkdir
from datetime import datetime, timedelta
import setup_db
from rich import print
from rich.layout import Layout
from rich.panel import Panel
from punchconfig import DEFAULT_NAME

days_in_month_ = {
    1:31,
    2:28,
    3:31,
    4:30,
    5:31,
    6:30,
    7:31,
    8:31,
    9:30,
    10:31,
    11:30,
    12:31
}

def main(username:str):
    if not username:
        username = DEFAULT_NAME
    if not path.exists(path.dirname(__file__)+'\\data'):
        mkdir(path.dirname(__file__)+'\\data')
    db_link = path.dirname(__file__)+'\data\shifts.db'
    conn = create_connection(db_link)#connect to database


    cur = conn.cursor()
    try:
        cur.execute('SELECT * FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
    except sqlite3.OperationalError:
        #table does not exist
        setup_db.setup_db()
        punch_in(conn, username)
        punch_out(conn)
        cur.execute('SELECT * FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
    latest_punch = cur.fetchall()[0]
    output = rich_layout(latest_punch)
    print(output)
    is_punched_in = True if latest_punch[4] == None else False
    user_response = input('\t')
    if user_response.lower().strip() in ['y', 'yes']:
        if is_punched_in: 
            print('here')
            punch_out(conn)
        else:
            punch_in(conn, username)

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def punch_in(conn, username):
    """makes a new database entry for the started shift and sets is_working to true"""
    sql = ''' INSERT INTO shifts(name, date, shift_start)
              VALUES(?, ?, ?) '''
              #name, date, shift_start
    cur = conn.cursor()
    current_datetime = datetime.now()
    current_datetime = current_datetime - timedelta(microseconds=current_datetime.microsecond)
    current_date = str(current_datetime.date())
    current_time = str(current_datetime.time())
    cur.execute(sql, (username, current_date, current_time))
    conn.commit()

def punch_out(conn):
    """updates the database entry with the clockout time and sets is_working to false"""
    sql = ''' UPDATE shifts
              SET shift_end = ? ,
                  shift_length = ? , 
                  daily_hours = ? 
              WHERE id = (SELECT MAX(id) FROM shifts)'''
    cur = conn.cursor()
    current_datetime = datetime.now()
    current_datetime = current_datetime - timedelta(microseconds=current_datetime.microsecond)
    current_time = current_datetime.time()
    shift_length = calculate_shift_length(conn, current_time)
    daily_hours = calculate_daily_hours_logged(conn)
    daily_hours += shift_length #current shift not added in function call
    cur.execute(sql, (str(current_time), str(shift_length), str(daily_hours)))
    conn.commit()

"""calculates difference between two dates given as [yr,mo,day], all ints"""
def calculate_date_shift(early_date:list[int],later_date:list[int])->int:
    #probably gonna replace this with a builtin on refactor
    #days between them
    date_shift = later_date[2] - early_date[2]
    month_shift = later_date[1] - early_date[1]
    #god forbid i work through new years
    year_shift = abs(later_date[0] - early_date[0])
    month_shift += year_shift * 12
    while month_shift > 0:
        #e.g. month=5, date_shift += 31
        date_shift += days_in_month_[early_date[1]]
        #leap year
        if early_date[1] == 2 and early_date[0] % 4 == 0:
            date_shift += 1
        early_date[1] += 1
        #wrap months around if i work for months on end
        if early_date[1] > 12:
            early_date[1] = 1
            early_date[0] += 1
        month_shift -= 1
    return date_shift



def calculate_shift_length(conn, current_time):
    sql = '''SELECT date, shift_start FROM shifts WHERE id = (SELECT MAX(id) from shifts)'''
    cur = conn.cursor()
    cur.execute(sql)
    shift_data = cur.fetchall()[0]

    shift_start_time = shift_data[0]
    shift_start_time = datetime.strptime(shift_start_time, '%H:%M:%S')
    current_time = datetime.strptime(str(current_time), '%H:%M:%S')
    shift_amount = current_time - shift_start_time
    start_date = shift_data[0].split('-')
    current_date =  datetime.today()[0:3]
    date_shift = calculate_date_shift(start_date, current_date)
    #day changed while working
    while date_shift > 0:
        #add one day to offset the subtraction
        shift_amount += timedelta(days=1)
    return shift_amount

def calculate_daily_hours_logged(conn):
    sql = '''SELECT shift_length FROM shifts WHERE date = (SELECT date FROM shifts WHERE id = (SELECT MAX(id) from shifts))'''
    cur = conn.cursor()
    cur.execute(sql)
    total_shifts = cur.fetchall()
    #either [None] or [str1, str2, str3, ...]
    if not total_shifts[0]:
        return timedelta(seconds=0) 
    else:
        total_shifts = total_shifts[:-1]
        date_time_list = [datetime.strptime(x[0], '%H:%M:%S') for x in total_shifts if x[0] != None]
        sum_of_seconds = sum(x.second for x in date_time_list)
        sum_of_minutes = sum(x.minute for x in date_time_list)
        sum_of_hours = sum(x.hour for x in date_time_list)
        s = sum_of_seconds % 60
        m = sum_of_minutes % 60
        m += sum_of_seconds // 60
        h = sum_of_hours
        h += sum_of_minutes // 60        
        return timedelta(hours=h, minutes=m, seconds=s)

def rich_layout(punch_data):
    (id, user, start_date, start_time, end_time, length, daily_length) = (punch_data)
    punch_panel = Layout()
    punch_panel.split_column(
        Layout(name='Pat\'s Punch Clock is FOSS', size=1),
        Layout(name='top_row', size=3),
        Layout(name='bottom_row', size=3)
    )
    punch_panel['top_row'].split_row(
        Layout(name='title_panel', size=18),
        Layout(name='last_punch_panel'),
    )
    
    
    is_punched_in = True if end_time == None else False
    last_punch = start_time if end_time == None else end_time
    punch_panel['title_panel'].update(Panel('Punch Clock'))
    punch_panel['last_punch_panel'].update(Panel(f'Last Punch: {last_punch}'))
    if is_punched_in:
        msg = 'Enter \'y\' to punch out'
    else:
        msg = 'Enter \'y\' to punch in'
    punch_panel['bottom_row'].update(Panel(msg))
    return punch_panel

if __name__=='__main__':
    main()