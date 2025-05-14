import sqlite3
import dotenv
import db_access


def set_env_variable(key, newvalue):
    dotenv.set_key("../../credentials/.env", key, newvalue)


def get_env_variable(key):
    return dotenv.get_key("../../credentials/.env", key)


def delete_env_variable(key):
    dotenv.unset_key("../../credentials/.env", key)


def get_reference_list(identifier=None):
    conn = db_access.get_db_connection()
    if not identifier:
        login_list = list(conn.cursor().execute("""SELECT stl.Title, srv.Server FROM SteamLogin stl JOIN Server srv ON
                                            srv.Id = stl.ServerId""").fetchall())
    else:
        login_list = list(conn.cursor().execute("""SELECT Title, ServerId FROM SteamLogin
                                        WHERE Title = ? OR ServerId = ?""", [identifier, identifier]).fetchall())
    db_access.close_db_connection(conn)
    return login_list


def get_reference_server(identifier):
    conn = db_access.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    login_list = list(conn.cursor().execute("""SELECT srv.Server FROM Server srv JOIN SteamLogin stl ON srv.Id = stl.ServerId
                                            WHERE stl.Title = ? OR srv.Server = ?""", [identifier, identifier]).fetchall())
    server = str(login_list[0])
    db_access.close_db_connection(conn)
    return server


def delete_credentials(identifier):
    conn = db_access.get_db_connection()
    server = get_reference_server(identifier)
    delete_env_variable(server + "username")
    delete_env_variable(server + "password")
    conn.cursor().execute("""DELETE FROM SteamLogin WHERE Title = ? OR ServerId = ?""", [identifier, identifier])
    conn.commit()
    db_access.close_db_connection(conn)
    return


def edit_credentials(identifier, username, password):
    server = get_reference_server(identifier)
    set_env_variable(server + "username", username)
    set_env_variable(server + "password", password)
    return


def add_credentials(title, server, username, password):
    conn = db_access.get_db_connection()
    try:
        conn.cursor().execute("""INSERT INTO SteamLogin (Title, ServerId) Values (?, (SELECT Id FROM Server WHERE Server = ?))""",
                              [title, server])
        set_env_variable(server + "username", username)
        set_env_variable(server + "password", password)
        conn.commit()
        db_access.close_db_connection(conn)
    except sqlite3.IntegrityError:
        print("Server does not exist within the database!")
    return


def database_exists():
    conn = db_access.get_db_connection()
    check = conn.cursor().execute("""SELECT name FROM sqlite_master; """).fetchall()
    db_access.close_db_connection(conn)
    return check


def create_tables():
    conn = db_access.get_db_connection()
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS User(Id INT PRIMARY KEY, Discord BIGINT UNIQUE, Steam BIGINT UNIQUE,
        MMR INT, Pos1 INT, Pos2 INT,Pos3 INT, Pos4 INT, Pos5 INT, LastUpdated DATETIME)""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS Server(Id INT PRIMARY KEY, Server BIGINT, AdminChannel BIGINT,
        QueueChannel BIGINT, GlobalChannel BIGINT, ChatChannel BIGINT, ChampionRole BIGINT, AdminRole BIGINT)""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS UserServer(UserId INT, ServerId INT, Verified BOOL, Banned BOOL, 
        Wins INT, Losses INT, FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS ServerSettings(ServerId INT UNIQUE, AfkTimer INT, SkillFloor INT,
        SkillCeiling INT, PingRole BIGINT, Tryhard BOOL, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS GlobalQueue(ServerId INT UNIQUE, PublicListing BOOL, InviteLink CHAR,
        FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS MessageIds(ServerId INT UNIQUE, AdminPanel BIGINT, AdminMenu BIGINT, 
        UserButtons BIGINT, UserMenu BIGINT, InhouseQueue BIGINT, GlobalQueue BIGINT, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS DotaSettings(ServerId INT, LobbyName CHAR, LobbyPassword CHAR, Region INT,
                            LeagueId INT, ViewerDelay INT, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS SteamLogin(ServerId INT UNIQUE, Title CHAR,
        FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS AutoLobby(MatchId INT PRIMARY KEY, ServerId INT, LobbyStatus BOOL,
        MatchStatus BOOL, FOREIGN KEY(ServerId) REFERENCES Server(Id)""")
    conn.cursor().execute("""CREATE TABLE IF NOT EXISTS UserLobby(MatchId INT, UserId INT, FOREIGN KEY(UserId) REFERENCES User(Id), 
        FOREIGN KEY(MatchId) REFERENCES AutoLobby(MatchId)""")
    db_access.close_db_connection(conn)
