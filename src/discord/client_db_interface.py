import discord.utils
import pandas as pd
from datetime import datetime
from dotenv import get_key
import discord_database_access as db_access


def get_discord_token():
    return get_key("../../credentials/.env", "TOKEN")


def check_server_in_db(server):
    conn = db_access.get_db_connection()
    check = conn.cursor().execute("""SELECT * FROM Server WHERE Server = ?; """, [server.id]).fetchall()
    db_access.close_db_connection(conn)
    return check


def add_server_to_db(server):
    conn = db_access.get_db_connection()
    conn.cursor().execute("""INSERT INTO Server (Server) VALUES (?)""", [server.id])
    conn.commit()
    db_access.close_db_connection(conn)
    return


def check_server_settings(server):
    conn = db_access.get_db_connection()
    server_details = list(conn.cursor().execute("""SELECT ServerSettings.ServerId FROM ServerSettings INNER JOIN Server
                                                ON ServerSettings.ServerId = Server.Id WHERE Server.Server = ?""",
                                                [server.id]))
    db_access.close_db_connection(conn)
    return server_details


def register_server(server, setup_list):
    conn = db_access.get_db_connection()
    conn.cursor().execute("""UPDATE Server SET AdminChannel = ?, QueueChannel = ?, GlobalChannel = ?, ChatChannel = ?, 
                                AdminRole = ? WHERE Server = ?""", [setup_list[0], setup_list[1], setup_list[2],
                                                                    setup_list[3], setup_list[4], server.id])
    conn.commit()
    db_access.close_db_connection(conn)


def add_default_settings(server):
    conn = db_access.get_db_connection()
    conn.cursor().execute("""INSERT INTO ServerSettings (ServerId, AfkTimer, SkillFloor, SkillCeiling, QueueName, Tryhard)
                            VALUES ((SELECT Id from Server where Server = ?), 15, 0, 6000, "INHOUSE", False)""",
                          [server.id])
    conn.cursor().execute("""INSERT INTO MessageIds (ServerId) VALUES ((SELECT Id from Server where Server = ?))""",
                          [server.id])
    conn.commit()
    db_access.close_db_connection(conn)


def load_admin_channel(server):
    channel_id = db_access.load_channel_id(server, "AdminChannel")
    return discord.utils.get(server.channels, id=channel_id)


def load_queue_channel(server):
    channel_id = db_access.load_channel_id(server, "QueueChannel")
    return discord.utils.get(server.channels, id=channel_id)


def load_global_channel(server):
    channel_id = db_access.load_channel_id(server, "QueueChannel")
    return discord.utils.get(server.channels, id=channel_id)


def load_chat_channel(server):
    channel_id = db_access.load_channel_id(server, "ChatChannel")
    return discord.utils.get(server.channels, id=channel_id)


def check_chat_channel(message_channel, server):
    chat_channel_id = db_access.load_channel_id(server, "ChatChannel")
    return message_channel.id == chat_channel_id


def update_message_ids(server, messages):
    conn = db_access.get_db_connection()
    conn.cursor().execute("""UPDATE MessageIds SET AdminPanel = ?, AdminMenu = ?, UserButtons = ?, UserMenu = ?, 
                             InhouseQueue = ?, GlobalQueue = ? WHERE ServerId IN (SELECT Id from Server where Server = ?)""",
                          [messages[0], messages[1], messages[2], messages[3], messages[4], messages[5], server.id])
    conn.commit()
    db_access.close_db_connection(conn)


def load_message_ids(server):
    conn = db_access.get_db_connection()
    message_ids = list(conn.cursor().execute("""SELECT mid.AdminPanel, mid.AdminMenu, mid.UserButtons, mid.UserMenu, 
                             mid.InhouseQueue, mid.GlobalQueue FROM MessageIds mid JOIN Server srv ON mid.ServerId = 
                             srv.Id WHERE srv.Server = ?""", [server.id]))
    db_access.close_db_connection(conn)
    return message_ids[0]


def check_admin(user, server):
    admin_role = load_admin_role(server)
    if admin_role not in user.roles:
        return False
    else:
        return True


def load_admin_role(server):
    admin_id = db_access.load_id_from_server(server, "AdminRole")
    return discord.utils.get(server.roles, id=admin_id)


def load_champion_role(server):
    champion_id = db_access.load_id_from_server(server, "ChampionRole")
    return discord.utils.get(server.roles, id=champion_id)


def check_if_champion(user, server):
    if not hasattr(user, 'roles'):
        return False
    champion_role = load_champion_role(server)
    if champion_role in user.roles:
        return True
    return False


def get_banned_status(user, server):
    conn = db_access.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    banned_status = list(
        conn.cursor().execute("""SELECT UserServer.Banned FROM UserServer JOIN User 
            ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user.id, server.id]))
    db_access.close_db_connection(conn)
    return banned_status[0]


def get_verified_status(user, server):
    conn = db_access.get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    verified_status = list(
        conn.cursor().execute("""SELECT UserServer.Verified FROM UserServer JOIN User 
            ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user.id, server.id]))
    db_access.close_db_connection(conn)
    return verified_status[0]


