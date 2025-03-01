from abc import ABC, abstractmethod
from datetime import datetime
from zoneinfo import ZoneInfo

import discord
from src.discord import client_db_interface, check_user, team_balancer


class UserEmbed(discord.Embed):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def user_embed(self, user_account):
        self.clear_fields()
        data_list = client_db_interface.get_user_stats(user_account, self.server)
        role_champion = client_db_interface.load_champion_role(self.server)
        user_verified, user_banned = client_db_interface.get_user_status(user_account, self.server)
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
        badge = check_user.badge_rank(data_list[2])
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


class EmptyEmbed(ABC):

    @abstractmethod
    def empty_embed(self):
        pass


class AdminEmbedView(UserEmbed, EmptyEmbed):
    def __init__(self, server):
        UserEmbed.__init__(self, server)
        EmptyEmbed.__init__(self)
        self.server = server

    def empty_embed(self):
        self.set_thumbnail(url=self.server.icon.url)
        self.title = "No unverified users"
        self.description = f'There\'s nobody to verify!'
        self.color = 0xFF0000
        self.set_image(
            url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')

    def stats_embed(self):
        user_count, verified_count, banned_count = client_db_interface.count_users(self.server)
        server_settings = client_db_interface.load_server_settings(self.server)
        self.set_thumbnail(url=self.server.icon.url)
        self.title = "Server Details"
        self.description = f'Server Information'
        self.add_field(name='Number of Registered Users', value=user_count, inline=False)
        self.add_field(name='Number of Verified Users', value=verified_count, inline=False)
        self.add_field(name='Number of Banned Users', value=banned_count, inline=False)
        self.add_field(name='Afk Timer', value=server_settings[0], inline=False)
        self.add_field(name='MMR Floor', value=server_settings[1], inline=False)
        self.add_field(name='MMR Ceiling', value=server_settings[2], inline=False)
        self.add_field(name='Tryhard Mode', value='Disabled', inline=False)
        self.add_field(name='Global Queue', value='Disabled', inline=False)
        self.add_field(name='Global Queue Visibility', value='Private', inline=False)
        self.color = 0xFFD700
        self.set_image(url=None)

    def banned_embed(self):
        self.clear_fields()
        self.set_thumbnail(url=self.server.icon.url)
        ban_list = client_db_interface.load_banned_users(self.server)
        self.title = "Ban List"
        self.description = "Showing currently banned users"
        if not ban_list:
            self.description = "There are no banned users. That's great news!"
        i = 0
        for banned in ban_list:
            banned_user = discord.utils.get(self.server.members, id=banned[0])
            self.add_field(name=banned_user.display_name, value=f'Username: {banned_user.name} | '
                                                                f'[Dotabuff Link](https://www.dotabuff.com/players/{banned[1]})',
                           inline=False)
            i += 1
            if i >= 10:
                break
        self.color = 0x000000
        self.set_image(url=None)


class QueueEmbedView(discord.Embed, EmptyEmbed):
    def __init__(self, server):
        super().__init__()
        self.server = server
        self.set_thumbnail(url=self.server.icon.url)
        self.role_champion = client_db_interface.load_champion_role(server)

    def set_title(self, queue_name):
        self.title = f"{queue_name} QUEUE"

    def empty_embed(self):
        self.clear_fields()
        self.color = 0xFF0000
        self.description = "The queue is currently empty. You can change this!"
        self.add_field(name=f'No one is in the queue', value='', inline=False)
        update_time = datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
        self.set_footer(text=f'Queue updated at: {update_time}')

    def partial_queue(self, queue_list):
        self.clear_fields()
        if any(x for x in queue_list if x.is_champion is True):
            self.description = f"A champion is in the queue!"
            self.color = 0xFFD70
        else:
            self.description = f"Queue is live, come join!"
            self.color = 0x00ff00
        queue_length = len(queue_list)
        if queue_length == 1:
            self.add_field(name=f'1 player in queue', value='', inline=False)
        else:
            self.add_field(name=f'{queue_length} players in queue', value='', inline=False)
        mmr_total = 0
        for user in queue_list:
            mmr_total = mmr_total + user.mmr
            role_preference = check_user.check_role_priority(user)
            self.add_field(name=user.name,
                           value=f'MMR: {user.mmr} | [Dotabuff](https://www.dotabuff.com/players/{user.steam}) | Preference: {role_preference}',
                           inline=False)
        update_time = datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
        average_mmr = int(mmr_total / queue_length)
        self.set_footer(text=f'Queue updated at: {update_time} | Average MMR: {average_mmr}')

    def full_queue(self, queue_list):
        self.clear_fields()
        # queue_ids = [user.id for user in queue_list]
        queue_roles = ["Carry", "Midlane", "Offlane", "Soft Supp", "Hard Supp"]
        queue_teams = team_balancer.assign_teams(queue_list[:10])
        self.description = f'Queue is full, please join the lobby!'
        self.color = 0x00ff00
        self.add_field(name='Roles', value='', inline=True)
        self.add_field(name='Radiant', value='', inline=True)
        self.add_field(name='Dire', value='', inline=True)
        radiant_team = queue_teams[0]
        dire_team = queue_teams[1]
        x = 0
        mmr_total_radiant = 0
        mmr_total_dire = 0
        while x < 5:
            user_acc_radiant = discord.utils.get(self.server.members, id=radiant_team[x])
            user_acc_dire = discord.utils.get(self.server.members, id=dire_team[x])
            user_radiant = client_db_interface.view_user_data(radiant_team[x])
            user_dire = client_db_interface.view_user_data(dire_team[x])
            mmr_total_radiant = mmr_total_radiant + user_radiant[2]
            mmr_total_dire = mmr_total_dire + user_dire[2]
            self.add_field(name=f'{queue_roles[x]}',
                                  value='\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC',
                                  inline=True)
            self.add_field(name=user_acc_radiant.display_name,
                                  value=f'MMR: {user_radiant[2]} \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC \n'
                                        f'[Dotabuff](https://www.dotabuff.com/players/{user_radiant[1]})',
                                  inline=True)
            self.add_field(name=user_acc_dire.display_name,
                                  value=f'MMR: {user_dire[2]} \n'
                                        f'[Dotabuff](https://www.dotabuff.com/players/{user_dire[1]})',
                                  inline=True)
            x += 1
        mmr_avg_radiant = mmr_total_radiant / 5
        mmr_avg_dire = mmr_total_dire / 5
        self.add_field(name=f'Average MMR', value='', inline=True)
        self.add_field(name=f'{mmr_avg_radiant}', value='', inline=True)
        self.add_field(name=f'{mmr_avg_dire}', value='', inline=True)
        update_time = datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
        self.add_field(name='Players',
                              value=f'<@{radiant_team[0]}> <@{radiant_team[1]}> <@{radiant_team[2]}> <@{radiant_team[3]}>'
                                    f'<@{radiant_team[4]}> <@{dire_team[0]}> <@{dire_team[1]}> <@{dire_team[2]}> <@{dire_team[3]}>'
                                    f'<@{dire_team[4]}>')
        self.set_footer(text=f'Teams created at: {update_time}')


class StandInEmbed(discord.Embed):
    def __init__(self, server):
        super().__init__()
        self.server = server

    def show_stand_ins(self, mmr_cap):
        self.title = "Stand-in List"
        self.set_thumbnail(url=self.server.icon.url)
        stand_in_list = client_db_interface.load_users_below_mmr(mmr_cap, self.server)
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
            user_account = discord.utils.get(self.server.members, id=user_data[0])
            self.add_field(name=user_account.name, value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) '
                                                         f'| Roles: {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]} {user_data[7]}',
                           inline=False)
