import discord
import client_db_interface
from src.discord.admin_modals import DiscordSettingsModal, SearchDotabuffModal, EditUserModal, DeleteUserModal, \
    DotaSettingsModal
from src.discord.embed_views import UserEmbed

# Select menu for administrators
class AdminOptions(discord.ui.View):
    def __init__(self, server):
        super().__init__(timeout=None)
        self.server = server
        self.last_value = None
        self.add_item(AdminSelectUserEmbed())

    def change_tryhard_setting(self):
        tryhard_mode = client_db_interface.load_tryhard_settings(self.server)
        if tryhard_mode:
            client_db_interface.update_discord_settings(self.server, "Tryhard", False)
            return "disabled"
        else:
            client_db_interface.update_discord_settings(self.server, "Tryhard", True)
            return "enabled"

    def edit_dota_settings(self, lobby_name, region, league_id, viewer_delay):
        if lobby_name:
            client_db_interface.update_dota_settings(self.server, "LobbyName", lobby_name)
        if region:
            client_db_interface.update_dota_settings(self.server, "Region", region)
        if league_id:
            client_db_interface.update_dota_settings(self.server, "LeagueId", league_id)
        if viewer_delay:
            client_db_interface.update_dota_settings(self.server, "ViewerDelay", viewer_delay)

    def edit_discord_settings(self, mmr_floor, mmr_ceiling, queue_name, akf_timer):
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
                    self.edit_discord_settings(discord_settings.mmr_floor_int, discord_settings.mmr_ceiling_int,
                                            discord_settings.queue_name_string, discord_settings.afk_timer_int)
            case "Dota":
                dota_settings = DotaSettingsModal(self.server)
                await interaction.response.send_modal(dota_settings)
                await dota_settings.wait()
                if dota_settings.edit_settings:
                    self.edit_dota_settings(dota_settings.new_lobby_name, dota_settings.lobby_region_int,
                                            dota_settings.league_id_int, dota_settings.viewer_delay_int)
            case "Tryhard":
                result = self.change_tryhard_setting()
                await interaction.response.send_message("Tryhard mode " + result, ephemeral=True, delete_after=10)
            case "Global":
                await interaction.response.send_message("This option is not yet available")
            case "Search":
                await interaction.response.send_modal(SearchDotabuffModal())


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