def get_user_status(user, server):
    status_list = db_access.load_user_status(user.id, server.id)
    if not status_list[0]:
        return ""
    verified = status_list[0][0]
    banned = status_list[0][1]
    if banned:
        return "banned"
    if verified:
        return "verified"
    return ""


def user_registered(user, server):
    conn = db_access.get_db_connection()
    user_id = list(conn.cursor().execute("""SELECT usv.UserId FROM UserServer usv INNER JOIN User usr ON usr.Id = usv.UserId 
                                            JOIN Server svr ON svr.Id = usv.ServerId WHERE usr.Discord = ? AND svr.Server 
                                            = ?""", [user.id, server.id]))
    db_access.close_db_connection(conn)
    return user_id


def auto_register(user, server):
    user_id = db_access.get_user_id(user)
    if user_id == 0:
        return False
    server_id = db_access.load_server_id(server)
    conn = db_access.get_db_connection()
    conn.cursor().execute("""INSERT INTO UserServer (UserId, ServerId, Banned, Wins, Losses) VALUES (?, ?, 0, 0, 0)""",
                          [user_id, server_id])
    conn.commit()
    db_access.close_db_connection(conn)
    return True


def get_unverified_users(server):
    unverified_ids = db_access.load_unverified_ids(server)
    unverified_list = []
    for user in unverified_ids:
        unverified_list.append(user)
    return unverified_list


def enable_verification(user, server):
    db_access.set_verification(user, server, True)


def disable_verification(user, server):
    db_access.set_verification(user, server, False)


def ban_user(user, server):
    db_access.set_banned(user, server, True)


def unban_user(user, server):
    db_access.set_banned(user, server, False)


def update_dota_settings(server, column, new_value):
    conn = db_access.get_db_connection()

    db_access.close_db_connection(conn)
    return


def load_tryhard_settings(server):
    conn = db_access.get_db_connection()
    tryhard = list(conn.cursor().execute("""SELECT Stg.Tryhard FROM ServerSettings Stg JOIN Server Srv ON Stg.ServerId 
                                            = Srv.Id WHERE Srv.Server = ?""", [server.id]))
    db_access.close_db_connection(conn)
    return tryhard[0]


def update_discord_settings(server, column, new_value):
    conn = db_access.get_db_connection()
    conn.cursor().execute(f"""UPDATE ServerSettings SET {column} = ? FROM (SELECT Server.Id FROM Server WHERE Server.Server = ?) 
                            AS Upds WHERE Upds.id = ServerSettings.ServerId""", [new_value, server.id])
    db_access.close_db_connection(conn)
    return


def load_server_settings(server):
    conn = db_access.get_db_connection()
    settings = list(conn.cursor().execute("""SELECT Stg.AfkTimer, Stg.SkillFloor, Stg.SkillCeiling, Stg.QueueName FROM 
                                          ServerSettings Stg JOIN Server Srv ON Stg.ServerId = Srv.Id WHERE Srv.Server 
                                          = ?""", [server.id]))
    db_access.close_db_connection(conn)
    return list(settings[0])


def setup_autolobby():
    conn = db_access.get_db_connection()
    data = [1, 0]
    conn.cursor().execute("""INSERT INTO Autolobby (Id, Active) VALUES (?, ?)""", data)
    conn.commit()
    db_access.close_db_connection(conn)


