import math
from typing_extensions import Self

import discord
import client_db_interface as get_data
from src.discord import client_db_interface


def badge_rank(mmr):
    match mmr:
        case _ if mmr >= 5620:
            return "Immortal"
        case _ if mmr >= 4620:
            badge = "Divine "
            mmr = mmr - 4620
            return badge + str(math.ceil(mmr / 200))
        case _ if mmr >= 3850:
            badge = "Ancient "
            mmr = mmr - 3850
        case _ if mmr >= 3080:
            badge = "Legend "
            mmr = mmr - 3080
        case _ if mmr >= 2310:
            badge = "Archon "
            mmr = mmr - 2310
        case _ if mmr >= 1540:
            badge = "Crusader "
            mmr = mmr - 1540
        case _ if mmr >= 770:
            badge = "Guardian "
            mmr = mmr - 770
        case _:
            badge = "Herald "
    return badge + str(math.ceil(mmr / 154))


def user_exists(server, user_name):
    try:
        user_account = next((x for x in server.members if user_name.lower() in x.display_name.lower()))
        user_in_database = get_data.check_discord_exists(user_account.id)
    except StopIteration:
        user_account = None
        user_in_database = False
    return user_in_database, user_account


def check_role_priority(user):
    core_roles = [user[0], user[1], user[2]]
    supp_roles = [user[3], user[4]]
    if 5 in core_roles and 5 not in supp_roles:
        role_pref = "Core"
    elif 5 in supp_roles and 5 not in core_roles:
        role_pref = "Support"
    else:
        core_avg = sum(core_roles) / 3
        supp_avg = sum(supp_roles) / 2
        role_balance = core_avg - supp_avg
        match role_balance:
            case _ if role_balance < 0:
                role_pref = "Support"
            case _ if role_balance > 1:
                role_pref = "Core"
            case _:
                role_pref = "Balanced"
    return role_pref


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
