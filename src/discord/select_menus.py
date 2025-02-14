import discord
import check_user
import client_db_interface
import datetime


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

# Modal for editing user details (accessed via admin select menu)
class EditUserModal(discord.ui.Modal, title='Edit Registered User'):
    player_name = discord.ui.TextInput(label='User\'s global name or Discord username')
    set_mmr = discord.ui.TextInput(label='Set new MMR for user?', max_length=5, required=False)
    new_dotabuff = discord.ui.TextInput(label='Edit Dotabuff User URL?', required=False)
    remove_verify = discord.ui.TextInput(label='Remove verification from user?', max_length=1, required=False)
    ban_user = discord.ui.TextInput(label='Ban or unban a user from inhouse queue?', max_length=1, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user.user_exists(server, user_name)
        if not check_if_exists[0]:
            await interaction.response.send_message(f'User {self.player_name} does not exist in database',
                                                    ephemeral=True,
                                                    delete_after=10)
            return
        new_mmr = str(self.set_mmr)
        if new_mmr != "":
            try:
                int_new_mmr = int(new_mmr)
                client_db_interface.update_user_data(check_if_exists[1].id, "mmr", int_new_mmr)
            except ValueError:
                await interaction.response.send_message('Please only input numbers for mmr',
                                                        ephemeral=True,
                                                        delete_after=10)
        steam_id = str(self.new_dotabuff)
        if steam_id != "":
            try:
                steam_id = steam_id.split("players/")
                steam_id = steam_id[1].split('/')
                int_steam_id = int(steam_id[0])
                client_db_interface.update_user_data(check_if_exists[1].id, "steam", int_steam_id)
            except ValueError:
                await interaction.response.send_message('Please enter a full Dotabuff URL when updating a user',
                                                        ephemeral=True,
                                                        delete_after=10)
        verify_role = str(self.remove_verify)
        if verify_role == "":
            pass
        elif verify_role.lower() == "y":
            client_db_interface.set_verification(check_if_exists[1], server, "False")
        else:
            await interaction.response.send_message('Please enter "y" to confirm removal of verified role',
                                                    ephemeral=True,
                                                    delete_after=10)
        ban_time = str(self.ban_user)
        if ban_time == "":
            pass
        elif ban_time.lower() == "y":
            if client_db_interface.get_banned_status(check_if_exists[1], server):
                client_db_interface.set_banned(check_if_exists[1], server, False)
            else:
                client_db_interface.set_banned(check_if_exists[1], server, True)
        else:
            await interaction.response.send_message('Please enter "y" to confirm add or removal of ban',
                                                    ephemeral=True,
                                                    delete_after=10)
        await interaction.response.send_message(f'Details for user {self.player_name} have been updated',
                                                ephemeral=True, delete_after=10)


class RemoveUserModal(discord.ui.Modal, title='Delete User from Database'):
    player_name = discord.ui.TextInput(label='User\'s name')
    confirm_deletion = discord.ui.TextInput(label='Confirm deletion?', max_length=1, placeholder='y/n')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        delete_conf = str(self.confirm_deletion)
        server = interaction.user.guild
        check_if_exists = check_user.user_exists(server, user_name)
        if check_if_exists[0]:
            if delete_conf.lower() == "y":
                client_db_interface.remove_user_data(check_if_exists[1], server)
                await interaction.response.send_message(f'User {self.player_name} has been deleted', ephemeral=True,
                                                        delete_after=10)
            else:
                await interaction.response.send_message(f'Please enter "y" to confirm removal of player',
                                                        ephemeral=True,
                                                        delete_after=10)
        else:
            await interaction.response.send_message(content=f'User {user_name} is not registered', ephemeral=True,
                                                    delete_after=10)


class DiscordSettingsModal(discord.ui.Modal, title='Change Discord Settings'):
    mmr_floor = discord.ui.TextInput(label='Set Minimum MMR', required=False)
    mmr_limit = discord.ui.TextInput(label='Set Maximum MMR', required=False)
    queue_name = discord.ui.TextInput(label='Set inhouse queue name', required=False)
    afk_timer = discord.ui.TextInput(label='Set afk time', required=False)

    # league_id = discord.ui.TextInput(label='Set league ID', required=False)

    async def on_submit(self, interaction: discord.Interaction):
        str_mmr_floor = str(self.mmr_floor)
        str_mmr_limit = str(self.mmr_limit)
        str_queue_name = str(self.queue_name)
        str_afk_timer = str(self.afk_timer)
        settings_dict = {'SkillFloor': str_mmr_floor, 'SkillCeiling': str_mmr_limit, 'AfkTimer': str_afk_timer}
        for item in settings_dict:
            if settings_dict[item] != "":
                try:
                    settings_dict[item] = int(settings_dict[item])
                    client_db_interface.update_discord_settings(interaction.guild, item, settings_dict[item])
                except ValueError:
                    await interaction.response.send_message(f'Please only input numbers for {item}',
                                                            ephemeral=True, delete_after=10)
        if str_queue_name != "":
            client_db_interface.update_discord_settings(interaction.guild, 'QueueName', str_queue_name.upper())
        # if str_league_id != "":
        #     try:
        #         client_db_interface.update_dota_settings(interaction.guild, 'LeagueId', str_league_id)
        #     except ValueError:
        #         await interaction.response.send_message(f'Please only input numbers for the league ID',
        #                                                 ephemeral=True, delete_after=10)
        await interaction.response.send_message(f'Server config file has been updated.',
                                                ephemeral=True, delete_after=10)


# Select menu for administrators
class AdminOptions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.last_value = None

    @discord.ui.select(placeholder="Select an action here", min_values=0, max_values=1, options=[
        discord.SelectOption(label="Edit", emoji="🖊️", description="Edit a user's details and status"),
        discord.SelectOption(label="Search", emoji="🔎", description="Search for a specific user"),
        discord.SelectOption(label="Remove", emoji="🗑️", description="Delete a registered user"),
        discord.SelectOption(label="Discord Settings", emoji="🖥️", description="Change Discord Settings"),
        discord.SelectOption(label="Dota Settings", emoji="🖱️", description="Change Dota Settings")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values:
            self.last_value = select.values[0]
        match self.last_value:
            case "Edit":
                await interaction.response.send_modal(EditUserModal())
            case "Search":
                await interaction.response.send_modal(ViewUserModal())
            case "Remove":
                await interaction.response.send_modal(RemoveUserModal())
            case "Discord Settings":
                await interaction.response.send_modal(DiscordSettingsModal())
            case "Dota Settings":
                await interaction.response.defer()
