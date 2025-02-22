import datetime
import discord
from src.discord import client_db_interface
from check_user import UserEmbed, StandInEmbed


class NotifyUpdateModal(discord.ui.Modal, title='Update MMR'):
    def __init__(self):
        super().__init__()
        self.new_mmr = None
        self.updated = None

    set_mmr = discord.ui.TextInput(label='Request new MMR for user', max_length=5, required=True)

    def check_updated_recently(self, user):
        user_data = client_db_interface.view_user_data(user.id)
        date_str = user_data[8]
        date_format = '%Y-%m-%d'
        date_obj = datetime.datetime.strptime(date_str, date_format)
        current_day = datetime.datetime.today()
        if current_day < date_obj + datetime.timedelta(days=7):
            return True
        else:
            return False

    def update_user_mmr(self, interaction):
        try:
            int_new_mmr = int(self.new_mmr)
        except ValueError:
            return False
        client_db_interface.update_user_data(interaction.user.id, "mmr", int_new_mmr)
        client_db_interface.update_user_data(interaction.user.id, "LastUpdated",
                                             datetime.datetime.today().strftime('%Y-%m-%d'))
        return True

    async def on_submit(self, interaction: discord.Interaction):
        self.new_mmr = str(self.set_mmr)
        if not client_db_interface.user_registered(interaction.user, interaction.guild):
            await interaction.response.send_message('You need to register first before updating your MMR!', ephemeral=True,
                                                    delete_after=10)
            return
        if self.check_updated_recently(interaction.user):
            await interaction.response.send_message('You can only request an MMR update every two weeks', ephemeral=True,
                                                    delete_after=10)
            return
        self.updated = self.update_user_mmr(interaction)
        if self.updated:
            send_message = "Your request has been sent to the notification channel."
        else:
            send_message = 'Please only input numbers for mmr'
        await interaction.response.send_message(send_message, ephemeral=True, delete_after=10)

class FindStandInModal(discord.ui.Modal, title="Find a stand-in for your team"):
    def __init__(self):
        super().__init__()
        self.mmr_cap = None

    search_limit = discord.ui.TextInput(label='MMR limit', max_length=5, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        self.mmr_cap = str(self.search_limit)
        try:
            int_mmr_cap = int(self.mmr_cap)
        except ValueError:
            await interaction.response.send_message("Please only input numbers for MMR", ephemeral=True, delete_after=10)
            return
        list_embed = StandInEmbed()
        list_embed.show_stand_ins(int_mmr_cap, interaction.guild)
        await interaction.response.send_message(embed=list_embed, ephemeral=True)


# Select menu for users (above inhouse queue)
class UserOptions(discord.ui.View):
    def __init__(self, chat_channel, server):
        super().__init__(timeout=None)
        self.last_value = None
        self.chat_channel = chat_channel
        self.admin_role = client_db_interface.load_admin_role(server)

    @discord.ui.select(placeholder="Select an action here", min_values=0, max_values=1, options=[
        discord.SelectOption(label="Search Users", value="Search", emoji="🔎",
                             description="Search for a specific user with their name"),
        discord.SelectOption(label="Find A Stand-in", value="Find", emoji="👋",
                             description="Get a list of potential stand-ins"),
        discord.SelectOption(label="Update MMR", value="Update", emoji="❗", description="Notify admins of MMR change"),
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values:
            self.last_value = select.values[0]
        match self.last_value:
            case "Search":
                await interaction.response.send_message(view=SelectUserView(), ephemeral=True)
            case "Find":
                await interaction.response.send_modal(FindStandInModal())
            case "Update":
                update_modal = NotifyUpdateModal()
                await interaction.response.send_modal(update_modal)
                await update_modal.wait()
                if update_modal.updated:
                    await self.chat_channel.send(f'<@&{self.admin_role.id}> User <@{interaction.user.id}> wants their MMR set '
                                           f'to {update_modal.new_mmr}')


class SelectUserView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SelectUserEmbed())


class SelectUserEmbed(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Who do you want to view?", max_values=1, min_values=0)

    async def callback(self, interaction: discord.Interaction):
        user = self.values[0]
        if not client_db_interface.user_registered(user, interaction.guild):
            await interaction.response.send_message("User not registered", ephemeral=True)
            return
        user_embed = UserEmbed()
        user_embed.user_embed(user, interaction.guild)
        await interaction.response.send_message(embed=user_embed, ephemeral=True)

