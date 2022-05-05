import sqlite3
from sqlite3 import Error
from os import path, mkdir
from datetime import datetime, timedelta
from xmlrpc.client import DateTime
import setup_db

def main(username:str):
    if not username:
        username = "Pat"
    db_link = path.dirname(__file__)+'\data\shifts.db'
    conn = create_connection(db_link)#connect to database
    if conn is None:
        if not path.exists(path.dirname(__file__)+'\data'):
            mkdir(path.dirname(__file__)+'\data')
        setup_db.setup_db()
    else:
        cur = conn.cursor()
        cur.execute('SELECT shift_end FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
        punched_out = cur.fetchall()
        #will be [] if new table, [None] if clocked in, [str] if clocked out
        if len(punched_out) == 0: 
            punched_out.append([True])#preventing indexerror
        punched_out = punched_out[0][0]
        if punched_out:
            user_is_sure = input('you are not working. are you clocking in? ')
            if user_is_sure.lower().strip() in ['y', 'yes']: punch_in(conn, username)
        else:
            user_is_sure = input('You are working. Clock out? ')
            if user_is_sure in ['y', 'yes']: punch_out(conn)

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

def calculate_shift_length(conn, current_time):
    sql = '''SELECT shift_start FROM shifts WHERE id = (SELECT MAX(id) from shifts)'''
    cur = conn.cursor()
    cur.execute(sql)
    shift_start_time = cur.fetchall()[0][0]
    shift_start_time = datetime.strptime(shift_start_time, '%H:%M:%S')
    current_time = datetime.strptime(str(current_time), '%H:%M:%S')
    shift_amount = abs(shift_start_time - current_time)
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
        date_time_list = [datetime.strptime(x[0], '%H:%M:%S') for x in total_shifts]
        sum_of_seconds = sum(x.second for x in date_time_list)
        sum_of_minutes = sum(x.minute for x in date_time_list)
        sum_of_hours = sum(x.hour for x in date_time_list)
        s = sum_of_seconds % 60
        m = sum_of_minutes % 60
        m += sum_of_seconds // 60
        h = sum_of_hours
        h += sum_of_minutes // 60        
        return timedelta(hours=h, minutes=m, seconds=s)

        
if __name__=='__main__':
    main()