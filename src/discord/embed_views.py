import discord
from src.discord import client_db_interface, check_user


class UserEmbed(discord.Embed):
    def __init__(self):
        super().__init__()

    def user_embed(self, user_account, server):
        self.clear_fields()
        data_list = client_db_interface.get_user_stats(user_account.id, server)
        role_champion = client_db_interface.load_champion_role(server)
        user_verified, user_banned = client_db_interface.get_user_status(user_account, server)
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


class AdminEmbedView(UserEmbed):
    def __init__(self):
        super().__init__()

    def registered_embed(self, data_list):
        self.title = 'Registered users'
        self.description = f'Showing all registered users'
        self.color = 0x00ff00
        for user in data_list:
            user_data = client_db_interface.view_user_data(user.id)
            self.add_field(name=user.display_name,
                           value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]})'
                                 f'| Roles: {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]} {user_data[7]}',
                           inline=False)
        self.set_image(url=None)

    def empty_embed(self):
        self.title = "No unverified users"
        self.description = f'There\'s nobody to verify!'
        self.color = 0xFF0000
        self.set_image(
            url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')

    def stats_embed(self, server):
        user_count, verified_count, banned_count = client_db_interface.count_users(server)
        server_settings = client_db_interface.load_server_settings(server)
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

    def banned_embed(self, server):
        self.clear_fields()
        ban_list = client_db_interface.load_banned_users(server)
        self.title = "Ban List"
        self.description = "Showing currently banned users"
        if not ban_list:
            self.description = "There are no banned users. That's great news!"
        i = 0
        for banned in ban_list:
            banned_user = discord.utils.get(server.members, id=banned[0])
            self.add_field(name=banned_user.display_name, value=f'Username: {banned_user.name} | '
                                                                f'[Dotabuff Link](https://www.dotabuff.com/players/{banned[1]})',
                           inline=False)
            i += 1
            if i >= 10:
                break
        self.color = 0x000000
        self.set_image(url=None)


class QueueEmbedView(discord.ui.View):
    def __init__(self):
        super().__init__()


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
