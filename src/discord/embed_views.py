import discord

from src.discord import client_db_interface
from check_user import UserEmbed


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

    def banned_embed(self, server):
        ban_list = client_db_interface.load_banned_users(server)
        self.title = "Ban List"
        self.description = "Showing currently banned users"
        if not ban_list:
            self.description = "There are no banned users. That's great news!"
        i = 0
        for banned in ban_list:
            banned_user = discord.utils.get(server.members, id=banned[0])
            self.add_field(name=banned_user.display_name, value=f'Username: {banned_user.name} | '
                            f'[Dotabuff Link](https://www.dotabuff.com/players/{banned[1]})', inline=False)
            i+=1
            if i >= 10:
                break
        self.color = 0x000000
