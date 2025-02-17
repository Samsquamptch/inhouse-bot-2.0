import sqlite3


def get_db_connection():
    conn = sqlite3.connect(f'../../data/inhouse.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def close_db_connection(conn):
    conn.close()


def load_channel_id(server, channel_name):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    channel_id = list(
        conn.cursor().execute(f'SELECT {channel_name} FROM Server where Server = ?', [server.id]).fetchall())
    close_db_connection(conn)
    return channel_id[0]


def load_id_from_server(server, column):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    column_id = list(
        conn.cursor().execute(f'SELECT {column} FROM Server where Server = ?', [server.id]).fetchall())
    close_db_connection(conn)
    return column_id[0]


def set_banned(user, server, banned):
    conn = get_db_connection()
    user_id = get_user_id(user)
    server_id = load_server_id(server)
    conn.cursor().execute("UPDATE UserServer SET Banned = ? WHERE UserId = ? AND ServerId = ?",
                          [banned, user_id, server_id])
    conn.commit()
    close_db_connection(conn)
    return


def get_user_id(user):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    user_id = list(conn.cursor().execute("""SELECT Id FROM User WHERE Discord = ?""", [user.id]))
    close_db_connection(conn)
    if not user_id:
        return 0
    return user_id[0]


def load_server_id(server):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    server_id = list(conn.cursor().execute("""SELECT Id FROM Server WHERE Server = ?""", [server.id]))
    close_db_connection(conn)
    return server_id[0]


def set_verification(user, server, verified):
    conn = get_db_connection()
    user_id = get_user_id(user)
    server_id = load_server_id(server)
    conn.cursor().execute("UPDATE UserServer SET Verified = ? WHERE UserId = ? AND ServerId = ?",
                          [verified, user_id, server_id])
    conn.commit()
    close_db_connection(conn)
    return


def load_unverified_ids(server):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    unverified_ids = (
        list(conn.cursor().execute(
            "SELECT User.Discord FROM UserServer INNER JOIN Server ON Server.Id = UserServer.ServerId "
            "JOIN User ON User.Id = UserServer.UserId WHERE Server.Server = ? AND UserServer.Verified "
            "IS NULL", [server.id]).fetchall())
    )
    conn.close()
    return unverified_ids


def check_for_value(column, value_check):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM User WHERE {column} = ?)", [value_check])
    item = cur.fetchone()[0]
    if item == 0:
        variable = False
    else:
        variable = True
    close_db_connection(conn)
    return variable


def load_user_status(user_id, server_id):
    conn = get_db_connection()
    user_status = list(
        conn.cursor().execute("""SELECT UserServer.Verified, UserServer.Banned FROM UserServer JOIN User 
            ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user_id, server_id]))
    close_db_connection(conn)
    return user_status[0]
