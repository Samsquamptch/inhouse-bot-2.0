import sqlite3


class DBManager(object):

    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(f'../../data/inhouse.db')
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def close_db_connection(conn):
        conn.close()
