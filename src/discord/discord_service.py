import pandas as pd
import team_balancer
import sqlite3
import yaml
import random
from datetime import datetime
from yaml.loader import SafeLoader
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
                                                on ServerSettings.ServerId = Server.Id
                                                WHERE Server.Server = ?""",
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
                            VALUES ((SELECT Id from Server where Server = ?), 15, 0, 6000, "Inhouse Queue")""", [server.id])
    conn.commit()
    conn.close()

def load_channel_id(server, channel_name):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    channel_id = list(conn.cursor().execute(f'SELECT {channel_name} FROM Server where Server = ?', [server.id]).fetchall())
    conn.close()
    return channel_id[0]

def get_unverified_users(server):
    conn = get_db_connection()
    conn.row_factory = lambda cursor, row: row[0]
    unverified_list = list(conn.cursor().execute("""SELECT UserId FROM UserServer WHERE ServerId = ? AND Verified IS NULL""",
                          [server.id]).fetchall())
    conn.close()
    return unverified_list


def set_verification(user_id, verified):
    conn = get_db_connection()
    conn.cursor().execute("""UPDATE UserServer SET Verified = ? WHERE UserId = ?""", [verified, user_id])
    conn.commit()
    conn.close()
    return

def load_config_data(server, category):
    with open(f'../../data/{server}_config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    print(category)
    return data


def update_league(new_value):
    with open(f'../../credentials/credentials_steam.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
        data['LEAGUE'] = int(new_value)
        with open(f'../../credentials/credentials_steam.yml', 'w') as f:
            yaml.dump(data, f)


def update_config(server, category, sub_category, new_value):
    with open(f'../../data/{server.id}_config.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    data[category][sub_category] = new_value
    with open(f'../../data/{server.id}_config.yml', 'w') as f:
        yaml.dump(data, f)

def setup_autolobby(server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    data = [1, 0]
    cur.execute("""INSERT INTO Autolobby (Id, Active) VALUES (?, ?)""", data)
    conn.commit()
    conn.close()


def update_autolobby(server_id, value):
    conn = sqlite3.connect(f'../../data/inhouse_{server_id}.db')
    cur = conn.cursor()
    cur.execute("""UPDATE Autolobby SET Active = ? WHERE Id = ?""", value)
    conn.commit()
    conn.close()


def check_autolobby(server_id):
    conn = sqlite3.connect(f'../../data/inhouse_{server_id}.db')
    cur = conn.cursor()
    cur.execute("SELECT Active from Autolobby where Id=?", [1])
    match_state = cur.fetchone()[0]
    print(match_state)
    conn.close()
    return match_state


def update_user_data(discord_id, column, new_data, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    if column == "roles":
        new_data.append(discord_id)
        cur.execute("UPDATE Users SET pos1 = ?, pos2 = ?, pos3 = ?, pos4 = ?, pos5 = ? WHERE disc=?", new_data)
    else:
        cur.execute(f"UPDATE Users SET {column} = ? WHERE disc = ?", [new_data, discord_id])
    conn.commit()
    cur.close()


def check_for_value(column, value_check):
    conn = sqlite3.connect(f'../../data/inhouse.db')
    cur = conn.cursor()
    cur.execute(f"SELECT EXISTS(SELECT 1 FROM Users WHERE {column} = ?)", [value_check])
    item = cur.fetchone()[0]
    if item == 0:
        variable = False
    else:
        variable = True
    conn.close()
    return variable


def view_user_data(discord_id, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    user_data_list = list(cur.execute("SELECT * from Users WHERE disc=?", [discord_id]))
    conn.close()
    return list(user_data_list[0])


def add_user_data(player, server):
    player.append(datetime.today().strftime('%Y-%m-%d'))
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO Users (Discord, Steam, MMR, Pos1, Pos2, Pos3, Pos4, Pos5, LastUpdated) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", player)
    conn.commit()
    conn.close()


def remove_user_data(discord_id, server):
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
    cur = conn.cursor()
    cur.execute("""DELETE FROM Users where disc=?""", [discord_id])
    conn.commit()
    conn.close()


def assign_teams(queue_ids, server):
    id_tuple = tuple(queue_ids)
    conn = sqlite3.connect(f'../../data/inhouse_{server.id}.db')
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
