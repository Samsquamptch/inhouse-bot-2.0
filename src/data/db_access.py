import sqlite3


def get_db_connection():
    conn = sqlite3.connect(f'../../data/inhouse.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def close_db_connection(conn):
    conn.close()
