import sqlite3
from sqlite3 import Error
from os import path
from setup_db import setup_db
from datetime import datetime, timedelta

def main():
    #check if file exists
    db_link = path.abspath('.')+'\punchclock\data\shifts.db'
    if not path.exists(db_link):
        setup_db()
    #connect to database
    conn = create_connection(db_link)
    if conn is None:
        print('Error! Could not establish connection.')
    else:
        if get_is_working(conn):#currently on shift
            user_is_sure = input('You are working. Clock out? ')
            if user_is_sure in ['y', 'yes']: punch_out(conn)
            else:
                something_went_wrong = input("did something go wrong and you're clocking in?")
                if something_went_wrong.lower().strip() in ['y', 'yes']:
                    punch_in(conn)
        else:#not on shift
            user_is_sure = input('you are not working. are you clocking in?')
            if user_is_sure.lower().strip() in ['y', 'yes']: punch_in(conn)
            else:
                something_went_wrong = input("did something go wrong and you're clocking out?")
                if something_went_wrong.lower().strip() in ['y', 'yes']:
                    punch_out(conn)

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def get_last_row(conn):
    sql = ''' SELECT MAX(id) FROM shifts'''
    cur = conn.cursor()
    cur.execute(sql)
    max_id = cur.fetchall()
    return max_id[0][0]


def get_is_working(conn):
    """queries database to see if the latest entry has is_working=True """
    sql = ''' SELECT is_working FROM shifts ORDER BY id DESC LIMIT 1'''
    cur = conn.cursor()
    cur.execute(sql)
    is_working = cur.fetchall()
    print(is_working)
    return is_working[0][0]

def punch_in(conn):
    """makes a new database entry for the started shift and sets is_working to true"""
    sql = ''' INSERT INTO shifts(shift_start, is_working)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (datetime.now(), True))
    conn.commit()

def punch_out(conn):
    """updates the database entry with the clockout time and sets is_working to false"""
    sql = ''' UPDATE shifts
              SET shift_end = ? ,
                  is_working = ?
              WHERE id = ?'''
    cur = conn.cursor()
    right_now = datetime.now()
    right_now = right_now - timedelta(microseconds=right_now.microsecond)
    cur.execute(sql, (right_now, False, get_last_row(conn)))
    conn.commit()

if __name__=='__main__':
    main()