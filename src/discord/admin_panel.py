import discord
from enum import Enum
import client_db_interface
import embed_superclass


class AdminEmbed(embed_superclass.ChannelEmbeds):
    def __init__(self, server, admin_ui, chat_channel, embed_channel):
        super().__init__(server, chat_channel, embed_channel)
        self.unverified_list = client_db_interface.get_unverified_users(self.server)
        self.admin_ui = admin_ui
        self.button_state = AdminButtonState.UNVERIFIED

    async def send_embed(self):
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    async def update_message(self, interaction=None):
        if self.button_state == AdminButtonState.UNVERIFIED:
            self.unverified_list = client_db_interface.get_unverified_users(self.server)
            if self.unverified_list:
                user = self.unverified_list[0]
                self.admin_ui.user_embed(user, self.server)
            else:
                self.admin_ui.empty_embed()
        elif self.button_state == AdminButtonState.STATS:
            self.admin_ui.stats_embed(self.server)
        elif self.button_state == AdminButtonState.BANNED:
            self.admin_ui.banned_embed(self.server)
        if interaction:
            self.admin_ui.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        self.update_buttons()
        await self.message.edit(embed=self.admin_ui, view=self)

    def update_buttons(self):
        if self.button_state == AdminButtonState.UNVERIFIED:
            self.refresh_embed.label = "Refresh"
            self.refresh_embed.emoji = "♻"
            self.change_embed.label = "View Server Details"
            if not self.unverified_list:
                self.verify_user.disabled = True
                self.reject_user.disabled = True
            else:
                self.verify_user.disabled = False
                self.reject_user.disabled = False
        else:
            self.verify_user.disabled = True
            self.reject_user.disabled = True
            self.change_embed.label = "View Unverified Users"
        if self.button_state == AdminButtonState.STATS:
            self.refresh_embed.label = "View Ban List"
            self.refresh_embed.emoji = "🔨"
        elif self.button_state == AdminButtonState.BANNED:
            self.refresh_embed.label = "Server Stats"
            self.refresh_embed.emoji = "📋"

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
        if self.button_state == AdminButtonState.STATS:
            self.button_state = AdminButtonState.BANNED
        elif self.button_state == AdminButtonState.BANNED:
            self.button_state = AdminButtonState.STATS
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
        if self.button_state == AdminButtonState.UNVERIFIED:
            self.button_state = AdminButtonState.STATS
        else:
            self.button_state = AdminButtonState.UNVERIFIED
        await self.update_message(interaction)
        await interaction.response.defer()


class AdminButtonState(Enum):
    UNVERIFIED: str = "Unverified"
    STATS: str = "Stats"
    BANNED: str = "Banned"
    ADMIN: str = "Admin"

