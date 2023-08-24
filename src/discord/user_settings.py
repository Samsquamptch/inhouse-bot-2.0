import discord
import check_user
import data_management

class EditUserModal(discord.ui.Modal, title='Edit Registered User'):
    player_name = discord.ui.TextInput(label='User\'s global name or Discord username')
    set_mmr = discord.ui.TextInput(label='Set new MMR for user?', max_length=4, required=False)
    remove_verify_role = discord.ui.TextInput(label='Remove verification from user?', max_length=1, required=False)
    ban_user = discord.ui.TextInput(label='Ban user duration? (number = days banned)', max_length=2, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user.user_exists(server, user_name)
        if check_if_exists[0]:
            new_mmr = str(self.set_mmr)
            if new_mmr != "":
                try:
                    int_new_mmr = int(new_mmr)
                except:
                    await interaction.response.send_message('Please only input numbers for inhouse bans',
                                                            ephemeral=True,
                                                            delete_after=10)
            ban_time = str(self.ban_user)
            if ban_time != "":
                try:
                    int_ban_time = int(ban_time)
                except:
                    await interaction.response.send_message('Please only input numbers for inhouse bans',
                                                            ephemeral=True,
                                                            delete_after=10)
            user_account = check_if_exists[1]
            await interaction.response.send_message(f'Details for user {self.player_name} have been updated',
                                                    ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message(f'User {self.player_name} does not exist in database',
                                                    ephemeral=True,
                                                    delete_after=10)


class ViewUserModal(discord.ui.Modal, title='View Users'):
    player_name = discord.ui.TextInput(label='User\'s name (use "all" for full list)')

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
        await interaction.response.send_message(f'User {self.player_name} has been deleted', ephemeral=True,
                                                delete_after=10)


class UserChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Search", emoji="🔎", description="Search for a specific user with their name"),
        discord.SelectOption(label="Ladder", emoji="🪜", description="View player leaderboards (NOT WORKING YET)"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Search":
                await interaction.response.send_modal(ViewUserModal())
            case "Ladder":
                await interaction.response.send_message(content="This feature has not yet been added", ephemeral=True,
                                                        delete_after=10)
            case "Refresh":
                await interaction.response.defer()

class AdminChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Edit", emoji="🖊️", description="Edit a user's details and status"),
        discord.SelectOption(label="Search", emoji="🔎", description="Search for a specific user"),
        discord.SelectOption(label="Remove", emoji="🗑️", description="Delete a registered user"),
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
