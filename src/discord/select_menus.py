import discord
import check_user
import data_management


#Modal for editing user details (accessed via admin select menu)
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
        if check_if_exists[0]:
            new_mmr = str(self.set_mmr)
            if new_mmr != "":
                try:
                    int_new_mmr = int(new_mmr)
                    data_management.update_user_data(check_if_exists[1].id, [2], int_new_mmr)
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
                    data_management.update_user_data(check_if_exists[1].id, [1], int_steam_id)
                except ValueError:
                    await interaction.response.send_message('Please enter a full Dotabuff URL when updating a user',
                                                            ephemeral=True,
                                                            delete_after=10)
            verify_role = str(self.remove_verify)
            if verify_role != "":
                if verify_role.lower() == "y":
                    role_verified = discord.utils.get(server.roles, name="verified")
                    await check_if_exists[1].remove_roles(role_verified)
                else:
                    await interaction.response.send_message('Please enter "y" to confirm removal of verified role',
                                                            ephemeral=True,
                                                            delete_after=10)
            ban_time = str(self.ban_user)
            if ban_time != "":
                if ban_time.lower() == "y":
                    role_banned = discord.utils.get(server.roles, name="queue ban")
                    if role_banned in check_if_exists[1].roles:
                        await check_if_exists[1].remove_roles(role_banned)
                    else:
                        await check_if_exists[1].add_roles(role_banned)
                else:
                    await interaction.response.send_message('Please enter "y" to confirm add or removal of ban',
                                                            ephemeral=True,
                                                            delete_after=10)
            # ban_time = str(self.ban_user)
            # if ban_time != "":
            #     try:
            #         int_ban_time = int(ban_time)
            #         print(int_ban_time)
            #     except ValueError:
            #         await interaction.response.send_message('Please only input numbers for inhouse bans',
            #                                                 ephemeral=True,
            #                                                 delete_after=10)
            await interaction.response.send_message(f'Details for user {self.player_name} have been updated',
                                                    ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message(f'User {self.player_name} does not exist in database',
                                                    ephemeral=True,
                                                    delete_after=10)


class ViewUserModal(discord.ui.Modal, title='View User'):
    player_name = discord.ui.TextInput(label='User\'s global name or username')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user.user_exists(server, user_name)
        if check_if_exists[0]:
            user_data = data_management.view_user_data(check_if_exists[1].id)
            await interaction.response.send_message(embed=check_user.user_embed(user_data, check_if_exists[1], server),
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(content=f'User {user_name} is not registered', ephemeral=True,
                                                    delete_after=10)


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
                role_inhouse = discord.utils.get(server.roles, name="inhouse")
                role_verified = discord.utils.get(server.roles, name="verified")
                await check_if_exists[1].remove_roles(role_inhouse, role_verified)
                data_management.remove_user_data(check_if_exists[1].id)
                await interaction.response.send_message(f'User {self.player_name} has been deleted', ephemeral=True,
                                                        delete_after=10)
            else:
                await interaction.response.send_message(f'Please enter "y" to confirm removal of player',
                                                        ephemeral=True,
                                                        delete_after=10)
        else:
            await interaction.response.send_message(content=f'User {user_name} is not registered', ephemeral=True,
                                                    delete_after=10)


# Select menu for users (above inhouse queue)
class UserOptions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Search", emoji="🔎", description="Search for a specific user with their name"),
        discord.SelectOption(label="Update", emoji="❗", description="Notify admins of MMR change (NOT WORKING YET)"),
        discord.SelectOption(label="Ladder", emoji="🪜", description="View player leaderboards (NOT WORKING YET)"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Search":
                await interaction.response.send_modal(ViewUserModal())
            case "Update":
                await interaction.response.send_message(content="This feature has not yet been added", ephemeral=True,
                                                        delete_after=10)
            case "Ladder":
                await interaction.response.send_message(content="This feature has not yet been added", ephemeral=True,
                                                        delete_after=10)
            case "Refresh":
                await interaction.response.defer()


# Select menu for administrators
class AdminOptions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Edit", emoji="🖊️", description="Edit a user's details and status"),
        discord.SelectOption(label="Search", emoji="🔎", description="Search for a specific user"),
        discord.SelectOption(label="Remove", emoji="🗑️", description="Delete a registered user (NOT WORKING YET"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Edit":
                await interaction.response.send_modal(EditUserModal())
            case "Search":
                await interaction.response.send_modal(ViewUserModal())
            case "Remove":
                await interaction.response.send_modal(RemoveUserModal())
            case "Refresh":
                await interaction.response.defer()
