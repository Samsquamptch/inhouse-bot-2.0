import sqlite3
import dotenv


def get_db_connection():
    conn = sqlite3.connect(f'../../data/inhouse.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def set_env_variable(key, newvalue):
    dotenv.set_key("../../credentials/.env", key, newvalue)


def get_env_variable(key):
    return dotenv.get_key("../../credentials/.env", key)


def delete_env_variable(key):
    dotenv.unset_key("../../credentials/.env", key)


def get_reference_list(identifier=None):
    conn = get_db_connection()
    if not identifier:
        login_list = list(conn.cursor().execute("""SELECT Title, ServerId FROM SteamLogin""").fetchall())
    else:
        login_list = list(conn.cursor().execute("""SELECT Title, ServerId FROM SteamLogin
                                        WHERE Title = ? OR ServerId = ?""", [identifier, identifier]).fetchall())
    conn.close()
    return login_list


def get_reference_server(identifier):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    login_list = list(conn.cursor().execute("""SELECT ServerId FROM SteamLogin
                                            WHERE Title = ? OR ServerId = ?""", [identifier, identifier]).fetchall())
    conn.close()
    server = str(login_list[0])
    return server


def delete_credentials(identifier):
    conn = get_db_connection()
    server = get_reference_server(identifier)
    delete_env_variable(server + "username")
    delete_env_variable(server + "password")
    conn.cursor().execute("""DELETE FROM SteamLogin WHERE Title = ? OR ServerId = ?""", [identifier, identifier])
    conn.commit()
    conn.close()
    return


def edit_credentials(identifier, username, password):
    server = get_reference_server(identifier)
    set_env_variable(server + "username", username)
    set_env_variable(server + "password", password)
    return


def add_credentials(title, server, username, password):
    conn = get_db_connection()
    try:
        conn.cursor().execute("""INSERT INTO SteamLogin (Title, ServerId) Values (?, ?)""",
                              [title, server])
        set_env_variable(server + "username", username)
        set_env_variable(server + "password", password)
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        print("Server does not exist within the database!")
    return


def database_exists():
    conn = get_db_connection()
    check = conn.cursor().execute("""SELECT name FROM sqlite_master; """).fetchall()
    conn.close()
    return check


def create_tables():
    conn = get_db_connection()
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS User(Id INT PRIMARY KEY, Discord BIGINT UNIQUE, Steam BIGINT UNIQUE,
        MMR INT, Verified BOOL, Pos1 INT, Pos2 INT,Pos3 INT, Pos4 INT, Pos5 INT, LastUpdated DATETIME)""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS Server(Id INTEGER PRIMARY KEY, Server BIGINT, AdminChannel BIGINT,
        QueueChannel BIGINT, GlobalChannel BIGINT, ChatChannel BIGINT, ChampionRole BIGINT)""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS UserStats(UserId INT, ServerId INT, Wins INT, Losses INT,
        FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS ServerSettings(ServerId INT UNIQUE, AfkTimer INT, SkillFloor INT,
        SkillCeiling INT, QueueName CHAR, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS GlobalQueue(ServerId INT UNIQUE, PublicListing BOOL, InviteLink CHAR,
        FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS DotaSettings(ServerId INT, LobbyName CHAR, AllChat BOOL, Region INT,
        LeagueId INT, ViewerDelay INT, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS Banned(UserId INT NOT NULL, ServerId INT NOT NULL,
        FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id), PRIMARY KEY(UserId, ServerId))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS Admin(UserId INT NOT NULL, ServerId INT NOT NULL,
        FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id), PRIMARY KEY(UserId, ServerId))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS SteamLogin(ServerId INT UNIQUE, Title CHAR,
        FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.close()
