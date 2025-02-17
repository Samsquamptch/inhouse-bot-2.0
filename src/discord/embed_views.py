import discord

from src.discord import client_db_interface
from check_user import UserEmbed


class AdminEmbedView(UserEmbed):
    def __init__(self):
        super().__init__()

    def registered_embed(self, data_list):
        self.title='Registered users'
        self.description=f'Showing all registered users'
        self.color=0x00ff00
        for user in data_list:
            user_data = client_db_interface.view_user_data(user.id)
            self.add_field(name=user.display_name, value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]})'
                                      f'| Roles: {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]} {user_data[7]}', inline=False)
        self.set_image(url=None)

    def empty_embed(self):
        self.title="No unverified users"
        self.description=f'There\'s nobody to verify!'
        self.color=0xFF0000
        self.set_image(url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')


    def stats_embed(self):
        self.title = "Test"
        self.description = f'Oh yeah I\'m TESTING'
        self.color=0xFF0000
        self.set_image(url=f'https://i.ytimg.com/vi/1LsIQr_4iSY/maxresdefault.jpg')
