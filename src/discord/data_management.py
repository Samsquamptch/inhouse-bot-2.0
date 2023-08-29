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

# def delete_user_data(discord_id):
#     user_data = pd.read_csv("../../data/users.csv")
#     deleted_user = user_data.drop(f'disc=={discord_id}')
#     deleted_user.to_csv("../../data/users.csv", index=False)

def view_user_data(discord_id):
    user_data = pd.read_csv("../../data/users.csv")
    user_data_list = user_data.query(f'disc=={discord_id}').values.flatten().tolist()
    return user_data_list

def add_user_data(player):
    with open('../../data/users.csv', 'a', encoding='UTF8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(player)
