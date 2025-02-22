import math
import discord
import client_db_interface as get_data
from src.discord import client_db_interface


class UserEmbed(discord.Embed):
    def __init__(self):
        super().__init__()

    def user_embed(self, user_account, server):
        data_list = client_db_interface.get_user_stats(user_account.id, server)
        role_champion = get_data.load_champion_role(server)
        user_verified, user_banned = get_data.get_user_status(user_account, server)
        if user_banned:
            user_status = "User is currently banned 😢"
            user_clr = 0x000000
        elif role_champion in user_account.roles:
            user_status = "User is a champion! 😎"
            user_clr = 0xFFD700
        elif user_verified:
            user_status = "User is verified"
            user_clr = 0x00ff00
        else:
            user_status = "User is not verified"
            user_clr = 0xFF0000
        badge = badge_rank(data_list[2])
        self.title = f'{user_account.display_name}'
        self.description = f'{user_status}'
        self.color = user_clr
        if user_account.avatar:
            self.set_thumbnail(url=f'{user_account.avatar}')
        self.add_field(name='Dotabuff',
                       value=f'[{data_list[1]}](https://www.dotabuff.com/players/{data_list[1]})'
                             f'\u0020\u0020\u0020\u0020', inline=True)
        self.add_field(name='MMR', value=f'{data_list[2]} \u0020\u0020\u0020\u0020',
                       inline=True)
        self.add_field(name='Rank', value=f'{badge} \u0020\u0020', inline=True)
        self.add_field(name='Played', value=data_list[8] + data_list[9], inline=True)
        self.add_field(name='Wins', value=data_list[8], inline=True)
        self.add_field(name='Losses', value=data_list[9], inline=True)
        self.add_field(name='Role Preferences', value='', inline=False)
        role_list = ["Carry", "Midlane", "Offlane", "Soft Support", "Hard Support"]
        for i in range(3, 8):
            self.add_field(name=f'{role_list[i - 3]} ', value=f'{data_list[i]}', inline=False)
        self.set_image(url=None)


class StandInEmbed(discord.Embed):
    def __init__(self):
        super().__init__()

    def show_stand_ins(self, mmr_cap, server):
        self.title = "Stand-in List"
        self.set_thumbnail(url=server.icon.url)
        stand_in_list = client_db_interface.load_users_below_mmr(mmr_cap, server)
        match len(stand_in_list):
            case _ if len(stand_in_list) > 8:
                self.color = 0x00ff00
            case _ if len(stand_in_list) > 6:
                self.color = 0x80ff00
            case _ if len(stand_in_list) > 4:
                self.color = 0xffff00
            case _ if len(stand_in_list) > 2:
                self.color = 0xff8000
            case _ if len(stand_in_list) > 0:
                self.color = 0xFF0000
            case _:
                self.description = "There's nobody who meets your requirements on this server 💀"
                self.color = 0x000000
                return
        self.description = "Potential Stand-ins to use"
        for user_data in stand_in_list:
            user_account = discord.utils.get(server.members, id=user_data[0])
            self.add_field(name=user_account.name, value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) '
                                                         f'| Roles: {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]} {user_data[7]}',
                           inline=False)


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
    core_roles = [user[3], user[4], user[5]]
    supp_roles = [user[6], user[7]]
    if 5 in core_roles and 5 not in supp_roles:
        role_pref = "Core"
    elif 5 in supp_roles and 5 not in core_roles:
        role_pref = "Support"
    else:
        core_avg = (user[3] + user[4] + user[5]) / 3
        supp_avg = (user[6] + user[7]) / 2
        role_balance = core_avg - supp_avg
        match role_balance:
            case _ if role_balance < 0:
                role_pref = "Support"
            case _ if role_balance > 1:
                role_pref = "Core"
            case _:
                role_pref = "Balanced"
    return role_pref
