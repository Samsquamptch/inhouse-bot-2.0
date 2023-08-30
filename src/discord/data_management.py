# For all functions relating to adding/removing/amending/viewing from users.csv

import pandas as pd
import csv
import networkx as nx
from networkx.algorithms import bipartite
import scipy

def update_user_data(discord_id, columns, new_data):
    user_data = pd.read_csv("../../data/users.csv")
    updated_user = user_data.query(f'disc=={discord_id}')
    user_data.iloc[updated_user.index, columns] = new_data
    user_data.to_csv("../../data/users.csv", index=False)


def check_for_value(value_check):
    user_data = pd.read_csv("../../data/users.csv")
    if value_check not in user_data.values:
        variable = False
        return variable
    else:
        variable = True
        return variable

# def remove_user_data(discord_id):


def view_user_data(discord_id):
    user_data = pd.read_csv("../../data/users.csv")
    user_data_list = user_data.query(f'disc=={discord_id}').values.flatten().tolist()
    return user_data_list

def add_user_data(player):
    with open('../../data/users.csv', 'a', encoding='UTF8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(player)


def remove_user_data(discord_id):
    user_data = pd.read_csv("../../data/users.csv")
    updated_user = user_data.query(f'disc=={discord_id}')
    user_data = user_data.drop(updated_user.index)
    user_data.to_csv("../../data/users.csv", index=False)

def team_draft_balancer(list_mmr):
    team_order = []
    total = 0
    for mmr in list_mmr:
        total = total + mmr
    mmr_avg = total / 10
    print(total)
    print(mmr_avg)
    radiant = 0
    dire = 0
    radiant = radiant + list_mmr[0] + list_mmr[-1]
    team_order.append("Team 1")
    dire = dire + list_mmr[1] + list_mmr[-2]
    team_order.append("Team 2")
    if radiant > dire:
        dire = dire + list_mmr[2]
        radiant = radiant + list_mmr[3]
        team_order.append("Team 2")
        team_order.append("Team 1")
    else:
        radiant = radiant + list_mmr[2]
        dire = dire + list_mmr[3]
        team_order.append("Team 1")
        team_order.append("Team 2")
    if radiant > dire:
        dire = dire + list_mmr[4]
        radiant = radiant + list_mmr[5]
        team_order.append("Team 2")
        team_order.append("Team 1")
    else:
        radiant = radiant + list_mmr[4]
        dire = dire + list_mmr[5]
        team_order.append("Team 1")
        team_order.append("Team 2")
    if radiant > dire:
        dire = dire + list_mmr[6]
        radiant = radiant + list_mmr[7]
        team_order.append("Team 2")
        team_order.append("Team 1")
    else:
        radiant = radiant + list_mmr[6]
        dire = dire + list_mmr[7]
        team_order.append("Team 1")
        team_order.append("Team 2")
    team_order.append("Team 2")
    team_order.append("Team 1")
    radiant_avg = radiant / 5
    dire_avg = dire / 5
    print(radiant_avg)
    print(dire_avg)
    return team_order

def queue_pop(queue_ids):
    user_data = pd.read_csv("../../data/users.csv")
    queue = user_data.query("disc in @queue_ids")
    queue = queue.sort_values('mmr', ascending=False)
    team_uno = ["Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2"]
    team_dos = ["Team 1", "Team 2", "Team 2", "Team 1", "Team 1", "Team 2", "Team 2", "Team 1", "Team 1", "Team 2"]
    team_tres = team_draft_balancer(queue['mmr'].tolist())
    queue["team_uno"] = team_uno
    queue["team_dos"] = team_dos
    queue["team_tres"] = team_tres
    delta1 = queue.loc[queue['team_uno'] == "Team 1", 'mmr'].mean() - queue.loc[queue['team_uno'] == "Team 2", 'mmr'].mean()
    delta2 =queue.loc[queue['team_dos'] == "Team 1", 'mmr'].mean() - queue.loc[queue['team_dos'] == "Team 2", 'mmr'].mean()
    delta3 = queue.loc[queue['team_tres'] == "Team 1", 'mmr'].mean() - queue.loc[queue['team_tres'] == "Team 2", 'mmr'].mean()
    if delta3 <= delta1 and delta3 <= delta2:
        queue = queue.drop(columns="team_uno")
        queue = queue.drop(columns="team_dos")
        queue = queue.rename(columns={"team_tres": "team"})
    if delta1 <= delta2:
        queue = queue.drop(columns="team_dos")
        queue = queue.rename(columns={"team_uno": "team"})
        team1 = queue.loc[queue['team'] == "Team 1"]
        team2 = queue.loc[queue['team'] == "Team 2"]
        pos1 = pos_graph(team1)
        team1["pos"] = [11,12,13,14,15]
        team1.at[pos1[11], 'pos'] = 1
        team1.at[pos1[12], 'pos'] = 2
        team1.at[pos1[13], 'pos'] = 3
        team1.at[pos1[14], 'pos'] = 4
        team1.at[pos1[15], 'pos'] = 5
        team1 = team1.sort_values('pos')
        pos2 = pos_graph(team2)
        team2["pos"] = [11, 12, 13, 14, 15]
        team2.at[pos2[11], 'pos'] = 1
        team2.at[pos2[12], 'pos'] = 2
        team2.at[pos2[13], 'pos'] = 3
        team2.at[pos2[14], 'pos'] = 4
        team2.at[pos2[15], 'pos'] = 5
        team2 = team2.sort_values('pos')
        queue = pd.concat([team1, team2])
        queue.to_csv("../../data/match.csv", index=False)
        return team1['disc'].tolist(), team2['disc'].tolist()
    else:
        queue = queue.drop(columns="team_uno")
        queue = queue.rename(columns={"team_dos": "team"})
        team1 = queue.loc[queue['team'] == "Team 1"]
        team2 = queue.loc[queue['team'] == "Team 2"]
        pos1 = pos_graph(team1)
        team1["pos"] = [11, 12, 13, 14, 15]
        team1.at[pos1[11], 'pos'] = 1
        team1.at[pos1[12], 'pos'] = 2
        team1.at[pos1[13], 'pos'] = 3
        team1.at[pos1[14], 'pos'] = 4
        team1.at[pos1[15], 'pos'] = 5
        team1 = team1.sort_values('pos')
        pos2 = pos_graph(team2)
        team2["pos"] = [11, 12, 13, 14, 15]
        team2.at[pos2[11], 'pos'] = 1
        team2.at[pos2[12], 'pos'] = 2
        team2.at[pos2[13], 'pos'] = 3
        team2.at[pos2[14], 'pos'] = 4
        team2.at[pos2[15], 'pos'] = 5
        team2 = team2.sort_values('pos')
        queue = pd.concat([team1,team2])
        queue.to_csv("../../data/match.csv", index=False)
        return team1['disc'].tolist(), team2['disc'].tolist()



def pos_graph(team):
    G = nx.Graph()
    for i in range(0, 5):
        G.add_node(team.index[i])
        for j in range(1, 6):
            G.add_node(j + 10)
            G.add_edge(team.index[i], j + 10, weight=team.iloc[[i], [j + 2]].values.min())
    return bipartite.minimum_weight_full_matching(G, top_nodes=None, weight='weight')
