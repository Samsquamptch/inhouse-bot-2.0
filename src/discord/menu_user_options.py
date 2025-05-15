import datetime
import discord
from src.discord import client_db_interface
from embed_views import UserEmbed, StandInEmbed, LadderEmbed


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
        if current_day <= date_obj + datetime.timedelta(days=14):
            return True
        else:
            return False

    def update_user_mmr(self, interaction):
        try:
            int_new_mmr = int(self.new_mmr)
        except ValueError:
            return False
        client_db_interface.update_user_data(interaction.user.id, "MMR", int_new_mmr)
        client_db_interface.update_user_data(interaction.user.id, "LastUpdated",
                                             datetime.datetime.today().strftime('%Y-%m-%d'))
        return True

    async def on_submit(self, interaction: discord.Interaction):
        self.new_mmr = str(self.set_mmr)
        if not client_db_interface.user_registered(interaction.user, interaction.guild):
            await interaction.response.send_message('You need to register first before updating your MMR!',
                                                    ephemeral=True,
                                                    delete_after=10)
            return
        if self.check_updated_recently(interaction.user):
            await interaction.response.send_message('You can only request an MMR update every two weeks',
                                                    ephemeral=True,
                                                    delete_after=10)
            return
        self.updated = self.update_user_mmr(interaction)
        if self.updated:
            send_message = "Your request has been sent to the notification channel."
        else:
            send_message = 'Please only input numbers for mmr'
        await interaction.response.send_message(send_message, ephemeral=True, delete_after=10)


class FindStandInModal(discord.ui.Modal, title="Find a stand-in for your team"):
    def __init__(self, embed):
        super().__init__()
        self.mmr_cap = None
        self.list_embed = embed

    search_limit = discord.ui.TextInput(label='MMR limit', max_length=5, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        self.mmr_cap = str(self.search_limit)
        try:
            int_mmr_cap = int(self.mmr_cap)
        except ValueError:
            await interaction.response.send_message("Please only input numbers for MMR", ephemeral=True,
                                                    delete_after=10)
            return
        self.list_embed.show_stand_ins(int_mmr_cap)
        await interaction.response.send_message(embed=self.list_embed, ephemeral=True)


# Select menu for users (above inhouse queue)
class UserOptions(discord.ui.View):
    def __init__(self, chat_channel, server, approval_list):
        super().__init__(timeout=None)
        self.server = server
        self.last_value = None
        self.chat_channel = chat_channel
        self.admin_role = client_db_interface.load_admin_role(server)
        self.approval_list = approval_list

    def check_tryhard_mode(self):
        tryhard_check = client_db_interface.load_tryhard_settings(self.server)
        if not tryhard_check:
            return False
        return True

    async def request_mmr_update(self, user, mmr):
        self.approval_list.add_user_to_list(user, int(mmr), False)
        await self.chat_channel.send(f'<@&{self.admin_role.id}> User <@{user.id}> wants their MMR set '
                                     f'to {mmr}')

    @discord.ui.select(placeholder="Select an action here", min_values=0, max_values=1, options=[
        discord.SelectOption(label="Search Users", value="Search", emoji="🔎",
                             description="Search for a specific user with their name"),
        discord.SelectOption(label="Find A Stand-in", value="Find", emoji="👋",
                             description="Get a list of potential stand-ins"),
        discord.SelectOption(label="View Ladder", value="Ladder", emoji="📊",
                             description="View the top and bottom ranked players"),
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
                await interaction.response.send_modal(FindStandInModal(StandInEmbed(interaction.guild)))
            case "Ladder":
                if self.check_tryhard_mode():
                    ladder_view = ServerLadderView(self.server, LadderEmbed())
                    ladder_view.set_lists()
                    ladder_view.set_embed_top()
                    await interaction.response.send_message(view=ladder_view, embed=ladder_view.ladder_ui, ephemeral=True)
                else:
                    await interaction.response.send_message(content="Tryhard mode must be enabled to use this feature",
                                                            ephemeral=True, delete_after=10)
            case "Update":
                update_modal = NotifyUpdateModal()
                await interaction.response.send_modal(update_modal)
                await update_modal.wait()
                if update_modal.updated:
                    await self.request_mmr_update(interaction.user, update_modal.new_mmr)


class ServerLadderView(discord.ui.View):
    def __init__(self, server, ladder_ui):
        super().__init__(timeout=None)
        self.server = server
        self.ladder_ui = ladder_ui
        self.top_ten = []
        self.bottom_ten = []
        self.middle_ten = []
        self.ladder_length = 0
        self.ladder_user = None

    def set_lists(self):
        ladder_list = client_db_interface.load_ladder_list(self.server)
        self.ladder_length = len(ladder_list)
        for user_details in ladder_list[:10]:
            user = discord.utils.get(self.server.members, id=user_details[0])
            if user:
                self.top_ten.append(LadderUser(user.name, user_details))
            else:
                self.top_ten.append(LadderUser("Unknown", user_details))
        for user_details in ladder_list[-10:]:
            user = discord.utils.get(self.server.members, id=user_details[0])
            if user:
                self.bottom_ten.append(LadderUser(user, user_details))
            else:
                self.bottom_ten.append(LadderUser("Unknown", user_details))
        if self.ladder_length <= 20:
            self.button_mid_ten.disabled = True
            return
        mid_start = (self.ladder_length//2) - 5
        mid_end = (self.ladder_length//2) + 5
        for user_details in ladder_list[mid_start:mid_end]:
            user = discord.utils.get(self.server.members, id=user_details[0])
            if user:
                self.middle_ten.append(LadderUser(user, user_details))
            else:
                self.middle_ten.append(LadderUser("Unknown", user_details))

    def set_embed_top(self):
        self.ladder_ui.show_ladder(self.top_ten, "top", 1)

    def set_embed_mid(self):
        self.ladder_ui.show_ladder(self.middle_ten, "mid", (self.ladder_length//2) - 5)

    def set_embed_bot(self):
        self.ladder_ui.show_ladder(self.bottom_ten, "bot", self.ladder_length - 9)

    @discord.ui.button(label="View Top 10", emoji="⬆️", style=discord.ButtonStyle.green)
    async def button_top_ten(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.set_embed_top()
        await interaction.response.edit_message(embed=self.ladder_ui, view=self)

    @discord.ui.button(label="View Middle 10", emoji="↔️", style=discord.ButtonStyle.blurple)
    async def button_mid_ten(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.set_embed_mid()
        await interaction.response.edit_message(embed=self.ladder_ui, view=self)

    @discord.ui.button(label="View Bottom 10", emoji="⬇️", style=discord.ButtonStyle.red)
    async def button_bot_ten(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.set_embed_bot()
        await interaction.response.edit_message(embed=self.ladder_ui, view=self)


class LadderUser:
    def __init__(self, name, user_details):
        self.name = name
        self.steam = user_details[1]
        self.mmr = user_details[2]
        self.wins = user_details[3]
        self.losses = user_details[4]
        self.score = user_details[5]


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
        tryhard = client_db_interface.load_tryhard_settings(interaction.guild)
        user_embed = UserEmbed(interaction.guild)
        user_embed.user_embed(user, tryhard)
        await interaction.response.send_message(embed=user_embed, ephemeral=True)
