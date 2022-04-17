import sqlite3
from sqlite3 import Error
from os import path
from datetime import datetime, timedelta
from setup_db import setup_db

def main():
    db_link = path.dirname(__file__)+'\data\shifts.db'
    print(db_link)
    #connect to database
    conn = create_connection(db_link)
    if conn is None:
        print('Error! Could not establish connection.')
    else:
        cur = conn.cursor()
        cur.execute('SELECT shift_end FROM shifts WHERE id = (SELECT MAX(id) FROM shifts)')
        is_not_working = cur.fetchall()
        print(is_not_working)
        input()
        if len(is_not_working) > 0:
            is_not_working = is_not_working[0]
        else:
            is_not_working = True
        
        if is_not_working:
            user_is_sure = input('you are not working. are you clocking in?')
            if user_is_sure.lower().strip() in ['y', 'yes']: punch_in(conn)
        else:#is working
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

def punch_in(conn):
    """makes a new database entry for the started shift and sets is_working to true"""
    sql = ''' INSERT INTO shifts(name, date, shift_start)
              VALUES(?, ?, ?) '''
              #name, date, shift_start
    cur = conn.cursor()
    current_datetime = datetime.now()
    current_datetime = current_datetime - timedelta(microseconds=current_datetime.microsecond)
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    cur.execute(sql, ("Pat", current_date, current_time))
    conn.commit()

def punch_out(conn):
    """updates the database entry with the clockout time and sets is_working to false"""
    sql = ''' UPDATE shifts
              SET shift_end = ? ,
                  shift_length = ? , 
                  daily_hours = ? 
              WHERE id = (SELECT MAX(id) FROM shifts)'''
              #
    cur = conn.cursor()
    current_datetime = datetime.now()
    current_datetime = current_datetime - timedelta(microseconds=current_datetime.microsecond)
    current_time = current_datetime.time()
    shift_length = calculate_shift_length(conn, current_time)
    daily_hours = calculate_daily_hours_logged(conn, shift_length)
    daily_hours += shift_length #current shift not added in function call
    cur.execute(sql, (current_time, shift_length, daily_hours))
    conn.commit()

def calculate_shift_length(conn, current_time):
    sql = '''SELECT shift_start FROM shifts WHERE id = (SELECT MAX(id) from shifts)'''
    cur = conn.cursor()
    cur.execute(sql)
    shift_start_time = cur.fetchall()
    print(shift_start_time)
    return abs(current_time - shift_start_time)

def calculate_daily_hours_logged(conn):
    sql = '''SELECT shift_length FROM shifts WHERE date = (SELECT date FROM shifts WHERE id = (SELECT MAX(id) from shifts))'''
    cur = conn.cursor()
    cur.execute(sql)
    total_shifts = cur.fetchall()[0]
    return sum(total_shifts)

if __name__=='__main__':
    main()