import discord
import client_db_interface
from src.discord.embed_superclass import QueueSettings
from src.discord.embed_views import UserEmbed


# Modal for editing user details (accessed via admin select menu)
class EditUserModal(discord.ui.Modal, title='Edit Registered User'):
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
        try:
            steam_int = int(steam)
        except ValueError:
            return "Please enter your full Dotabuff url in the Dotabuff field"
        steam_reg = client_db_interface.check_steam_exists(steam_int)
        if steam_reg:
            return f'This dotabuff account is already registered on the database to user with ID: {steam_reg}'
        self.steam_int = steam_int

    def validate_mmr(self, mmr):
        if mmr == "":
            return
        try:
            mmr_int = int(mmr)
        except ValueError:
            return "Please enter your MMR in the MMR field"
        if mmr_int < 1 or mmr_int > 15000:
            return 'Please enter a valid MMR'
        self.mmr_int = mmr_int

    async def on_submit(self, interaction: discord.Interaction):
        steam = str(self.dotabuff_url)
        mmr = str(self.player_mmr)
        error_message = self.validate_steam(steam)
        if error_message:
            await interaction.response.send_message(content=error_message, ephemeral=True, delete_after=10)
            return
        error_message = self.validate_mmr(mmr)
        if error_message:
            await interaction.response.send_message(content=error_message, ephemeral=True, delete_after=10)
            return
        self.edit_user = True
        await interaction.response.send_message(content='User details have been updated', ephemeral=True, delete_after=10)


class DiscordSettingsModal(discord.ui.Modal, QueueSettings, title='Change Discord Settings'):
    def __init__(self, server):
        discord.ui.Modal.__init__(self, timeout=None)
        QueueSettings.__init__(self, server)
        self.mmr_floor_int = None
        self.mmr_ceiling_int = None
        self.queue_name_string = None
        self.afk_timer_int = None
        self.edit_settings = False

    new_mmr_floor = discord.ui.TextInput(label='Set Minimum MMR', required=False)
    new_mmr_limit = discord.ui.TextInput(label='Set Maximum MMR', required=False)
    new_queue_name = discord.ui.TextInput(label='Set inhouse queue name', required=False)
    new_afk_timer = discord.ui.TextInput(label='Set afk time', required=False)

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
            return "Please ensure you only enter numerical values for MMR fields (e.g. 5500 instead of 5.5K)"
        if floor_int >= ceiling_int or floor_int < 0:
            return "Please ensure that the mmr floor is equal to or greater than 0 and lower than the mmr limit"
        if floor:
            self.mmr_floor_int = floor_int
        if ceiling:
            self.mmr_ceiling_int = ceiling_int

    def check_int_value(self, string_value):
        try:
            int_value = int(string_value)
            return int_value
        except ValueError:
            return None

    def validate_afk(self, afk):
        if afk == "":
            return
        afk_int = self.check_int_value(afk)
        if not afk_int:
            return "Please ensure you only enter numerical values for the afk field (e.g. 15 instead of fifteen)"
        self.afk_timer_int = afk_int

    def set_queue_name(self, queue_name):
        if queue_name == "":
            return
        self.queue_name_string = queue_name

    async def on_submit(self, interaction: discord.Interaction):
        str_mmr_floor = str(self.new_mmr_floor)
        str_mmr_limit = str(self.new_mmr_limit)
        str_queue_name = str(self.new_queue_name)
        str_afk_timer = str(self.new_afk_timer)
        denied_message = self.validate_mmr_inputs(str_mmr_floor, str_mmr_limit)
        if denied_message:
            return await interaction.response.send_message(denied_message, ephemeral=True, delete_after=10)
        denied_message = self.validate_afk(str_afk_timer)
        if denied_message:
            return await interaction.response.send_message(denied_message, ephemeral=True, delete_after=10)
        self.set_queue_name(str_queue_name)
        self.edit_settings = True
        await interaction.response.send_message("Server settings have been updated", ephemeral=True, delete_after=10)


class DotaSettingsModal(discord.ui.Modal, title='Change Discord Settings'):
    lobby_name = discord.ui.TextInput(label='Set lobby name', required=False)
    all_chat = discord.ui.TextInput(label='Enable/Disable voice allchat', required=False)
    region = discord.ui.TextInput(label='Set inhouse region', required=False)
    league_id = discord.ui.TextInput(label='Set inhouse league ID', required=False)
    viewer_delay = discord.ui.TextInput(label='Set viewer delay', required=False)

    async def on_submit(self, interaction: discord.Interaction):
        return
        # if str_league_id != "":
        #     try:
        #         client_db_interface.update_dota_settings(interaction.guild, 'LeagueId', str_league_id)
        #     except ValueError:
        #         await interaction.response.send_message(f'Please only input numbers for the league ID',
        #                                                 ephemeral=True, delete_after=10)


