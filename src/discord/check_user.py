import math
import discord
import client_db_interface as get_data


def user_embed(data_list, player_data, server):
    role_champion = get_data.load_champion_role(server)
    user_verified, user_banned = get_data.get_user_status(player_data, server)
    if user_banned:
        user_status = "User is currently banned 😢"
        user_clr = 0x000000
    elif role_champion in player_data.roles:
        user_status = "User is a champion! 😎"
        user_clr = 0xFFD700
    elif user_verified:
        user_status = "User is verified"
        user_clr = 0x00ff00
    else:
        user_status = "User is not verified"
        user_clr = 0xFF0000
    badge = badge_rank(data_list[2])
    view_user_embed = discord.Embed(title=f'{player_data.display_name}', description=f'{user_status}',
                                    color=user_clr)
    if player_data.avatar:
        view_user_embed.set_thumbnail(url=f'{player_data.avatar}')
    view_user_embed.add_field(name='Dotabuff',
                              value=f'[{data_list[1]}](https://www.dotabuff.com/players/{data_list[1]})'
                                    f'\u0020\u0020\u0020\u0020', inline=True)
    view_user_embed.add_field(name='MMR', value=f'{data_list[2]} \u0020\u0020\u0020\u0020',
                              inline=True)
    view_user_embed.add_field(name='Rank', value=f'{badge} \u0020\u0020', inline=True)
    view_user_embed.add_field(name='Role Preferences', value='', inline=False)
    role_list = ["Carry", "Midlane", "Offlane", "Soft Support", "Hard Support"]
    for i in range(3, 8):
        view_user_embed.add_field(name=f'{role_list[i - 3]} ', value=f'{data_list[i]}', inline=False)
    return view_user_embed


def badge_rank(mmr):
    match mmr:
        case _ if mmr >= 5620:
            return "Immortal"
        case _ if mmr >= 4620:
            badge = "Divine"
            mmr = mmr - 4620
            return badge + str(math.ceil(mmr / 200))
        case _ if mmr >= 3850:
            badge = "Ancient "
            mmr = mmr - 3850
            return badge + str(math.ceil(mmr / 154))
        case _ if mmr >= 3080:
            badge = "Legend "
            mmr = mmr - 3080
            return badge + str(math.ceil(mmr / 154))
        case _ if mmr >= 2310:
            badge = "Archon "
            mmr = mmr - 2310
            return badge + str(math.ceil(mmr / 154))
        case _ if mmr >= 1540:
            badge = "Crusader "
            mmr = mmr - 1540
            return badge + str(math.ceil(mmr / 154))
        case _ if mmr >= 770:
            badge = "Guardian "
            mmr = mmr - 770
            return badge + str(math.ceil(mmr / 154))
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
