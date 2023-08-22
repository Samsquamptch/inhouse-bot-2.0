import pandas as pd

def update_roles(current_user, role_pref):
    user_data = pd.read_csv("../../data/users.csv")
    user_roles = user_data.query(f'disc=={current_user}')
    user_data.iloc[user_roles.index, [3, 4, 5, 6, 7]] = role_pref
    user_data.to_csv("../../data/users.csv", index=False)

def update_mmr(current_user, new_mmr):
    user_data = pd.read_csv("../../data/users.csv")
    value_to_change = user_data.query(f'disc=={current_user}')
    user_data.iloc[value_to_change.index, [2]] = new_mmr
    user_data.to_csv("../../data/users.csv", index=False)

def check_for_value(value_check):
    user_data = pd.read_csv("../../data/users.csv")
    if value_check not in user_data.values:
        variable = False
        return variable
    else:
        variable = True
        return variable
