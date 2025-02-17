import discord
import check_user
import client_db_interface
import embed_superclass
from embed_views import AdminEmbedView


class AdminEmbed(embed_superclass.EmbedSuperclass):
    def __init__(self, chat_channel, embed_channel, server):
        super().__init__(chat_channel, embed_channel, server)
        self.server = server
        self.unverified_list = client_db_interface.get_unverified_users(self.server)
        self.view_status = True

    async def send_embed(self):
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    async def update_message(self, interaction=None):
        admin_embed = AdminEmbedView()
        self.update_buttons()
        admin_embed.set_thumbnail(url=f'{self.server.icon.url}')
        if self.view_status:
            self.unverified_list = client_db_interface.get_unverified_users(self.server)
            if self.unverified_list:
                user = self.unverified_list[0]
                user_data = client_db_interface.view_user_data(user.id)
                admin_embed.user_embed(user_data, user, self.server)
            else:
                admin_embed.empty_embed()
        else:
            admin_embed.stats_embed()
        if interaction:
            admin_embed.set_footer(text=f'last accessed by {interaction.user.display_name} at {interaction.created_at}')
        await self.message.edit(embed=admin_embed, view=self)

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
