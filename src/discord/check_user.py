import discord
import data_management

register_list = []


def user_embed(data_list, player_data, server):
    roles_id = data_management.load_config_data(server, 'ROLES')
    role_verified = discord.utils.get(server.roles, id=roles_id['verified_role'])
    role_banned = discord.utils.get(server.roles, id=roles_id['banned_role'])
    role_champion = discord.utils.get(server.roles, id=roles_id['champions_role'])
    if role_banned in player_data.roles:
        user_status = "User is currently banned 😢"
        user_clr = 0x000000
    elif role_champion in player_data.roles:
        user_status = "User is a champion!"
        user_clr = 0xFFD700
    elif role_verified in player_data.roles:
        user_status = "User is verified"
        user_clr = 0x00ff00
    else:
        user_status = "User is not verified"
        user_clr = 0xFF0000
    # Due to how the role balancer calculations work, number weighting is saved the opposite to how users are used to
    # (which is higher number = more pref and lower number = less pref). This swap shows what users expect to see,
    # instead of what is actually happening behind the scenes (low num = more pref and high num = less pref)
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
    badge = badge_rank(data_list[2])
    view_user_embed = discord.Embed(title=f'{player_data.display_name}', description=f'{user_status}',
                                    color=user_clr)
    if player_data.avatar:
        view_user_embed.set_thumbnail(url=f'{player_data.avatar}')
    view_user_embed.add_field(name='Dotabuff',
                              value=f'[{data_list[1]}](https://www.dotabuff.com/players/{data_list[1]})'
                                    f'\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC', inline=True)
    view_user_embed.add_field(name='MMR', value=f'{data_list[2]} \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC',
                              inline=True)
    view_user_embed.add_field(name='Rank', value=f'{badge} \u1CBC\u1CBC\u1CBC\u1CBC', inline=True)
    # view_user_embed.add_field(name='Matches', value=f'0', inline=True)
    # view_user_embed.add_field(name='Wins', value=f'0', inline=True)
    # view_user_embed.add_field(name='Losses', value=f'0', inline=True)
    view_user_embed.add_field(name='Role Preferences', value='', inline=False)
    view_user_embed.add_field(name=f'Carry: \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC{data_list[3]}', value=f'',
                              inline=False)
    view_user_embed.add_field(name=f'Midlane: \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC{data_list[4]}', value=f'',
                              inline=False)
    view_user_embed.add_field(name=f'Offlane:\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC{data_list[5]}', value=f'',
                              inline=False)
    view_user_embed.add_field(name=f'Soft Support:\u1CBC\u1CBC {data_list[6]}', value=f'', inline=False)
    view_user_embed.add_field(name=f'Hard Support: \u1CBC {data_list[7]}', value=f'', inline=False)
    return view_user_embed


def badge_rank(mmr):
    match mmr:
        case _ if mmr >= 5620:
            return "Immortal"
        case _ if mmr >= 4620:
            match mmr:
                case _ if mmr >= 5420:
                    return "Divine 5"
                case _ if mmr >= 5220:
                    return "Divine 4"
                case _ if mmr >= 5020:
                    return "Divine 3"
                case _ if mmr >= 4820:
                    return "Divine 2"
                case _:
                    return "Divine 1"
        case _ if mmr >= 3850:
            match mmr:
                case _ if mmr >= 4466:
                    return "Ancient 5"
                case _ if mmr >= 4312:
                    return "Ancient 4"
                case _ if mmr >= 4158:
                    return "Ancient 3"
                case _ if mmr >= 4004:
                    return "Ancient 2"
                case _:
                    return "Ancient 1"
        case _ if mmr >= 3080:
            match mmr:
                case _ if mmr >= 3696:
                    return "Legend 5"
                case _ if mmr >= 3542:
                    return "Legend 4"
                case _ if mmr >= 3388:
                    return "Legend 3"
                case _ if mmr >= 3234:
                    return "Legend 2"
                case _:
                    return "Legend 1"
        case _ if mmr >= 2310:
            match mmr:
                case _ if mmr >= 2926:
                    return "Archon 5"
                case _ if mmr >= 2772:
                    return "Archon 4"
                case _ if mmr >= 2618:
                    return "Archon 3"
                case _ if mmr >= 2464:
                    return "Archon 2"
                case _:
                    return "Archon 1"
        case _ if mmr >= 1540:
            match mmr:
                case _ if mmr >= 2156:
                    return "Crusader 5"
                case _ if mmr >= 2002:
                    return "Crusader 4"
                case _ if mmr >= 1848:
                    return "Crusader 3"
                case _ if mmr >= 1694:
                    return "Crusader 2"
                case _:
                    return "Crusader 1"
        case _ if mmr >= 770:
            match mmr:
                case _ if mmr >= 1386:
                    return "Guardian 5"
                case _ if mmr >= 1232:
                    return "Guardian 4"
                case _ if mmr >= 1078:
                    return "Guardian 3"
                case _ if mmr >= 924:
                    return "Guardian 2"
                case _:
                    return "Guardian 1"
        case _:
            match mmr:
                case _ if mmr >= 616:
                    return "Herald 5"
                case _ if mmr >= 462:
                    return "Herald 4"
                case _ if mmr >= 308:
                    return "Herald 3"
                case _ if mmr >= 154:
                    return "Herald 2"
                case _:
                    return "Herald 1"


def user_exists(server, user_name):
    try:
        user_account = next((x for x in server.members if user_name.lower() in x.display_name.lower()))
        user_in_database = data_management.check_for_value("disc", user_account.id, server)
    except StopIteration:
        user_in_database = False
        user_account = None
    return user_in_database, user_account


def check_role_priority(user):
    core_roles = [user[3], user[4], user[5]]
    supp_roles = [user[6], user[7]]
    if 1 in core_roles and 1 not in supp_roles:
        role_pref = "Core"
    elif 1 in supp_roles and 1 not in core_roles:
        role_pref = "Support"
    else:
        core_avg = (user[3] + user[4] + user[5]) / 3
        supp_avg = (user[6] + user[7]) / 2
        role_balance = core_avg - supp_avg
        match role_balance:
            case _ if role_balance > 1:
                role_pref = "Support"
            case _ if role_balance < 0:
                role_pref = "Core"
            case _:
                role_pref = "Balanced"
    return role_pref


def user_list(list_condition, user=None):
    global register_list
    match list_condition:
        case "Add":
            register_list.append(user)
        case "Remove":
            register_list.remove(user)
        case _:
            pass
    return register_list