def update_autolobby(value):
    conn = db_access.get_db_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE Autolobby SET Active = ? WHERE Id = ?""", value)
    conn.commit()
    db_access.close_db_connection(conn)


def check_autolobby():
    conn = db_access.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Active from Autolobby where Id=?", [1])
    match_state = cur.fetchone()[0]
    print(match_state)
    db_access.close_db_connection(conn)
    return match_state


def update_user_data(discord_id, column, new_data):
    conn = db_access.get_db_connection()
    cur = conn.cursor()
    if column == "roles":
        new_data.append(discord_id)
        cur.execute("UPDATE Users SET Pos1 = ?, Pos2 = ?, Pos3 = ?, Pos4 = ?, Pos5 = ? WHERE disc=?", new_data)
    else:
        cur.execute(f"UPDATE User SET {column} = ? WHERE Discord = ?", [new_data, discord_id])
    conn.commit()
    db_access.close_db_connection(conn)


def check_discord_exists(user_id):
    discord_list = db_access.check_for_value("Discord", user_id)
    return discord_list


def check_steam_exists(steam_id):
    discord_list = db_access.check_for_value("Steam", steam_id)
    return discord_list


def view_user_data(discord_id):
    conn = db_access.get_db_connection()
    user_data_list = list(
        conn.cursor().execute("SELECT Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated FROM "
                              "User WHERE Discord=?", [discord_id]))
    db_access.close_db_connection(conn)
    return list(user_data_list[0])


def get_user_stats(user, server):
    conn = db_access.get_db_connection()
    user_data_list = list(
        conn.cursor().execute(
            "SELECT usr.Discord, usr.Steam, usr.MMR, usr.Pos1, usr.Pos2, usr.Pos3, usr.Pos4, usr.Pos5, "
            "usv.Wins, usv.Losses FROM User usr JOIN UserServer usv ON usr.Id = usv.UserId JOIN Server srv "
            "ON usv.ServerId = srv.Id WHERE usr.Discord = ? AND srv.Server = ?", [user.id, server.id]))
    db_access.close_db_connection(conn)
    return list(user_data_list[0])


def add_user_data(player):
    player.append(datetime.today().strftime('%Y-%m-%d'))
    conn = db_access.get_db_connection()
    conn.cursor().execute("INSERT INTO User (Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated) VALUES "
                          "(?, ?, ?, ?, ?, ?, ?, ?, ?)", player)
    conn.commit()
    db_access.close_db_connection(conn)
    conn.close()


def remove_user_data(user, server):
    conn = db_access.get_db_connection()
    user_id = db_access.get_user_id(user)
    server_id = db_access.load_server_id(server)
    conn.cursor().execute("""DELETE FROM UserServer where UserId = ? AND ServerId = ?""", [user_id, server_id])
    conn.commit()
    db_access.close_db_connection(conn)
    conn.close()


def get_queue_user_data(queue_ids):
    conn = db_access.get_db_connection()
    user_data = list(
        conn.cursor().execute("SELECT Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5 FROM User WHERE Discord IN (?,?,?,?,?,?,?,?,?,?)",
                              [queue_ids[0], queue_ids[1], queue_ids[2], queue_ids[3], queue_ids[4], queue_ids[5], queue_ids[6],
                               queue_ids[7], queue_ids[8], queue_ids[9]]))
    queue_data = []
    for user in user_data:
        queue_data.append(flip_values(list(user)))
    db_access.close_db_connection(conn)
    return queue_data


# Due to how the role balancer calculations work, number weighting is saved the opposite to how users are used to (which
# is higher number = more pref and lower number = less pref). This swap shows what users expect to see, instead of what
# is actually happening behind the scenes (low num = more pref and high num = less pref).
def flip_values(data_list):
    data_numbers = [3, 4, 5, 6, 7]
    for n in data_numbers:
        match data_list[n]:
            case 1:
                data_list[n] = 5
            case 2:
                data_list[n] = 4
            case 3:
                data_list[n] = 3
            case 4:
                data_list[n] = 2
            case 5:
                data_list[n] = 1
    return data_list


def count_users(server):
    conn = db_access.get_db_connection()
    user_count = conn.cursor().execute(f"""SELECT COUNT(usv.UserId) FROM UserServer usv JOIN Server srv ON usv.ServerId = 
                                    srv.Id WHERE srv.Server = ?""", [server.id]).fetchone()
    verified_count = conn.cursor().execute(f"""SELECT COUNT(usv.UserId) FROM UserServer usv JOIN Server srv ON usv.ServerId = 
                                    srv.Id WHERE srv.Server = ? AND usv.Verified""", [server.id]).fetchone()
    banned_count = conn.cursor().execute(f"""SELECT COUNT(usv.UserId) FROM UserServer usv JOIN Server srv ON usv.ServerId = 
                                    srv.Id WHERE srv.Server = ? AND usv.Banned""", [server.id]).fetchone()
    conn.close()
    return user_count[0], verified_count[0], banned_count[0]


def load_banned_users(server):
    conn = db_access.get_db_connection()
    ban_list = list(conn.cursor().execute(f"""SELECT usr.Discord, usr.Steam FROM User usr JOIN UserServer usv ON usr.Id = usv.UserId 
                                        JOIN Server srv ON usv.ServerId = srv.Id WHERE srv.Server = ? AND usv.Banned""",
                                          [server.id]))
    return ban_list


def get_user_mmr(user):
    conn = db_access.get_db_connection()
    user_mmr = list(conn.cursor().execute(f"""SELECT MMR FROM User WHERE Discord = ?""", [user.id]))
    db_access.close_db_connection(conn)
    return user_mmr[0][0]


def load_users_below_mmr(mmr_cap, server):
    conn = db_access.get_db_connection()
    user_list = list(conn.cursor().execute("""SELECT usr.Discord, usr.Steam, usr.MMR, usr.Pos1, usr.Pos2, usr.Pos3, usr.Pos4, 
                                            usr.Pos5 FROM User usr JOIN UserServer usv ON usv.UserId = usr.Id JOIN Server srv 
                                            ON srv.ID = usv.ServerId WHERE usr.MMR < ? AND srv.Server = ? ORDER BY MMR Desc 
                                            LIMIT 10""", [mmr_cap, server.id]))
    db_access.close_db_connection(conn)
    return user_list


def user_within_mmr_range(user, mmr_bot, mmr_top):
    conn = db_access.get_db_connection()
    is_below = list(conn.cursor().execute("""SELECT Discord FROM User WHERE Discord = ? AND MMR BETWEEN ? AND ?""",
                                          [user.id, mmr_bot, mmr_top]))
    db_access.close_db_connection(conn)
    return is_below
