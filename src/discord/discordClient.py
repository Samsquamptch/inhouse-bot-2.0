import discord
from discord.ext import commands
import setRoles
import dataManagement
import yaml
from yaml.loader import SafeLoader

class VerifyUserModal(discord.ui.Modal, title='Verify Registered User'):
    player_name = discord.ui.TextInput(label='User\'s global name or Discord username')
    verify_user = discord.ui.TextInput(label='Verify user?', max_length=1, placeholder='y/n')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user_exists(server, user_name)
        if check_if_exists[0] == True:
            confirm_verification = str(self.verify_user)
            match confirm_verification.lower():
                case "y":
                    user_account = check_if_exists[1]
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
            await interaction.response.send_message(f'User {self.player_name} does not exist in database', ephemeral=True,
                                                    delete_after=10)


class EditUserModal(discord.ui.Modal, title='Edit Registered User'):
    player_name = discord.ui.TextInput(label='User\'s global name or Discord username')
    set_mmr = discord.ui.TextInput(label='Set new MMR for user?', max_length=4, required=False)
    remove_verify_role = discord.ui.TextInput(label='Remove verification from user?', max_length=1, required=False)
    ban_user = discord.ui.TextInput(label='Ban user duration? (number = days banned)', max_length=2, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user_exists(server, user_name)
        if check_if_exists[0] == True:
            try:
                ban_time = str(self.ban_user)
                if ban_time != "":
                    int_ban_time = int(ban_time)
                    print(int_ban_time)
            except:
                await interaction.response.send_message('Please only input numbers for inhouse bans', ephemeral=True, delete_after=10)
            user_account = check_if_exists[1]
            await interaction.response.send_message(f'Details for user {self.player_name} have been updated',
                                                    ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message(f'User {self.player_name} does not exist in database', ephemeral=True,
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


class RegisterUserModal(discord.ui.Modal, title='Player Register'):
    dotabuff_url = discord.ui.TextInput(label='Dotabuff User URL')
    player_mmr = discord.ui.TextInput(label='Player MMR')

    async def on_submit(self, interaction: discord.Interaction):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        disc = interaction.user.id
        steam = str(self.dotabuff_url)
        mmr = self.player_mmr
        if "players/" in steam:
            steam = steam.split("players/")
            steam = steam[1]
            player = [disc,steam,mmr,5,5,5,5,5]
            dataManagement.add_user_data(player)
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                'You\'ve been registered, please set your roles (from top to bottom) and wait to be vouched',
                view=setRoles.RolePreferenceSelect(), ephemeral=True)
        else:
            await interaction.response.send_message('Please enter your full Dotabuff user url when registering',
                                                    ephemeral=True,
                                                    delete_after=10)


class PlayerViewModal(discord.ui.Modal, title='View Player '):
    player_name = discord.ui.TextInput(label='Player name')

    async def on_submit(self, interaction: discord.Interaction):
        # player_id = discord.utils.get(user.id, nick=self.player_name)
        await interaction.response.send_message(f'Looking for user {self.player_name}', ephemeral=True, delete_after=10)


class RegisterButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click to register for inhouse", emoji="📋",
                       style=discord.ButtonStyle.green)
    async def register(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        if role in interaction.user.roles:
            await interaction.response.send_message(content="You are already registered", ephemeral=True)
        else:
            await interaction.response.send_modal(RegisterUserModal())


class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    queue_list = []
    queue_player_name = []

    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        if role in interaction.user.roles:
            if interaction.user in self.queue_list:
                await interaction.response.send_message(content="You are already queued", ephemeral=True)
            else:
                self.queue_list.append(interaction.user)
                self.queue_player_name = [user.global_name for user in self.queue_list]
                await interaction.response.send_message(content=f'Users currently in queue:'
                                                                f'{self.queue_player_name}')
                await interaction.response.send_message(content="You have joined the queue", ephemeral=True)
        else:
            await interaction.response.send_message(content="You cannot join the queue", ephemeral=True)

    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        if role in interaction.user.roles:
            self.queue_list.remove(interaction.user)
            self.queue_player_name.remove(interaction.user.global_name)
            await interaction.response.send_message(content=f'Users currently in queue:'
                                                            f'{self.queue_player_name}')
            await interaction.response.send_message(content="You have left the queue", ephemeral=True)
        else:
            await interaction.response.send_message(content="You aren't in the queue", ephemeral=True)


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


class UserChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Roles", emoji="📄", description="Update what your role preferences are"),
        discord.SelectOption(label="Players", emoji="👀", description="View a player based on their name or steam ID"),
        discord.SelectOption(label="Ladder", emoji="🪜", description="View player leaderboards (NOT WORKING YET)"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        match select.values[0]:
            case "Roles":
                if role in interaction.user.roles:
                    await interaction.response.send_message(
                        content="Please update your role preferences (select from top to bottom)",
                        view=setRoles.RolePreferenceSelect(), ephemeral=True)
                else:
                    await interaction.response.send_message(content="Please register before setting roles",
                                                            ephemeral=True)
            case "Players":
                await interaction.response.send_modal(PlayerViewModal())
            case "Ladder":
                await interaction.response.send_message(content="This feature has not yet been added", ephemeral=True,
                                                        delete_after=10)
            case "Refresh":
                await interaction.response.defer()


def check_user_exists(server, user_name):
    try:
        user_account = discord.utils.get(server.members, global_name=user_name)
        if user_account == None:
            user_account = discord.utils.get(server.members, name=user_name)
        user_in_database = dataManagement.check_for_value(user_account.id)
    except:
        user_in_database = False
        user_account = None
    return user_in_database, user_account

def load_token():
    with open('../../credentials/discord_token.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data['TOKEN']


def run_discord_bot():
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print('bot now running!')

    @bot.command()
    async def user(ctx):
        await ctx.send("New user? Please register here:", view=RegisterButton())
        await ctx.send("Already registered? Please choose from the below options", view=UserChoices())

    @bot.command()
    async def admin(ctx):
        await ctx.send("Admin options are below", view=AdminChoices())

    @bot.command()
    async def queue(ctx):
        await ctx.send("Click here to join the queue", view=InhouseQueue())

    @bot.command()
    async def clear(ctx):
        await ctx.channel.purge()

    bot.run(load_token())


if __name__ == '__main__':
    run_discord_bot()
