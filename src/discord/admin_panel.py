import discord
import check_user
import client_db_interface
import embed_superclass


class AdminEmbed(embed_superclass.EmbedSuperclass):
    def __init__(self, chat_channel, embed_channel, server):
        super().__init__(chat_channel, embed_channel, server)
        self.server = server
        self.unverified_list = client_db_interface.get_unverified_users(self.server)
        self.view_status = True

    async def send_embed(self):
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    def registered_embed(self, data_list):
        all_embed = discord.Embed(title='Registered users', description=f'Showing all registered users',
                                  color=0x00ff00)
        icon_url = self.server.icon.url
        all_embed.set_thumbnail(url=f'{icon_url}')
        for user in data_list:
            user_data = client_db_interface.view_user_data(user.id)
            all_embed.add_field(name=user.display_name,
                                value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]})'
                                      f'| Roles: {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]} {user_data[7]}',
                                inline=False)
        return all_embed

    def empty_embed(self):
        empty_embed = discord.Embed(title="No unverified users", description=f'There\'s nobody to verify!',
                                    color=0xFF0000)
        empty_embed.set_image(
            url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')
        return empty_embed

    def stats_embed(self):
        test_embed = discord.Embed(title="Test", description=f'Oh yeah I\'m TESTING',
                                    color=0xFF0000)
        test_embed.set_image(
            url=f'https://i.ytimg.com/vi/1LsIQr_4iSY/maxresdefault.jpg')
        return test_embed

    async def update_message(self, interaction=None):
        self.update_buttons()
        if self.view_status:
            self.unverified_list = client_db_interface.get_unverified_users(self.server)
            if self.unverified_list:
                user = self.unverified_list[0]
                user_data = client_db_interface.view_user_data(user.id)
                panel_embed = check_user.user_embed(user_data, user, self.server)
            else:
                panel_embed = self.empty_embed()
        else:
            panel_embed = self.stats_embed()
        panel_embed.set_thumbnail(url=f'{self.server.icon.url}')
        if interaction:
            panel_embed.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        await self.message.edit(embed=panel_embed, view=self)

    def update_buttons(self):
        print(self.view_status)
        if self.view_status:
            self.refresh_embed.disabled = False
            self.change_embed.label = "View Server Details"
        else:
            self.refresh_embed.disabled = True
            self.change_embed.label = "View Unverified Users"
        if not self.unverified_list:
            self.verify_user.disabled = True
            self.reject_user.disabled = True
        else:
            self.verify_user.disabled = False
            self.reject_user.disabled = False


    @discord.ui.button(label="Verify User", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def verify_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        client_db_interface.enable_verification(self.unverified_list[0], interaction.guild)
        await self.chat_channel.send(f'User <@{self.unverified_list[0].id}> has been verified for the inhouse')
        await self.update_message(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="Refresh", emoji="♻",
                       style=discord.ButtonStyle.blurple)
    async def refresh_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_message(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="Reject User", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def reject_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        client_db_interface.disable_verification(self.unverified_list[0], interaction.guild, False)
        await self.chat_channel.send(f'User <@{self.unverified_list[0].id}> has been rejected from the inhouse.'
                                     f' An admin will inform you why you were rejected.')
        await self.update_message(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="View Registered Users", emoji="📋",
                       style=discord.ButtonStyle.grey)
    async def change_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Rework this to show info on number of registered users, banned users, etc.
        if self.view_status:
            self.view_status = False
        else:
            self.view_status = True
        await self.update_message(interaction)
        await interaction.response.defer()
