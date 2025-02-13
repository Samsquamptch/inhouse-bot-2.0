import discord
import discord_service
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
        discord_service.update_user_data(interaction.user.id, "pos1", select_item.values[0])
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
        discord_service.update_user_data(interaction.user.id, "pos2", select_item.values[0])
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
        discord_service.update_user_data(interaction.user.id, "pos3", select_item.values[0])
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
        discord_service.update_user_data(interaction.user.id, "pos4", select_item.values[0])
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
        discord_service.update_user_data(interaction.user.id, "pos5", select_item.values[0])
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
    def __init__(self, admin):
        super().__init__(timeout=None)
        self.admin = admin

    dotabuff_url = discord.ui.TextInput(label='Dotabuff User URL')
    player_mmr = discord.ui.TextInput(label='Player MMR', max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        steam = str(self.dotabuff_url)
        mmr = str(self.player_mmr)
        if discord_service.check_discord_exists(interaction.user.id):
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
                            steam_reg = discord_service.check_steam_exists(steam_int)
                            if steam_reg:
                                await interaction.response.send_message(
                                    'Your dotabuff account is already registered to the database, please contact an admin for assistance',
                                    ephemeral=True,
                                    delete_after=10)
                            else:
                                await register_user(interaction.user, steam_int, int_mmr, interaction.guild)
                                self.admin.unverified_list.append(interaction.user)
                                await interaction.response.send_message(
                                    'You\'ve been registered, please set your roles and wait to be verified',
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
    def __init__(self, admin_panel):
        super().__init__(timeout=None)
        self.admin = admin_panel

    @discord.ui.button(label="Click to register for inhouse", emoji="📝",
                       style=discord.ButtonStyle.green)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        if discord_service.user_registered(interaction.user):
            await interaction.response.send_message(content="You are already registered", ephemeral=True,
                                                    delete_after=10)
        elif discord_service.auto_register(interaction.user, interaction.guild):
            self.admin.unverified_list.append(interaction.user)
            await interaction.response.send_message(content="Registration complete, please wait to be verified", ephemeral=True,
                                                    delete_after=10)
            await register_notification(interaction.user, interaction.guild)
        else:
            await interaction.response.send_modal(RegisterUserModal(self.admin))

    @discord.ui.button(label="View your details", emoji="📋",
                       style=discord.ButtonStyle.blurple)
    async def view_self(self, interaction: discord.Interaction, button: discord.ui.Button):
        if discord_service.user_registered(interaction.user):
            user_data = discord_service.view_user_data(interaction.user.id)
            await interaction.response.send_message(
                embed=check_user.user_embed(user_data, interaction.user, interaction.guild),
                ephemeral=True)
        else:
            await interaction.response.send_message(content="You need to register before you can see your details",
                                                    ephemeral=True)

    @discord.ui.button(label="Update your role preferences", emoji="🖋️",
                       style=discord.ButtonStyle.blurple)
    async def set_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if discord_service.user_registered(interaction.user):
            await interaction.response.send_message(content="Please set your role preferences",
                                                    view=RolePreferenceSelect(), ephemeral=True)
        else:
            await interaction.response.send_message(content="Please register before setting roles",
                                                    ephemeral=True)


async def register_user(user, steam_int, int_mmr, server):
    # Due to how the role balancer calculations work, number weighting is saved the opposite
    # to how users are used to (which is higher number = more pref and lower number = less pref).
    # Swaps have been implemented where required for user output to avoid confusion
    player = [user.id, steam_int, int_mmr, 1, 1, 1, 1, 1]
    discord_service.add_user_data(player)
    discord_service.auto_register(user, server)
    await register_notification(user, server)


async def register_notification(user, server):
    # Adds the inhouse role to the user once their details have been added to the register
    admin_role = discord_service.load_admin_role(server)
    channel_chat_id = discord_service.load_channel_id(server, 'ChatChannel')
    chat_channel = discord.utils.get(server.channels, id=channel_chat_id)
    await chat_channel.send(f'<@&{admin_role.id}> user <@{user.id}> has '
                            f'registered for the inhouse and requires verification')
