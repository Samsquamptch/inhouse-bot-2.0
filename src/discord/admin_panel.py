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

    def registered_embed(self, data_list, interaction):
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
        all_embed.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        return all_embed

    def empty_embed(self, interaction):
        empty_embed = discord.Embed(title="No unverified users", description=f'There\'s nobody to verify!',
                                    color=0xFF0000)
        empty_embed.set_image(
            url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')
        if interaction:
            empty_embed.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        return empty_embed

    async def update_message(self, interaction=None):
        self.update_buttons()
        if self.view_status:
            self.unverified_list = client_db_interface.get_unverified_users(self.server)
            if self.unverified_list:
                user = self.unverified_list[0]
                user_data = client_db_interface.view_user_data(user.id)
                update_embed = check_user.user_embed(user_data, user, self.server)
                if interaction:
                    update_embed.set_footer(
                        text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
                await self.message.edit(embed=update_embed, view=self)
            else:
                await self.message.edit(embed=self.empty_embed(interaction), view=self)

    def update_buttons(self):
        print(self.view_status)
        if not self.unverified_list:
            self.verify_user.disabled = True
            self.reject_user.disabled = True
        else:
            self.verify_user.disabled = False
            self.reject_user.disabled = False
        if self.view_status:
            self.refresh_embed.disabled = False
            self.change_embed.label = "View Registered Users"
        else:
            self.refresh_embed.disabled = True
            self.change_embed.label = "View Unverified Users"

    @discord.ui.button(label="Verify User", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def verify_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        client_db_interface.enable_verification(self.unverified_list[0], interaction.guild)
        await self.chat_channel.send(f'User <@{self.unverified_list[0].id}> has been verified for the inhouse')
        del self.unverified_list[0]
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
        del self.unverified_list[0]
        await self.update_message(interaction)
        await interaction.response.defer()

    @discord.ui.button(label="View Registered Users", emoji="📋",
                       style=discord.ButtonStyle.grey)
    async def change_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        # TODO: Rework this to show info on number of registered users, banned users, etc.
        if self.view_status:
            self.view_status = False
            await self.update_message(interaction)
            await interaction.response.defer()
        else:
            self.view_status = True
            await self.update_message(interaction)
            await interaction.response.defer()
