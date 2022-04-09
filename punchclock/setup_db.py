import sqlite3
from sqlite3 import Error
from os import path



def setup_db():
    """create database file for punch clock that has one """
    sql_create_punchclock_table ="""CREATE TABLE IF NOT EXISTS shifts (
                                        id integer PRIMARY KEY,
                                        shift_start text,
                                        shift_end text,
                                        is_working boolean
                                );"""
    db_link = path.abspath('.')+'\punchclock\data\shifts.db'
    print(db_link)
    conn = create_connection(db_link)
    if conn is not None:
        create_table(conn,sql_create_punchclock_table)
    else:
        print('Error! Could not establish connection.')


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

if __name__=='__main__':
    setup_db()