# Select menu for administrators
class AdminOptions(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server
        self.last_value = None
        self.add_item(AdminSelectUserEmbed())

    # def edit_user(self, user, mmr, steam_id):
    #     if not user:
    #         return
    #     if mmr:
    #         client_db_interface.update_user_data(user.id, "MMR", mmr)
    #     if steam_id:
    #         client_db_interface.update_user_data(user.id, "Steam", steam_id)
    #     return


    def search_user_dotabuff(self):
        return

    def edit_discord_settings(self):
        return

    def edit_dota_settings(self, mmr_floor, mmr_ceiling, queue_name, akf_timer):
        if mmr_floor:
            client_db_interface.update_discord_settings(self.server, "SkillFloor", mmr_floor)
        if mmr_ceiling:
            client_db_interface.update_discord_settings(self.server, "SkillCeiling", mmr_ceiling)
        if queue_name:
            client_db_interface.update_discord_settings(self.server, "QueueName", queue_name)
        if akf_timer:
            client_db_interface.update_discord_settings(self.server, "AfkTimer", akf_timer)

    @discord.ui.select(placeholder="Change server settings here", min_values=0, max_values=1, options=[
        discord.SelectOption(label="Edit Discord Settings", value="Discord", emoji="🖥️",
                             description="Change Discord Settings"),
        discord.SelectOption(label="Edit Dota Settings", value="Dota", emoji="🖱️", description="Change Dota Settings"),
        discord.SelectOption(label="Change Tryhard Mode", value="Tryhard", emoji="🤓",
                             description="Enable or Disable Tryhard Mode"),
        discord.SelectOption(label="Edit Global Queue Settings", value="Global", emoji="🌍",
                             description="Change Global Queue Settings"),
        discord.SelectOption(label="Dotabuff Search", value="Search", emoji="🔎",
                             description="Search User by Dotabuff url")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values:
            self.last_value = select.values[0]
        match self.last_value:
            case "Discord":
                discord_settings = DiscordSettingsModal(self.server)
                await interaction.response.send_modal(discord_settings)
                await discord_settings.wait()
                if discord_settings.edit_settings:
                    self.edit_dota_settings(discord_settings.mmr_floor_int, discord_settings.mmr_ceiling_int,
                                            discord_settings.queue_name_string, discord_settings.afk_timer_int)
            case "Tryhard":
                await interaction.response.defer()
            case "Dota":
                await interaction.response.defer()
            case "Global":
                await interaction.response.defer()


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


class ManageUserEmbed(discord.ui.View):
    def __init__(self, user, server, user_ui):
        super().__init__(timeout=None)
        self.user = user
        self.server = server
        self.user_ui = user_ui

    def set_button_state(self):
        if client_db_interface.get_banned_status(self.user, self.server):
            self.set_ban.label = "Unban User"
        else:
            self.set_ban.label = "Ban User"
        if client_db_interface.get_verified_status(self.user, self.server):
            self.set_verification.label = "Remove Verification"
        else:
            self.set_verification.label = "Verify User"

    def change_user_verification(self):
        user_status = client_db_interface.get_verified_status(self.user, self.server)
        if user_status:
            client_db_interface.disable_verification(self.user, self.server)
        else:
            client_db_interface.enable_verification(self.user, self.server)
        self.user_ui.user_embed(self.user)

    def change_user_ban_status(self):
        user_status = client_db_interface.get_banned_status(self.user, self.server)
        if user_status:
            client_db_interface.unban_user(self.user, self.server)
        else:
            client_db_interface.ban_user(self.user, self.server)
        self.user_ui.user_embed(self.user)

    def update_user_details(self, mmr, steam):
        if mmr:
            client_db_interface.update_user_data(self.user.id, "MMR", mmr)
        if steam:
            client_db_interface.update_user_data(self.user.id, "Steam", steam)

    @discord.ui.button(label="Edit User Details", emoji="🖊️", style=discord.ButtonStyle.blurple)
    async def edit_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_id = interaction.message.id
        edit_modal = EditUserModal()
        await interaction.response.send_modal(edit_modal)
        await edit_modal.wait()
        if edit_modal.edit_user:
            self.update_user_details(edit_modal.mmr_int, edit_modal.steam_int)
            await interaction.followup.edit_message(message_id, embed=self.user_ui, view=self)
        self.set_button_state()


    @discord.ui.button(label="Set Verification", emoji="✅", style=discord.ButtonStyle.green)
    async def set_verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.change_user_verification()
        self.set_button_state()
        await interaction.response.edit_message(embed=self.user_ui, view=self)

    @discord.ui.button(label="Ban User", emoji="❌", style=discord.ButtonStyle.red)
    async def set_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.change_user_ban_status()
        self.set_button_state()
        await interaction.response.edit_message(embed=self.user_ui, view=self)

    @discord.ui.button(label="Delete User", emoji="🗑️", style=discord.ButtonStyle.gray)
    async def delete_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        delete_modal = DeleteUserModal()
        await interaction.response.send_modal(delete_modal)
        await delete_modal.wait()
        if delete_modal.confirm_delete:
            client_db_interface.remove_user_data(self.user, self.server)
            await interaction.delete_original_response()


class AdminSelectUserEmbed(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(placeholder="Which user do you wish to manage?", max_values=1, min_values=0)

    async def callback(self, interaction: discord.Interaction):
        user = self.values[0]
        if not client_db_interface.user_registered(user, interaction.guild):
            await interaction.response.send_message("User not registered", ephemeral=True)
            return
        user_view = ManageUserEmbed(user, interaction.guild, UserEmbed(interaction.guild))
        user_view.set_button_state()
        user_view.user_ui.user_embed(user)
        await interaction.response.send_message(view=user_view, embed=user_view.user_ui, ephemeral=True)
