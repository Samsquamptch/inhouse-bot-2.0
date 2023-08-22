import pandas as pd

def update_user_data(discord_id, columns, new_data):
    user_data = pd.read_csv("../../data/users.csv")
    updated_user = user_data.query(f'disc=={discord_id}')
    user_data.iloc[updated_user.index, columns] = new_data
    user_data.to_csv("../../data/users.csv", index=False)

def check_for_value(discord_id):
    user_data = pd.read_csv("../../data/users.csv")
    if discord_id not in user_data.values:
        variable = False
        return variable
    else:
        variable = True
        return variable
