import sqlite3
from sqlite3 import Error
from os import path
import setup_db
from datetime import datetime

def main():
    #check if file exists
    db_link = path.abspath('.')+'punchclock/data/shifts.db'
    #if not path.exists(db_link):
    #    setup_db.main()
    #connect to database
    conn = setup_db.create_connection(db_link)
    if conn is None:
        print('Error! Could not establish connection.')
    else:
        if check_if_working(conn):#currently on shift
            user_is_sure = input('You are working. Clock out? ')
            if user_is_sure in ['y', 'yes']: punch_out()
        else:#not on shift
            user_is_sure = input('you are not working. are you clocking in?')
            if user_is_sure.lower().strip() in ['y', 'yes']: punch_in()
            else:
                something_went_wrong = input("did something go wrong and you're clocking out?")
                if something_went_wrong.lower().strip() in ['y', 'yes']:
                    punch_out()
        

def check_if_working(conn):
    """queries database to see if the latest entry has is_working=True """
    sql = ''' SELECT is_working FROM shifts ORDER BY id DESC LIMIT 1'''
    cur = conn.cursor()
    cur.execute(sql)
    is_working = cur.fetchall()
    return is_working

def punch_in(conn):
    """makes a new database entry for the started shift and sets is_working to true"""
    sql = ''' INSERT INTO shifts(shift_start,working)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (datetime.now(), True))
    conn.commit()
    return cur.lastrowid

def punch_out(conn):
    """updates the database entry with the clockout time and sets is_working to false"""
    sql = ''' UPDATE shifts
              SET shift_end = ? ,
                  is_working = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, (datetime.now(), False))
    conn.commit()
    return cur.lastrowid

if __name__=='__main__':
    main()