import discord.utils
import pandas as pd
from datetime import datetime
from dotenv import get_key
from discord_db_connection import DBManager


def get_discord_token():
    return get_key("../../credentials/.env", "TOKEN")


def check_server_in_db(server):
    conn = DBManager.get_db_connection()
    check = conn.cursor().execute("""SELECT * FROM Server WHERE Server = ?; """, [server.id]).fetchall()
    DBManager.close_db_connection(conn)
    return check


def add_server_to_db(server):
    conn = DBManager.get_db_connection()
    conn.cursor().execute("""INSERT INTO Server (Server) VALUES (?)""", [server.id])
    conn.commit()
    DBManager.close_db_connection(conn)
    return


def check_server_settings(server):
    conn = DBManager.get_db_connection()
    server_details = list(conn.cursor().execute("""SELECT ServerSettings.ServerId FROM ServerSettings INNER JOIN Server
                                                ON ServerSettings.ServerId = Server.Id WHERE Server.Server = ?""",
                                                [server.id]))
    DBManager.close_db_connection(conn)
    return server_details


def register_server(server, setup_list):
    conn = DBManager.get_db_connection()
    conn.cursor().execute("""UPDATE Server SET AdminChannel = ?, QueueChannel = ?, GlobalChannel = ?, ChatChannel = ?, 
                                AdminRole = ? WHERE Server = ?""", [setup_list[0], setup_list[1], setup_list[2],
                                                                    setup_list[3], setup_list[4], server.id])
    conn.commit()
    DBManager.close_db_connection(conn)


def add_default_settings(server):
    conn = DBManager.get_db_connection()
    conn.cursor().execute("""INSERT INTO ServerSettings (ServerId, AfkTimer, SkillFloor, SkillCeiling, QueueName)
                            VALUES ((SELECT Id from Server where Server = ?), 15, 0, 6000, "INHOUSE")""",
                          [server.id])
    conn.commit()
    DBManager.close_db_connection(conn)


def load_channel_id(server, channel_name):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    channel_id = list(
        conn.cursor().execute(f'SELECT {channel_name} FROM Server where Server = ?', [server.id]).fetchall())
    DBManager.close_db_connection(conn)
    return channel_id[0]


def load_admin_role(server):
    admin_id = load_id_from_server(server, "AdminRole")
    return discord.utils.get(server.roles, id=admin_id)


def load_champion_role(server):
    champion_id = load_id_from_server(server, "ChampionRole")
    return discord.utils.get(server.roles, id=champion_id)


def load_id_from_server(server, column):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    column_id = list(
        conn.cursor().execute(f'SELECT {column} FROM Server where Server = ?', [server.id]).fetchall())
    DBManager.close_db_connection(conn)
    return column_id[0]


def get_banned_status(user, server):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    banned_status = list(
        conn.cursor().execute("""SELECT UserServer.Banned FROM UserServer JOIN User 
            ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user.id, server.id]))
    DBManager.close_db_connection(conn)
    return banned_status[0]


def get_verified_status(user, server):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    verified_status = list(
        conn.cursor().execute("""SELECT UserServer.Verified FROM UserServer JOIN User 
                ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user.id, server.id]))
    DBManager.close_db_connection(conn)
    return verified_status[0]

