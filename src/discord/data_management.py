# For all functions relating to adding/removing/amending/viewing from users.csv

import pandas as pd
import csv


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

def queue_pop(queue_ids):
    user_data = pd.read_csv("../../data/userstest.csv")
    queue = user_data.query(f'disc in @queue_ids')
    queue = queue.sort_values('mmr', ascending=False)
    team_uno = ["Team 1","Team 2","Team 1","Team 2","Team 1","Team 2","Team 1","Team 2","Team 1","Team 2"]
    team_dos = ["Team 1","Team 2","Team 2","Team 1","Team 1","Team 2","Team 2","Team 1","Team 1","Team 2"]
    queue["teamuno"] = team_uno
    queue["teamdos"] = team_dos
    delta1 = queue.loc[queue['teamuno'] == "Team 1", 'mmr'].mean() - queue.loc[queue['teamuno'] == "Team 2", 'mmr'].mean()
    delta2 =queue.loc[queue['teamdos'] == "Team 1", 'mmr'].mean() - queue.loc[queue['teamdos'] == "Team 2", 'mmr'].mean()
    print(delta1)
    print(delta2)
    if delta1 <= delta2:
        queue.drop(columns=team_dos)
        queue.rename(columns={"team_uno":"team"})
        queue.to_csv("../../data/match.csv", index=False)
        team1 = queue.loc[queue['teamuno'] == "Team 1", 'disc'].flatten.tolist()
        team2 = queue.loc[queue['team'] == "Team 2", 'disc'].flatten.tolist()
        return team1, team2
    else:
        queue.drop(columns=team_uno)
        queue.rename(columns={"team_dos": "team"})
        queue.to_csv("../../data/match.csv", index=False)
        team1 = queue.loc[queue['teamdos'] == "Team 1", 'disc'].flatten.tolist()
        team2 = queue.loc[queue['team'] == "Team 2", 'disc'].flatten.tolist()
        return team1, team2
