import discord.utils
import pandas as pd
import team_balancer
import sqlite3
import random
from datetime import datetime
import networkx as nx
from networkx.algorithms import bipartite
from dotenv import get_key


def get_db_connection():
    conn = sqlite3.connect(f'../../data/inhouse.db')
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_discord_token():
    return get_key("../../credentials/.env", "TOKEN")


def check_server_in_db(server):
    conn = get_db_connection()
    check = conn.cursor().execute("""SELECT * FROM Server WHERE Server = ?; """, [server.id]).fetchall()
    conn.close()
    return check


def add_server_to_db(server):
    conn = get_db_connection()
    conn.cursor().execute("""INSERT INTO Server (Server) VALUES (?)""", [server.id])
    conn.commit()
    conn.close()
    return


def check_server_settings(server):
    conn = get_db_connection()
    server_details = list(conn.cursor().execute("""SELECT ServerSettings.ServerId FROM ServerSettings INNER JOIN Server
                                                ON ServerSettings.ServerId = Server.Id WHERE Server.Server = ?""",
                                                [server.id]))
    conn.close()
    return server_details


def register_server(server, setup_list):
    conn = get_db_connection()
    conn.cursor().execute("""UPDATE Server SET AdminChannel = ?, QueueChannel = ?, GlobalChannel = ?, ChatChannel = ?, 
                                AdminRole = ? WHERE Server = ?""", [setup_list[0], setup_list[1], setup_list[2],
                                                                    setup_list[3], setup_list[4], server.id])
    conn.commit()
    conn.close()


def add_default_settings(server):
    conn = get_db_connection()
    conn.cursor().execute("""INSERT INTO ServerSettings (ServerId, AfkTimer, SkillFloor, SkillCeiling, QueueName)
                            VALUES ((SELECT Id from Server where Server = ?), 15, 0, 6000, "INHOUSE")""",
                          [server.id])
    conn.commit()
    conn.close()


def load_channel_id(server, channel_name):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    channel_id = list(
        conn.cursor().execute(f'SELECT {channel_name} FROM Server where Server = ?', [server.id]).fetchall())
    conn.close()
    return channel_id[0]


def load_admin_role(server):
    admin_id = load_id_from_server(server, "AdminRole")
    return discord.utils.get(server.roles, id=admin_id)


def load_champion_role(server):
    champion_id = load_id_from_server(server, "ChampionRole")
    return discord.utils.get(server.roles, id=champion_id)


def load_id_from_server(server, column):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    column_id = list(
        conn.cursor().execute(f'SELECT {column} FROM Server where Server = ?', [server.id]).fetchall())
    conn.close()
    return column_id[0]


def get_user_status(user, server):
    conn = get_db_connection()
    user_status = list(
        conn.cursor().execute("""SELECT UserServer.Verified, UserServer.Banned FROM UserServer JOIN User 
        ON User.Id = UserServer.UserId JOIN Server ON Server.Id = UserServer.ServerId WHERE User.Discord = ? AND Server.Server = ?""",
                              [user.id, server.id]))
    conn.close()
    return list(user_status[0])


def user_registered(user):
    conn = get_db_connection()
    user_id = list(conn.cursor().execute("""SELECT UserServer.UserId FROM UserServer INNER JOIN User ON 
                                            User.Id = UserServer.UserId WHERE User.Discord = ?""", [user.id]))
    conn.close()
    return user_id


def get_user_id(user):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    user_id = list(conn.cursor().execute("""SELECT Id FROM User WHERE Discord = ?""", [user.id]))
    conn.close()
    if not user_id:
        return 0
    return user_id[0]


def get_server_id(server):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    server_id = list(conn.cursor().execute("""SELECT Id FROM Server WHERE Server = ?""", [server.id]))
    conn.close()
    return server_id[0]


def auto_register(user, server):
    user_id = get_user_id(user)
    if user_id == 0:
        return False
    server_id = get_server_id(server)
    conn = get_db_connection()
    conn.cursor().execute("""INSERT INTO UserServer (UserId, ServerId, Banned) VALUES (?, ?, 0)""",
                          [user_id, server_id])
    conn.commit()
    conn.close()
    return True


def get_unverified_users(server):
    conn = get_db_connection()
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
    conn = get_db_connection()
    user_id = get_user_id(user)
    server_id = get_server_id(server)
    conn.cursor().execute("UPDATE UserServer SET Verified = ? WHERE UserId = ? AND ServerId = ?",
                          [verified, user_id, server_id])
    conn.commit()
    conn.close()
    return


def load_config_data(server, category):
    return


def update_league(new_value):
    return


def update_config(server, column, new_value):
    return


def load_server_settings(server):
    conn = get_db_connection()
    settings = list(conn.cursor().execute("""SELECT Stg.AfkTimer, Stg.SkillFloor, Stg.SkillCeiling, Stg.QueueName FROM 
                                          ServerSettings Stg JOIN Server Srv ON Stg.ServerId = Srv.Id WHERE Srv.Server 
                                          = ?""", [server.id]))
    conn.close()
    return list(settings[0])


def setup_autolobby():
    conn = get_db_connection()
    data = [1, 0]
    conn.cursor().execute("""INSERT INTO Autolobby (Id, Active) VALUES (?, ?)""", data)
    conn.commit()
    conn.close()


