import dotenv
import src.data.db_access as db_access


def load_active_lobbies():
    conn = db_access.get_db_connection()
    autolobby_list = list(conn.cursor().execute("""SELECT srv.Server, alb.MatchId FROM AutoLobby alb JOIN Server srv ON alb.ServerId = srv.Id 
            WHERE alb.MatchStatus = 0"""))
    db_access.close_db_connection(conn)
    return autolobby_list


def load_server_steam(server):
    username = dotenv.get_key("../../credentials/.env", str(server)+"username")
    password = dotenv.get_key("../../credentials/.env", str(server)+"password")
    return [username, password]

def update_match_records(winners, losers, server):
    conn = db_access.get_db_connection()
    for player in winners:
        conn.cursor().execute("""UPDATE USER SET MMR = MMR + 25 WHERE Steam = ?""" [player])
        conn.cursor().execute("""UPDATE UserServer SET Wins = Wins + 1 WHERE EXISTS (SELECT 1 FROM Server WHERE 
            UserServer.ServerId = Server.Id AND Server.Server = ?""", [server])
        conn.commit()
    for player in losers:
        conn.cursor().execute("""UPDATE USER SET MMR = MMR - 25 WHERE Steam = ?"""[player])
        conn.cursor().execute("""UPDATE UserServer SET Losses = Losses + 1 WHERE EXISTS (SELECT 1 FROM Server WHERE 
                    UserServer.ServerId = Server.Id AND Server.Server = ?""", [server])
        conn.commit()
    db_access.close_db_connection(conn)
    return

def update_autolobby_status(column, match_id):
    conn = db_access.get_db_connection()
    conn.cursor().execute(f"""UPDATE AutoLobby SET {column} = 1 WHERE MatchId = ?"""[match_id])

def return_queue_ids(match_id):
    conn = db_access.get_db_connection()
    steam_ids = []
    id_list = list(conn.cursor().execute("""SELECT Usr.Steam FROM User Usr JOIN UserLobby Uly ON Uly.UserId = Usr.Id
                                                WHERE Uly.MatchId = ?""", [match_id]))
    db_access.close_db_connection(conn)
    for id in id_list:
        steam_ids.append(id[0] + 76561197960265728)
    return steam_ids

def load_dota_settings(server):
    conn = db_access.get_db_connection()
    settings = list(conn.cursor().execute("""SELECT Dts.LobbyName, Dts.LobbyPassword, Dts.Region, Dts.LeagueId, Dts.ViewerDelay FROM 
                                              DotaSettings Dts JOIN Server Srv ON Dts.ServerId = Srv.Id WHERE Srv.Server 
                                              = ?""", [server]))
    db_access.close_db_connection(conn)
    return list(settings[0])