def get_user_status(user, server):
    conn = DBManager.get_db_connection()
    user_status = list(
        conn.cursor().execute("""SELECT UserServer.Verified, UserServer.Banned FROM UserServer JOIN User 
        ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user.id, server.id]))
    DBManager.close_db_connection(conn)
    return list(user_status[0])


def user_registered(user):
    conn = DBManager.get_db_connection()
    user_id = list(conn.cursor().execute("""SELECT UserServer.UserId FROM UserServer INNER JOIN User ON 
                                            User.Id = UserServer.UserId WHERE User.Discord = ?""", [user.id]))
    DBManager.close_db_connection(conn)
    return user_id


def get_user_id(user):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    user_id = list(conn.cursor().execute("""SELECT Id FROM User WHERE Discord = ?""", [user.id]))
    DBManager.close_db_connection(conn)
    if not user_id:
        return 0
    return user_id[0]


def get_server_id(server):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    server_id = list(conn.cursor().execute("""SELECT Id FROM Server WHERE Server = ?""", [server.id]))
    DBManager.close_db_connection(conn)
    return server_id[0]


def auto_register(user, server):
    user_id = get_user_id(user)
    if user_id == 0:
        return False
    server_id = get_server_id(server)
    conn = DBManager.get_db_connection()
    conn.cursor().execute("""INSERT INTO UserServer (UserId, ServerId, Banned) VALUES (?, ?, 0)""",
                          [user_id, server_id])
    conn.commit()
    DBManager.close_db_connection(conn)
    return True


def get_unverified_users(server):
    conn = DBManager.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    unverified_ids = (
        list(conn.cursor().execute(
            "SELECT User.Discord FROM UserServer INNER JOIN Server ON Server.Id = UserServer.ServerId "
            "JOIN User ON User.Id = UserServer.UserId WHERE Server.Server = ? AND UserServer.Verified "
            "IS NULL", [server.id]).fetchall())
    )
    conn.close()
    unverified_list = []
    for user_id in unverified_ids:
        unverified_list.append(discord.utils.get(server.members, id=user_id))
    return unverified_list


def set_verification(user, server, verified):
    conn = DBManager.get_db_connection()
    user_id = get_user_id(user)
    server_id = get_server_id(server)
    conn.cursor().execute("UPDATE UserServer SET Verified = ? WHERE UserId = ? AND ServerId = ?",
                          [verified, user_id, server_id])
    conn.commit()
    DBManager.close_db_connection(conn)
    return


def set_banned(user, server, banned):
    conn = DBManager.get_db_connection()
    user_id = get_user_id(user)
    server_id = get_server_id(server)
    conn.cursor().execute("UPDATE UserServer SET Banned = ? WHERE UserId = ? AND ServerId = ?",
                          [banned, user_id, server_id])
    conn.commit()
    DBManager.close_db_connection(conn)
    return


def update_dota_settings(server, column, new_value):
    conn = DBManager.get_db_connection()

    DBManager.close_db_connection(conn)
    return


def update_discord_settings(server, column, new_value):
    conn = DBManager.get_db_connection()
    conn.cursor().execute(f"""UPDATE ServerSettings SET {column} = ? FROM (SELECT Server.Id FROM Server WHERE Server.Server = ?) AS test 
                            WHERE test.id = ServerSettings.ServerId""", [new_value, server.id])
    DBManager.close_db_connection(conn)
    return


def load_server_settings(server):
    conn = DBManager.get_db_connection()
    settings = list(conn.cursor().execute("""SELECT Stg.AfkTimer, Stg.SkillFloor, Stg.SkillCeiling, Stg.QueueName FROM 
                                          ServerSettings Stg JOIN Server Srv ON Stg.ServerId = Srv.Id WHERE Srv.Server 
                                          = ?""", [server.id]))
    DBManager.close_db_connection(conn)
    return list(settings[0])


def setup_autolobby():
    conn = DBManager.get_db_connection()
    data = [1, 0]
    conn.cursor().execute("""INSERT INTO Autolobby (Id, Active) VALUES (?, ?)""", data)
    conn.commit()
    DBManager.close_db_connection(conn)


def update_autolobby(value):
    conn = DBManager.get_db_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE Autolobby SET Active = ? WHERE Id = ?""", value)
    conn.commit()
    DBManager.close_db_connection(conn)


def check_autolobby():
    conn = DBManager.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Active from Autolobby where Id=?", [1])
    match_state = cur.fetchone()[0]
    print(match_state)
    DBManager.close_db_connection(conn)
    return match_state


def update_user_data(discord_id, column, new_data):
    conn = DBManager.get_db_connection()
    cur = conn.cursor()
    if column == "roles":
        new_data.append(discord_id)
        cur.execute("UPDATE Users SET Pos1 = ?, Pos2 = ?, Pos3 = ?, Pos4 = ?, Pos5 = ? WHERE disc=?", new_data)
    else:
        cur.execute(f"UPDATE User SET {column} = ? WHERE Discord = ?", [new_data, discord_id])
    DBManager.close_db_connection(conn)
    cur.close()


def check_discord_exists(user_id):
    return check_for_value("Discord", user_id)


def check_steam_exists(steam_id):
    return check_for_value("Steam", steam_id)


def check_for_value(column, value_check):
    conn = DBManager.get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM User WHERE {column} = ?)", [value_check])
    item = cur.fetchone()[0]
    if item == 0:
        variable = False
    else:
        variable = True
    DBManager.close_db_connection(conn)
    return variable


def view_user_data(discord_id):
    conn = DBManager.get_db_connection()
    user_data_list = list(
        conn.cursor().execute("SELECT Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated FROM "
                              "User WHERE Discord=?", [discord_id]))
    DBManager.close_db_connection(conn)
    return list(user_data_list[0])


def add_user_data(player):
    player.append(datetime.today().strftime('%Y-%m-%d'))
    conn = DBManager.get_db_connection()
    conn.cursor().execute("INSERT INTO User (Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated) VALUES "
                          "(?, ?, ?, ?, ?, ?, ?, ?, ?)", player)
    DBManager.close_db_connection(conn)
    conn.close()


def remove_user_data(user, server):
    conn = DBManager.get_db_connection()
    user_id = get_user_id(user)
    server_id = get_server_id(server)
    conn.cursor().execute("""DELETE FROM UserServer where UserId = ? AND ServerId = ?""", [user_id, server_id])
    DBManager.close_db_connection(conn)
    conn.close()


def get_queue_user_data(queue_ids):
    conn = DBManager.get_db_connection()
    id_tuple = tuple(queue_ids)
    user_data = pd.read_sql_query("SELECT * FROM Users WHERE disc IN {};".format(id_tuple), conn)
    DBManager.close_db_connection(conn)
    return user_data
