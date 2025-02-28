import discord
import client_db_interface
import embed_superclass


class AdminEmbed(embed_superclass.ChannelEmbeds):
    def __init__(self, chat_channel, embed_channel, server, admin_embed):
        super().__init__(chat_channel, embed_channel, server)
        self.unverified_list = client_db_interface.get_unverified_users(self.server)
        self.view_status = True
        self.stats_status = True
        self.admin_embed = admin_embed

    async def send_embed(self):
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    async def update_message(self, interaction=None):
        self.update_buttons()
        self.admin_embed.clear_fields()
        self.admin_embed.set_thumbnail(url=f'{self.server.icon.url}')
        if self.view_status:
            self.unverified_list = client_db_interface.get_unverified_users(self.server)
            if self.unverified_list:
                user = self.unverified_list[0]
                self.admin_embed.user_embed(user, self.server)
            else:
                self.admin_embed.empty_embed()
        else:
            if self.stats_status:
                self.admin_embed.stats_embed(self.server)
            else:
                self.admin_embed.banned_embed(self.server)
        if interaction:
            self.admin_embed.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        await self.message.edit(embed=self.admin_embed, view=self)

    def update_buttons(self):
        if not self.view_status:
            self.verify_user.disabled = True
            self.reject_user.disabled = True
            self.change_embed.label = "View Unverified Users"
            if self.stats_status:
                self.refresh_embed.label= "View Ban List"
                self.refresh_embed.emoji= "🔨"
            else:
                self.refresh_embed.label = "Server Stats"
                self.refresh_embed.emoji = "📋"
        else:
            self.refresh_embed.label = "Refresh"
            self.refresh_embed.emoji = "♻"
            self.change_embed.label = "View Server Details"
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
        if not self.view_status:
            self.stats_status = not self.stats_status
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
        self.view_status = not self.view_status
        await self.update_message(interaction)
        await interaction.response.defer()
