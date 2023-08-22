import discord
import check_user


class VerifyUserModal(discord.ui.Modal, title='Verify Registered User'):
    player_name = discord.ui.TextInput(label='User\'s global name or Discord username')
    verify_user = discord.ui.TextInput(label='Verify user?', max_length=1, placeholder='y/n')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        if_exists = check_user.user_exists(server, user_name)
        if if_exists[0]:
            confirm_verification = str(self.verify_user)
            match confirm_verification.lower():
                case "y":
                    user_account = if_exists[1]
                    role = discord.utils.get(server.roles, name="verified")
                    if role not in user_account.roles:
                        await user_account.add_roles(role)
                        await interaction.response.send_message(f'User {self.player_name} has been verified',
                                                                ephemeral=True,
                                                                delete_after=10)
                    else:
                        await interaction.response.send_message(f'User {self.player_name} is already verified',
                                                                ephemeral=True,
                                                                delete_after=10)
                case "n":
                    await interaction.response.send_message(f'User {self.player_name} has not been verified',
                                                            ephemeral=True,
                                                            delete_after=10)
                case _:
                    await interaction.response.send_message(
                        f'please use y/n to confirm verification of user {self.player_name}', ephemeral=True,
                        delete_after=10)
        else:
            await interaction.response.send_message(f'User {self.player_name} does not exist in database',
                                                    ephemeral=True,
                                                    delete_after=10)


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


class ViewUsersModal(discord.ui.Modal, title='View Users'):
    player_name = discord.ui.TextInput(label='User\'s name (use "all" for full list)')

    async def on_submit(self, interaction: discord.Interaction):
        input_name = str(self.player_name)
        if input_name == "all":
            # for i in CSV file
            await interaction.response.send_message('Showing all registered users', ephemeral=True, delete_after=10)
        else:
            print(self.player_name)
            # player_id = discord.utils.get(user.id, nick=self.player_name)
            await interaction.response.send_message(f'Showing user {self.player_name} details', ephemeral=True,
                                                    delete_after=10)


class RemoveUserModal(discord.ui.Modal, title='Delete User from Database'):
    player_name = discord.ui.TextInput(label='User\'s name')
    confirm_deletion = discord.ui.TextInput(label='Confirm deletion?', max_length=1, placeholder='y/n')

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'User {self.player_name} has been deleted', ephemeral=True,
                                                delete_after=10)


class AdminChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Verify", emoji="✅", description="Verify a registered user"),
        discord.SelectOption(label="Edit", emoji="🖊️", description="Edit a user's details and status"),
        discord.SelectOption(label="View", emoji="👀", description="View all registered or a specific user"),
        discord.SelectOption(label="Remove", emoji="❌", description="Delete a registered user"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Verify":
                await interaction.response.send_modal(VerifyUserModal())
            case "Edit":
                await interaction.response.send_modal(EditUserModal())
            case "View":
                await interaction.response.send_modal(ViewUsersModal())
            case "Remove":
                await interaction.response.send_modal(RemoveUserModal())
            case "Refresh":
                await interaction.response.defer()
