import discord
from src.discord import client_db_interface
from src.discord.embed_superclass import QueueSettings
from src.discord.embed_views import UserEmbed


class ModalValidator:
    def __init__(self):
        self.error_message = None

    def check_int_value(self, string_value):
        try:
            int_value = int(string_value)
            return int_value
        except ValueError:
            return None


class DeleteUserModal(discord.ui.Modal, title='Confirm Deletion'):
    def __init__(self):
        super().__init__(timeout=None)
        self.delete_user = False

    confirm_delete = discord.ui.TextInput(label='Enter \'yes\' to delete the user', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        delete_check = str(self.confirm_delete)
        if delete_check.lower() == "yes":
            self.delete_user = True
            await interaction.response.send_message(content="User has been deleted", ephemeral=True)
            return
        await interaction.response.defer()
        return


class SearchDotabuffModal(discord.ui.Modal, ModalValidator, title='Search User by Dotabuff URL'):
    def __init__(self):
        super().__init__(timeout=None)
        self.steam_id = None
        self.user_account = None

    search_url = discord.ui.TextInput(label='Please enter the Dotabuff URL here', required=True)

    def validate_steam(self, steam):
        if steam == "":
            return
        if "dotabuff.com/players/" in steam:
            steam = steam.split("players/")
            steam = steam[1]
        if "/" in steam:
            steam = steam.split('/')
            steam = steam[0]
        steam_int = self.check_int_value(steam)
        if not steam_int:
            self.error_message = "Please enter your full Dotabuff url in the Dotabuff field"
            return
        steam_reg = client_db_interface.check_steam_exists(steam_int)
        if not steam_reg:
            self.error_message = "No user with this Dotabuff account found in the database"
            return
        self.steam_id = steam_int

    def user_exists(self, server):
        discord_id = client_db_interface.load_user_from_steam(self.steam_id)
        user = discord.utils.get(server.members, id=discord_id)
        if not user:
            self.error_message = f"User with ID: {discord_id} not found on this server"
            return
        self.user_account = user

    async def on_submit(self, interaction: discord.Interaction):
        dotabuff_url = str(self.search_url)
        self.validate_steam(dotabuff_url)
        self.user_exists(interaction.guild)
        if self.error_message:
            await interaction.response.send_message(content=self.error_message, ephemeral=True, delete_after=10)
            return
        user_embed = UserEmbed(interaction.guild)
        user_embed.user_embed(self.user_account, True)
        await interaction.response.send_message(content="User Details found", embed=user_embed, ephemeral=True)


class EditUserModal(discord.ui.Modal, ModalValidator, title='Edit Registered User'):
    def __init__(self):
        super().__init__(timeout=None)
        self.mmr_int = None
        self.steam_int = None
        self.edit_user = False

    player_mmr = discord.ui.TextInput(label='Set new MMR for user?', max_length=5, required=False)
    dotabuff_url = discord.ui.TextInput(label='Edit Dotabuff User URL?', required=False)

    def validate_steam(self, steam):
        if steam == "":
            return
        if "dotabuff.com/players/" in steam:
            steam = steam.split("players/")
            steam = steam[1]
        if "/" in steam:
            steam = steam.split('/')
            steam = steam[0]
        steam_int = self.check_int_value(steam)
        if not steam_int:
            self.error_message = "Please enter your full Dotabuff url in the Dotabuff field"
            return
        steam_reg = client_db_interface.check_steam_exists(steam_int)
        if steam_reg:
            self.error_message = f'This dotabuff account is already registered on the database to user with ID: {steam_reg}'
            return
        self.steam_int = steam_int

    def validate_mmr(self, mmr):
        if mmr == "":
            return
        mmr_int = self.check_int_value(mmr)
        if not mmr_int:
            self.error_message = "Please enter your MMR in the MMR field"
            return
        if not 1 <= mmr_int <= 15000:
            self.error_message = 'Please enter a valid MMR'
            return
        self.mmr_int = mmr_int

    async def on_submit(self, interaction: discord.Interaction):
        steam = str(self.dotabuff_url)
        mmr = str(self.player_mmr)
        self.validate_steam(steam)
        self.validate_mmr(mmr)
        if self.error_message:
            await interaction.response.send_message(content=self.error_message, ephemeral=True, delete_after=10)
            return
        self.edit_user = True
        await interaction.response.send_message(content='User details have been updated', ephemeral=True, delete_after=10)


class DiscordSettingsModal(discord.ui.Modal, QueueSettings, ModalValidator, title='Change Discord Settings'):
    def __init__(self, server):
        discord.ui.Modal.__init__(self, timeout=None)
        ModalValidator.__init__(self)
        QueueSettings.__init__(self, server)
        self.mmr_floor_int = None
        self.mmr_ceiling_int = None
        self.ping_role_int = None
        self.afk_timer_int = None
        self.champion_role_int = None
        self.edit_settings = False

    new_mmr_floor = discord.ui.TextInput(label='Set Minimum MMR', required=False)
    new_mmr_limit = discord.ui.TextInput(label='Set Maximum MMR', required=False)
    new_ping_role = discord.ui.TextInput(label='Set inhouse ping role', required=False)
    new_afk_timer = discord.ui.TextInput(label='Set afk time', required=False)
    new_champion_role = discord.ui.TextInput(label='Set champion role', required=False)

    def validate_mmr_inputs(self, floor, ceiling):
        if not floor and not ceiling:
            return
        if floor:
            floor_int = self.check_int_value(floor)
        else:
            floor_int = self.mmr_floor
        if ceiling:
            ceiling_int = self.check_int_value(ceiling)
        else:
            ceiling_int = self.mmr_ceiling
        if not floor_int or not ceiling_int:
            self.error_message = "Please ensure you only enter numerical values for MMR fields (e.g. 5500 instead of 5.5K)"
            return
        if floor_int >= ceiling_int or floor_int < 0:
            self.error_message = "Please ensure that the mmr floor is equal to or greater than 0 and lower than the mmr limit"
            return
        if floor:
            self.mmr_floor_int = floor_int
        if ceiling:
            self.mmr_ceiling_int = ceiling_int

    def validate_afk(self, afk):
        if afk == "":
            return
        afk_int = self.check_int_value(afk)
        if not afk_int:
            self.error_message = "Please ensure you only enter numerical values for the afk field (e.g. 15 instead of fifteen)"
            return
        if afk_int < 0:
            self.error_message = "Please ensure that the afk check timer is greater than or equal to 0"
            return
        self.afk_timer_int = afk_int

    def validate_ping_role(self, ping_role):
        if ping_role == "":
            return
        ping_int = self.check_int_value(ping_role)
        if not ping_int:
            self.error_message = "Please ensure you entered the correct role ID of your chosen ping role"
            return
        self.ping_role_int = ping_int

    def validate_champion_role(self, champion):
        if champion == "":
            return
        champion_int = self.check_int_value(champion)
        if not champion_int:
            self.error_message = "Please ensure you entered the correct role ID of your chosen champion role"
            return
        self.champion_role_int = champion_int


    async def on_submit(self, interaction: discord.Interaction):
        str_mmr_floor = str(self.new_mmr_floor)
        str_mmr_limit = str(self.new_mmr_limit)
        str_ping_role = str(self.new_ping_role)
        str_afk_timer = str(self.new_afk_timer)
        str_champion_role = str(self.new_champion_role)
        self.validate_mmr_inputs(str_mmr_floor, str_mmr_limit)
        self.validate_afk(str_afk_timer)
        self.validate_champion_role(str_champion_role)
        self.validate_ping_role(str_ping_role)
        if self.error_message:
            return await interaction.response.send_message(self.error_message, ephemeral=True, delete_after=10)
        self.edit_settings = True
        await interaction.response.send_message("Server settings have been updated", ephemeral=True, delete_after=10)


class DotaSettingsModal(discord.ui.Modal, ModalValidator, title='Change Discord Settings'):

    def __init__(self, server):
        discord.ui.Modal.__init__(self, timeout=None)
        ModalValidator.__init__(self)
        self.new_lobby_name = None
        self.lobby_region_int = None
        self.league_id_int = None
        self.viewer_delay_int = None
        self.new_lobby_password = None
        self.edit_settings = False

    lobby_name = discord.ui.TextInput(label='Set lobby name', required=False)
    lobby_region = discord.ui.TextInput(label='Set inhouse region', required=False)
    league_id = discord.ui.TextInput(label='Set inhouse league ID', required=False)
    viewer_delay = discord.ui.TextInput(label='Set viewer delay', required=False)
    lobby_password = discord.ui.TextInput(label='Set lobby password', required=False)

    def validate_lobby_name(self, lobby_name):
        if lobby_name == "":
            return
        self.new_lobby_name = lobby_name

    def validate_password(self, password):
        if password =="":
            return
        self.new_lobby_password = password

    def validate_region(self, region):
        if region == "":
            return
        int_region = self.check_int_value(region)
        if not int_region:
            self.error_message = "Please only enter an int value for the lobby region. Check the github wiki page for more information"
            return
        region_list = list(range(1, 17))
        region_list.append(37)
        if int_region not in region_list:
            self.error_message = "Please input a region ID which matches one of the parameters outlined in the github repository wiki"
            return
        self.lobby_region_int = region

    def validate_league_id(self, league_id):
        if league_id == "":
            return
        int_lobby_id = self.check_int_value(league_id)
        if not int_lobby_id:
            self.error_message = "Please enter the league id you wish to use for the lobby"
            return
        self.league_id_int = int_lobby_id

    def validate_viewer_delay(self, viewer_delay):
        if viewer_delay == "":
            return
        int_viewer_delay = self.check_int_value(viewer_delay)
        if not int_viewer_delay:
            self.error_message = "Please enter the viewer delay amount in minutes"
            return
        self.viewer_delay = int_viewer_delay

    async def on_submit(self, interaction: discord.Interaction):
        str_lobby_name = str(self.lobby_name)
        str_region = str(self.lobby_region)
        str_league_id = str(self.league_id)
        str_viewer_delay = str(self.viewer_delay)
        str_lobby_password = str(self.lobby_password)
        self.validate_lobby_name(str_lobby_name)
        self.validate_password(str_lobby_password)
        self.validate_region(str_region)
        self.validate_league_id(str_league_id)
        self.validate_viewer_delay(str_viewer_delay)
        if self.error_message:
            await interaction.response.send_message(content=self.error_message, ephemeral=True, delete_after=10)
            return
        self.edit_settings = True
        await interaction.response.send_message(content="Settings have been updated", ephemeral=True, delete_after=10)
