import discord
import client_db_interface
from embed_views import UserEmbed
from collections import defaultdict


# TODO: Rework this into RolePreferenceSelect to reduce the amount of redundant code (low priority)
# class PreferenceSelect(discord.ui.Select):
#     def __init__(self):
#         options = [
#             discord.SelectOption(label="Very high", value="5"),
#             discord.SelectOption(label="High", value="4"),
#             discord.SelectOption(label="Moderate", value="3"),
#             discord.SelectOption(label="Low", value="2"),
#             discord.SelectOption(label="Very low", value="1"),
#         ]
#         super().__init__(placeholder="Select an option", max_values=1, min_values=1, options=options)


# Select menus for choosing your role preferences
class RolePreferenceSelect(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.roles_dict = defaultdict(list)

    def preference_counter(self, message_id, role):
        if message_id not in self.roles_dict:
            self.roles_dict[message_id].append(role)
        elif message_id in self.roles_dict and role not in self.roles_dict[message_id]:
            self.roles_dict[message_id].append(role)
        else:
            pass
        for key, value in self.roles_dict.items():
            items_len = len([item for item in value if item])
            if key == message_id and items_len == 5:
                del self.roles_dict[message_id]
                all_roles_updated = True
                return all_roles_updated
        all_roles_updated = False
        return all_roles_updated

    @discord.ui.select(
        custom_id="CarryPref", placeholder="Carry Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_carry_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        client_db_interface.update_user_data(interaction.user.id, "pos1", select_item.values[0])
        message_id = interaction.message.id
        counter_check = self.preference_counter(message_id, "Carry")
        if counter_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(message_id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()

    @discord.ui.select(
        custom_id="MidPref", placeholder="Midlane Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_mid_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        client_db_interface.update_user_data(interaction.user.id, "pos2", select_item.values[0])
        message_id = interaction.message.id
        counter_check = self.preference_counter(message_id, "Midlane")
        if counter_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(message_id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()

    @discord.ui.select(
        custom_id="OffPref", placeholder="Offlane Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_off_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        client_db_interface.update_user_data(interaction.user.id, "pos3", select_item.values[0])
        message_id = interaction.message.id
        counter_check = self.preference_counter(message_id, "Offlane")
        if counter_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(message_id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()

    @discord.ui.select(
        custom_id="SoftPref", placeholder="Soft Support Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_soft_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        client_db_interface.update_user_data(interaction.user.id, "pos4", select_item.values[0])
        message_id = interaction.message.id
        counter_check = self.preference_counter(message_id, "Soft Support")
        if counter_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(message_id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()

    @discord.ui.select(
        custom_id="HardPref", placeholder="Hard Support Preference", min_values=1, max_values=1,
        options=[
            discord.SelectOption(label="Very high", value="5"),
            discord.SelectOption(label="High", value="4"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="2"),
            discord.SelectOption(label="Very low", value="1"),
        ]
    )
    async def select_hard_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        client_db_interface.update_user_data(interaction.user.id, "pos5", select_item.values[0])
        message_id = interaction.message.id
        counter_check = self.preference_counter(message_id, "Hard Support")
        if counter_check:
            await interaction.response.defer()
            await interaction.followup.edit_message(message_id,
                                                    content="Thank you for updating your preferences",
                                                    view=None)
        else:
            await interaction.response.defer()


class RegisterUserModal(discord.ui.Modal, title='Player Register'):
    def __init__(self):
        super().__init__(timeout=None)
        self.steam_int = None
        self.mmr_int = None
        self.is_valid = False

    dotabuff_url = discord.ui.TextInput(label='Dotabuff User URL')
    player_mmr = discord.ui.TextInput(label='Player MMR', max_length=5)

    def confirm_register_values(self, steam, mmr):
        if "dotabuff.com/players/" in steam:
            steam = steam.split("players/")
            steam = steam[1]
        if "/" in steam:
            steam = steam.split('/')
            steam = steam[0]
        try:
            mmr_int = int(mmr)
            steam_int = int(steam)
        except ValueError:
            return 'Please enter your full dotabuff url and your mmr in the appropriate fields'
        if mmr_int < 1 or mmr_int > 15000:
            return None, None,


    def validate_steam(self, steam):
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
            return 'Your dotabuff account is already registered to the database, please contact an admin for assistance'
        self.steam_int = steam_int

    def validate_mmr(self, mmr):
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
        self.is_valid = True
        await interaction.response.send_message(content='You\'ve been registered, please set your roles and wait to be verified',
                                                ephemeral=True, delete_after=10)


class RegisterEmbed(discord.ui.View):
    def __init__(self, approval_list):
        super().__init__(timeout=None)
        self.approval_list = approval_list

    async def register_check(self, user, guild):
        if client_db_interface.user_registered(user, guild):
            message_content = "You are already registered"
        elif client_db_interface.auto_register(user, guild):
            message_content = "Registration complete, please wait to be verified"
            await self.register_notification(user, guild)
        else:
            message_content = None
        return message_content

    @staticmethod
    async def register_user(self, user, steam_int, int_mmr, server):
        player = [user.id, steam_int, int_mmr, 5, 5, 5, 5, 5]
        client_db_interface.add_user_data(player)
        client_db_interface.auto_register(user, server)
        self.approval_list.add_user_to_list(user, int_mmr, True)
        await self.register_notification(user, server)

    @staticmethod
    async def register_notification(user, server):
        admin_role = client_db_interface.load_admin_role(server)
        chat_channel = client_db_interface.load_chat_channel(server)
        await chat_channel.send(f'<@&{admin_role.id}> user <@{user.id}> has '
                                f'registered for the inhouse and requires verification')

    @discord.ui.button(label="Click to register for inhouse", emoji="📝",
                       style=discord.ButtonStyle.green)
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        message_content = await self.register_check(interaction.user, interaction.guild)
        if message_content:
            await interaction.response.send_message(content=message_content, ephemeral=True,
                                                    delete_after=10)
            return
        register_modal = RegisterUserModal()
        await interaction.response.send_modal(register_modal)
        await register_modal.wait()
        if register_modal.is_valid:
            await self.register_user(self, interaction.user, register_modal.steam_int, register_modal.mmr_int, interaction.guild)

    @discord.ui.button(label="View your details", emoji="📋",
                       style=discord.ButtonStyle.blurple)
    async def view_self(self, interaction: discord.Interaction, button: discord.ui.Button):
        if client_db_interface.user_registered(interaction.user, interaction.guild):
            user_embed = UserEmbed(interaction.guild)
            user_embed.user_embed(interaction.user)
            await interaction.response.send_message(embed=user_embed, ephemeral=True)
        else:
            await interaction.response.send_message(content="You need to register before you can see your details",
                                                    ephemeral=True)

    @discord.ui.button(label="Update your role preferences", emoji="🖋️",
                       style=discord.ButtonStyle.blurple)
    async def set_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if client_db_interface.user_registered(interaction.user, interaction.guild):
            await interaction.response.send_message(content="Please set your role preferences",
                                                    view=RolePreferenceSelect(), ephemeral=True)
        else:
            await interaction.response.send_message(content="Please register before setting roles",
                                                    ephemeral=True)

