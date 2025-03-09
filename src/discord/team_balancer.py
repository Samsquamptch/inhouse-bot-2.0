import random

import networkx as nx
from networkx.algorithms import bipartite

from src.discord import client_db_interface, check_user


def assign_teams(queue_ids):
    user_data = client_db_interface.get_queue_user_data(queue_ids)
    queue = user_data.sort_values('mmr', ascending=False)
    team_uno = sort_balancer(queue['mmr'].tolist())
    team_dos = mean_balancer(queue['mmr'].tolist())
    team_tres = draft_balancer(queue['mmr'].tolist())
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
    return team1['disc'].tolist(), team2['disc'].tolist()


def role_allocation(team):
    graph = nx.Graph()
    for i in range(0, 5):
        graph.add_node(team.index[i])
        for j in range(1, 6):
            graph.add_node(j + 5000)
            graph.add_edge(team.index[i], j + 5000, weight=team.iloc[[i], [j + 2]].values.min())
    return bipartite.minimum_weight_full_matching(graph, top_nodes=None, weight='weight')


def draft_balancer(list_mmr):
    team_order1 = ['', '', '', '', '', '', '', '', '', '']
    radiant1 = 0
    dire1 = 0
    for n in range(0, 10, 2):
        if radiant1 == dire1 or radiant1 < dire1:
            radiant1 += list_mmr[n]
            dire1 += list_mmr[n + 1]
            team_order1[n] = "Team 1"
            team_order1[n + 1] = "Team 2"
        else:
            dire1 = dire1 + list_mmr[n]
            radiant1 = radiant1 + list_mmr[n + 1]
            team_order1[n] = "Team 2"
            team_order1[n + 1] = "Team 1"
    team_order2 = ['', '', '', '', '', '', '', '', '', '']
    radiant2 = 0
    dire2 = 0
    for n in range(8, -2, -2):
        if radiant2 == dire2 or radiant2 < dire2:
            radiant2 += list_mmr[n]
            dire2 += list_mmr[n + 1]
            team_order2[n] = "Team 1"
            team_order2[n + 1] = "Team 2"
        else:
            dire2 = dire2 + list_mmr[n]
            radiant2 = radiant2 + list_mmr[n + 1]
            team_order2[n] = "Team 2"
            team_order2[n + 1] = "Team 1"
    average1 = (radiant1 / 5) - (dire1 / 5)
    average2 = (radiant2 / 5) - (dire2 / 5)
    if abs(average1) < 100 and abs(average2) < 100:
        coin_flip = random.randint(1, 2)
        if coin_flip == 1:
            return team_order1
        else:
            return team_order2
    elif abs(average1) < abs(average2):
        return team_order1
    else:
        return team_order2


def sort_balancer(list_mmr):
    team_order1 = ["Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2"]
    radiant1 = list_mmr[0] + list_mmr[2] + list_mmr[4] + list_mmr[6] + list_mmr[8]
    dire1 = list_mmr[1] + list_mmr[3] + list_mmr[5] + list_mmr[7] + list_mmr[9]
    for n in range(8, 0, -2):
        if ((list_mmr[n] - list_mmr[n + 1]) / 2) < ((radiant1 / 5) - (dire1 / 5)):
            team_order1[n] = "Team 2"
            team_order1[n + 1] = "Team 1"
            radiant1 -= list_mmr[n]
            radiant1 += list_mmr[n + 1]
            dire1 += list_mmr[n]
            dire1 -= list_mmr[n + 1]
    team_order2 = ["Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2", "Team 1", "Team 2"]
    radiant2 = list_mmr[0] + list_mmr[2] + list_mmr[4] + list_mmr[6] + list_mmr[8]
    dire2 = list_mmr[1] + list_mmr[3] + list_mmr[5] + list_mmr[7] + list_mmr[9]
    for n in range(0, 10, 2):
        if ((list_mmr[n] - list_mmr[n + 1]) / 2) < ((radiant2 / 5) - (dire2 / 5)):
            team_order2[n] = "Team 2"
            team_order2[n + 1] = "Team 1"
            radiant2 -= list_mmr[n]
            radiant2 += list_mmr[n + 1]
            dire2 += list_mmr[n]
            dire2 -= list_mmr[n + 1]
    average1 = (radiant1 / 5) - (dire1 / 5)
    average2 = (radiant2 / 5) - (dire2 / 5)
    if abs(average1) < 100 and abs(average2) < 100:
        coin_flip = random.randint(1, 2)
        if coin_flip == 1:
            return team_order1
        else:
            return team_order2
    elif abs(average1) < abs(average2):
        return team_order1
    else:
        return team_order2


def mean_balancer(list_mmr):
    team_order1 = ['', '', '', '', '', '', '', '', '', '']
    radiant1 = 0
    dire1 = 0
    for n in range(0, 5, 1):
        if radiant1 == dire1 or radiant1 < dire1:
            radiant1 += list_mmr[4 - n]
            dire1 += list_mmr[5 + n]
            team_order1[4 - n] = "Team 1"
            team_order1[5 + n] = "Team 2"
        else:
            dire1 += list_mmr[4 - n]
            radiant1 += list_mmr[5 + n]
            team_order1[4 - n] = "Team 2"
            team_order1[5 + n] = "Team 1"
    team_order2 = ['', '', '', '', '', '', '', '', '', '']
    radiant2 = 0
    dire2 = 0
    for n in range(0, 5, 1):
        if radiant2 == dire2 or radiant2 < dire2:
            radiant2 += list_mmr[n]
            dire2 += list_mmr[-(n + 1)]
            team_order2[n] = "Team 1"
            team_order2[-(n + 1)] = "Team 2"
        else:
            dire2 += list_mmr[n]
            radiant2 += list_mmr[-(n + 1)]
            team_order2[n] = "Team 2"
            team_order2[-(n + 1)] = "Team 1"
    average1 = (radiant1 / 5) - (dire1 / 5)
    average2 = (radiant2 / 5) - (dire2 / 5)
    if abs(average1) < 100 and abs(average2) < 100:
        coin_flip = random.randint(1, 2)
        if coin_flip == 1:
            return team_order1
        else:
            return team_order2
    elif abs(average1) < abs(average2):
        return team_order1
    else:
        return team_order2