def update_autolobby(value):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""UPDATE Autolobby SET Active = ? WHERE Id = ?""", value)
    conn.commit()
    conn.close()


def check_autolobby():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT Active from Autolobby where Id=?", [1])
    match_state = cur.fetchone()[0]
    print(match_state)
    conn.close()
    return match_state


def update_user_data(discord_id, column, new_data):
    conn = get_db_connection()
    cur = conn.cursor()
    if column == "roles":
        new_data.append(discord_id)
        cur.execute("UPDATE Users SET Pos1 = ?, Pos2 = ?, Pos3 = ?, Pos4 = ?, Pos5 = ? WHERE disc=?", new_data)
    else:
        cur.execute(f"UPDATE User SET {column} = ? WHERE Discord = ?", [new_data, discord_id])
    conn.commit()
    cur.close()


def check_discord_exists(user_id):
    return check_for_value("Discord", user_id)


def check_steam_exists(steam_id):
    return check_for_value("Steam", steam_id)


def check_for_value(column, value_check):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM User WHERE {column} = ?)", [value_check])
    item = cur.fetchone()[0]
    if item == 0:
        variable = False
    else:
        variable = True
    conn.close()
    return variable


def view_user_data(discord_id):
    conn = get_db_connection()
    user_data_list = list(
        conn.cursor().execute("SELECT Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated FROM "
                              "User WHERE Discord=?", [discord_id]))
    conn.close()
    return list(user_data_list[0])


def add_user_data(player):
    player.append(datetime.today().strftime('%Y-%m-%d'))
    conn = get_db_connection()
    conn.cursor().execute("INSERT INTO User (Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated) VALUES "
                          "(?, ?, ?, ?, ?, ?, ?, ?, ?)", player)
    conn.commit()
    conn.close()


def remove_user_data(discord_id):
    conn = get_db_connection()
    conn.cursor().execute("""DELETE FROM User where disc=?""", [discord_id])
    conn.commit()
    conn.close()


def assign_teams(queue_ids):
    id_tuple = tuple(queue_ids)
    conn = get_db_connection()
    user_data = pd.read_sql_query("SELECT * FROM Users WHERE disc IN {};".format(id_tuple), conn)
    queue = user_data.sort_values('mmr', ascending=False)
    team_uno = team_balancer.sort_balancer(queue['mmr'].tolist())
    team_dos = team_balancer.mean_balancer(queue['mmr'].tolist())
    team_tres = team_balancer.draft_balancer(queue['mmr'].tolist())
    queue["team_uno"] = team_uno
    queue["team_dos"] = team_dos
    queue["team_tres"] = team_tres
    delta1 = abs(queue.loc[queue['team_uno'] == "Team 1", 'mmr'].mean() - queue.loc[
        queue['team_uno'] == "Team 2", 'mmr'].mean())
    delta2 = abs(queue.loc[queue['team_dos'] == "Team 1", 'mmr'].mean() - queue.loc[
        queue['team_dos'] == "Team 2", 'mmr'].mean())
    delta3 = abs(queue.loc[queue['team_tres'] == "Team 1", 'mmr'].mean() - queue.loc[
        queue['team_tres'] == "Team 2", 'mmr'].mean())
    delta_list = [delta1, delta2, delta3]
    allowed_range = 100
    delta_choices = []
    while not delta_choices:
        delta_choices = [i for i in delta_list if i < allowed_range]
        allowed_range += 50
    print(delta_list)
    print(delta_choices)
    random_delta = random.choice(delta_choices)
    print(random_delta)
    if random_delta == delta1:
        queue = queue.drop(columns="team_dos")
        queue = queue.drop(columns="team_tres")
        queue = queue.rename(columns={"team_uno": "team"})
    elif random_delta == delta2:
        queue = queue.drop(columns="team_uno")
        queue = queue.drop(columns="team_tres")
        queue = queue.rename(columns={"team_dos": "team"})
    else:
        queue = queue.drop(columns="team_uno")
        queue = queue.drop(columns="team_dos")
        queue = queue.rename(columns={"team_tres": "team"})
    team1 = queue.loc[queue['team'] == "Team 1"]
    team2 = queue.loc[queue['team'] == "Team 2"]
    pos1 = role_allocation(team1)
    team1["pos"] = [11, 12, 13, 14, 15]
    team1.at[pos1[5001], 'pos'] = 1
    team1.at[pos1[5002], 'pos'] = 2
    team1.at[pos1[5003], 'pos'] = 3
    team1.at[pos1[5004], 'pos'] = 4
    team1.at[pos1[5005], 'pos'] = 5
    team1 = team1.sort_values('pos')
    pos2 = role_allocation(team2)
    team2["pos"] = [11, 12, 13, 14, 15]
    team2.at[pos2[5001], 'pos'] = 1
    team2.at[pos2[5002], 'pos'] = 2
    team2.at[pos2[5003], 'pos'] = 3
    team2.at[pos2[5004], 'pos'] = 4
    team2.at[pos2[5005], 'pos'] = 5
    team2 = team2.sort_values('pos')
    # queue = pd.concat([team1, team2])
    # queue.to_csv("../../data/match.csv", index=False)
    # with open('../../data/activate.txt', 'r+') as f:
    #     f.truncate(0)
    #     f.write('yes')
    return team1['disc'].tolist(), team2['disc'].tolist()


def role_allocation(team):
    graph = nx.Graph()
    for i in range(0, 5):
        graph.add_node(team.index[i])
        for j in range(1, 6):
            graph.add_node(j + 5000)
            graph.add_edge(team.index[i], j + 5000, weight=team.iloc[[i], [j + 2]].values.min())
    return bipartite.minimum_weight_full_matching(graph, top_nodes=None, weight='weight')
