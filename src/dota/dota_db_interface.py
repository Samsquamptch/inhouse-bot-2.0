import dotenv
import src.data.db_access as db_access


def load_active_lobbies():
    conn = db_access.get_db_connection()
    autolobby_list = list(conn.cursor().execute("""SELECT srv.Server FROM AutoLobby alb JOIN Server srv ON alb.ServerId = srv.Id 
            WHERE alb.MatchStatus = 0"""))
    db_access.close_db_connection(conn)
    return autolobby_list


def load_server_steam(server):
    username = dotenv.get_key("../../credentials/.env", str(server)+"username")
    password = dotenv.get_key("../../credentials/.env", str(server)+"password")
    return [username, password]
