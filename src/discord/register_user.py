import discord
import data_management
import check_user
from collections import defaultdict


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
            discord.SelectOption(label="Very high", value="1"),
            discord.SelectOption(label="High", value="2"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="4"),
            discord.SelectOption(label="Very low", value="5"),
        ]
    )
    async def select_carry_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, "pos1", select_item.values[0], interaction.guild)
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
            discord.SelectOption(label="Very high", value="1"),
            discord.SelectOption(label="High", value="2"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="4"),
            discord.SelectOption(label="Very low", value="5"),
        ]
    )
    async def select_mid_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, "pos2", select_item.values[0], interaction.guild)
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
            discord.SelectOption(label="Very high", value="1"),
            discord.SelectOption(label="High", value="2"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="4"),
            discord.SelectOption(label="Very low", value="5"),
        ]
    )
    async def select_off_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, "pos3", select_item.values[0], interaction.guild)
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
            discord.SelectOption(label="Very high", value="1"),
            discord.SelectOption(label="High", value="2"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="4"),
            discord.SelectOption(label="Very low", value="5"),
        ]
    )
    async def select_soft_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, "pos4", select_item.values[0], interaction.guild)
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
            discord.SelectOption(label="Very high", value="1"),
            discord.SelectOption(label="High", value="2"),
            discord.SelectOption(label="Moderate", value="3"),
            discord.SelectOption(label="Low", value="4"),
            discord.SelectOption(label="Very low", value="5"),
        ]
    )
    async def select_hard_preference(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        data_management.update_user_data(interaction.user.id, "pos5", select_item.values[0], interaction.guild)
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
    dotabuff_url = discord.ui.TextInput(label='Dotabuff User URL')
    player_mmr = discord.ui.TextInput(label='Player MMR', max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        steam = str(self.dotabuff_url)
        mmr = str(self.player_mmr)
        disc_reg = data_management.check_for_value(interaction.user.id, interaction.guild)
        if disc_reg:
            await interaction.response.send_message(
                'Your discord account is already registered to the database, please contact an admin for assistance',
                ephemeral=True,
                delete_after=10)
        else:
            try:
                int_mmr = int(mmr)
                if int_mmr < 1 or int_mmr > 15000:
                    await interaction.response.send_message('Please enter a valid MMR',
                                                            ephemeral=True,
                                                            delete_after=10)
                else:
                    if "dotabuff.com/players/" in steam:
                        steam = steam.split("players/")
                        steam = steam[1]
                        if "/" in steam:
                            steam = steam.split('/')
                            steam = steam[0]
                        try:
                            steam_int = int(steam)
                            steam_reg = data_management.check_for_value(steam_int, interaction.guild)
                            if steam_reg:
                                await interaction.response.send_message(
                                    'Your dotabuff account is already registered to the database, please contact an admin for assistance',
                                    ephemeral=True,
                                    delete_after=10)
                            else:
                                await register(interaction.user, steam_int, int_mmr, interaction.guild)
                                # Modals cannot be sent from another modal, meaning users will have to manually set roles
                                await interaction.response.send_message(
                                    'You\'ve been registered, please use the appropriate button to set your roles and wait to be vouched',
                                    view=RolePreferenceSelect(), ephemeral=True)
                        except ValueError:
                            await interaction.response.send_message(
                                'There was an error with the dotabuff url you provided, please try again',
                                ephemeral=True,
                                delete_after=10)
                    else:
                        await interaction.response.send_message(
                            'Please enter your full Dotabuff user url when registering',
                            ephemeral=True,
                            delete_after=10)
            except ValueError:
                await interaction.response.send_message('Please only enter numbers when providing your MMR',
                                                        ephemeral=True,
                                                        delete_after=10)


class RegisterButton(discord.ui.View):
    def __init__(self, role_inhouse):
        super().__init__(timeout=None)
        self.role_inhouse = role_inhouse

    @discord.ui.button(label="Click to register for inhouse", emoji="📝",
                       style=discord.ButtonStyle.green)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.role_inhouse in interaction.user.roles:
            await interaction.response.send_message(content="You are already registered", ephemeral=True,
                                                    delete_after=10)
        else:
            await interaction.response.send_modal(RegisterUserModal())

    @discord.ui.button(label="View your details", emoji="📋",
                       style=discord.ButtonStyle.blurple)
    async def view_self(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.role_inhouse in interaction.user.roles:
            user_data = data_management.view_user_data(interaction.user.id, interaction.guild)
            await interaction.response.send_message(embed=check_user.user_embed(user_data, interaction.user, interaction.guild),
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(content="You need to register before you can see your details",
                                                    ephemeral=True)

    @discord.ui.button(label="Update your role preferences", emoji="🖋️",
                       style=discord.ButtonStyle.blurple)
    async def set_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.role_inhouse in interaction.user.roles:
            await interaction.response.send_message(content="Please set your role preferences",
                                                    view=RolePreferenceSelect(), ephemeral=True)
        else:
            await interaction.response.send_message(content="Please register before setting roles",
                                                    ephemeral=True)

async def register(register_user, steam_int, int_mmr, server):
    # Due to how the role balancer calculations work, number weighting is saved the opposite
    # to how users are used to (which is higher number = more pref and lower number = less pref).
    # Swaps have been implemented where required for user output to avoid confusion
    player = [register_user.id, steam_int, int_mmr, 1, 1, 1, 1, 1]
    data_management.add_user_data(player, server)
    # Adds the inhouse role to the user once their details have been added to the register
    role_id = data_management.load_config_data(server, 'ROLES')
    role_inhouse = discord.utils.get(server.roles, id=role_id['registered_role'])
    role_admin = discord.utils.get(server.roles, id=role_id['admin_role'])
    await register_user.add_roles(role_inhouse)
    check_user.user_list("Add", register_user)
    notif_id = data_management.load_config_data(server, 'CHANNELS', 'notification_channel')
    notif_channel = discord.utils.get(server.channels, id=notif_id)
    await notif_channel.send(f'<@&{role_admin.id}> user <@{register_user.id}> has '
                             f'registered for the inhouse and requires verification')
