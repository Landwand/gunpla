from flask import g
# g safe threading for multiple requests,
import sqlite3


def get_db():
    if hasattr(g, 'conn'):
        return g.conn # connection exists, with row factory already set
    try:
        g.conn = sqlite3.connect('gunpla.db', isolation_level=None) # autocommit ON
        g.conn.row_factory = sqlite3.Row # set row_factory to sqlite3.Row class; calling it later will return an instance of Row
        return g.conn
    except sqlite3.Error as e:
        # this covers many types of DB errors
        raise Exception (f"Failed to connect to the database : {e}")


def get_cursor():
    conn = get_db()
    return conn.cursor()
    


