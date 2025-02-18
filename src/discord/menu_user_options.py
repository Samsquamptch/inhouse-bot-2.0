import datetime
import discord
from src.discord import client_db_interface, check_user


class ViewUserModal(discord.ui.Modal, title='View User'):
    player_name = discord.ui.TextInput(label='User\'s global name or username')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user.user_exists(server, user_name)
        if check_if_exists[0]:
            user_data = client_db_interface.view_user_data(check_if_exists[1].id)
            await interaction.response.send_message(embed=check_user.user_embed(user_data, check_if_exists[1], server),
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(content=f'User {user_name} is not registered', ephemeral=True,
                                                    delete_after=10)


class NotifyUpdateModal(discord.ui.Modal, title='Update MMR'):
    def __init__(self, chat_channel, admin_role):
        super().__init__()
        self.chat_channel = chat_channel
        self.admin_role = admin_role

    set_mmr = discord.ui.TextInput(label='Request new MMR for user', max_length=5, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        new_mmr = str(self.set_mmr)
        server = interaction.guild
        if not client_db_interface.get_verified_status(interaction.user, interaction.guild):
            await interaction.response.send_message('You need to register before you can request an update!',
                                                    ephemeral=True,
                                                    delete_after=10)
            return
        user_data = client_db_interface.view_user_data(interaction.user.id)
        date_str = user_data[8]
        date_format = '%Y-%m-%d'
        date_obj = datetime.datetime.strptime(date_str, date_format)
        current_day = datetime.datetime.today()
        if current_day < date_obj + datetime.timedelta(days=14):
            await interaction.response.send_message('You can only request an MMR update every two weeks',
                                                    ephemeral=True,
                                                    delete_after=10)
            return
        try:
            int_new_mmr = int(new_mmr)
            client_db_interface.update_user_data(interaction.user.id, "mmr", int_new_mmr)
            client_db_interface.update_user_data(interaction.user.id, "LastUpdated",
                                             datetime.datetime.today().strftime('%Y-%m-%d'))
            await self.chat_channel.send(
                f'<@&{self.admin_role.id}> User <@{interaction.user.id}> wants their MMR set to {new_mmr}')
            await interaction.response.send_message("Your request has been sent to the notification channel.",
                                                    ephemeral=True, delete_after=10)
        except ValueError:
            await interaction.response.send_message('Please only input numbers for mmr',
                                                    ephemeral=True,
                                                    delete_after=10)


# Select menu for users (above inhouse queue)
class UserOptions(discord.ui.View):
    def __init__(self, chat_channel, server):
        super().__init__(timeout=None)
        self.last_value = None
        self.chat_channel = chat_channel
        self.admin_role = client_db_interface.load_admin_role(server)

    @discord.ui.select(placeholder="Select an action here", min_values=0, max_values=1, options=[
        discord.SelectOption(label="Search", emoji="🔎", description="Search for a specific user with their name"),
        discord.SelectOption(label="Update", emoji="❗", description="Notify admins of MMR change"),
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values:
            self.last_value = select.values[0]
        match self.last_value:
            case "Search":
                await interaction.response.send_modal(ViewUserModal())
            case "Update":
                await interaction.response.send_modal(NotifyUpdateModal(self.chat_channel, self.admin_role))
