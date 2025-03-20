import discord
from enum import Enum
import client_db_interface
import embed_superclass


class AdminEmbed(embed_superclass.ChannelEmbeds):
    def __init__(self, server, admin_ui, chat_channel, embed_channel, approval_list):
        super().__init__(server, chat_channel, embed_channel)
        self.approval_list = approval_list
        self.admin_ui = admin_ui
        self.button_state = AdminButtonState.UNVERIFIED
        self.current_user = None

    async def send_embed(self):
        self.approval_list.start_list()
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    async def update_message(self, interaction=None):
        if self.button_state == AdminButtonState.UNVERIFIED:
            if self.approval_list.list_contains_users():
                self.current_user = self.approval_list.get_first_user()
                self.admin_ui.user_embed(self.current_user, True)
            else:
                self.admin_ui.empty_embed()
        elif self.button_state == AdminButtonState.STATS:
            self.admin_ui.stats_embed()
        elif self.button_state == AdminButtonState.BANNED:
            self.admin_ui.banned_embed()
        if interaction:
            self.admin_ui.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        self.update_buttons()
        await self.message.edit(embed=self.admin_ui, view=self)

    def update_buttons(self):
        if self.button_state == AdminButtonState.UNVERIFIED:
            self.refresh_embed.label = "Refresh"
            self.refresh_embed.emoji = "♻"
            self.change_embed.label = "View Server Details"
            if self.approval_list.list_contains_users():
                self.approve_user.disabled = False
                self.reject_user.disabled = False
            else:
                self.approve_user.disabled = True
                self.reject_user.disabled = True
        else:
            self.approve_user.disabled = True
            self.reject_user.disabled = True
            self.change_embed.label = "Manage Users"
        if self.button_state == AdminButtonState.STATS:
            self.refresh_embed.label = "View Ban List"
            self.refresh_embed.emoji = "🔨"
        elif self.button_state == AdminButtonState.BANNED:
            self.refresh_embed.label = "Server Stats"
            self.refresh_embed.emoji = "📋"

    def approval_action(self):
        if self.current_user.is_registering:
            client_db_interface.enable_verification(self.current_user, self.server)
            message = f'User <@{self.current_user.id}> has been verified for the inhouse'
        else:
            client_db_interface.update_user_data(self.current_user.id, "MMR", self.current_user.mmr)
            message = f'User <@{self.current_user.id}> has had their mmr updated to {self.current_user.mmr}'
        self.approval_list.remove_first_user()
        return message

    def rejection_action(self):
        if self.current_user.is_registering:
            client_db_interface.disable_verification(self.current_user, self.server)
            message = f'User <@{self.current_user.id}> has been rejected from the inhouse. An admin will inform you why.'
        else:
            message = f'User <@{self.current_user.id}> has had their mmr update request denied.'
        self.approval_list.remove_first_user()
        return message

    @discord.ui.button(label="Verify User", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def approve_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        approval_message = self.approval_action()
        await self.chat_channel.send(approval_message)
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
        rejection_message = self.rejection_action()
        await self.chat_channel.send(rejection_message)
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
