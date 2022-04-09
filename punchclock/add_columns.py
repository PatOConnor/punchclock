import sqlite3
from sqlite3 import Error
from os import path
from datetime import datetime, timedelta


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

if __name__=="__main__":
    db = create_connection(path.dirname(__file__)+'/data/shifts.db')
    cur = db.cursor()
    add_shift_length_column = "ALTER TABLE shifts ADD COLUMN  shift_length real"
    add_daily_hours_column = "ALTER TABLE shifts ADD COLUMN  daily_hours real"
    cur.execute(add_shift_length_column)
    cur.execute(add_daily_hours_column)
