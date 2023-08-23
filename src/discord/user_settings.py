import discord
import set_roles
import check_user
import data_management

class PlayerViewModal(discord.ui.Modal, title='View Player '):
    player_name = discord.ui.TextInput(label='Player name')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        check_if_exists = check_user.user_exists(server, user_name)
        if check_if_exists[0]:
            user_data = data_management.view_user_data(check_if_exists[1].id)
            await interaction.response.send_message(embed=check_user.user_embed(user_data, check_if_exists[1], server),
                                                    ephemeral=True)
        else:
            await interaction.response.send_message(f'User {self.player_name} not in database', ephemeral=True,
                                                    delete_after=10)


class UserChoices(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select an action here", min_values=1, max_values=1, options=[
        discord.SelectOption(label="Roles", emoji="📄", description="Update what your role preferences are"),
        discord.SelectOption(label="Players", emoji="👀", description="View a registered user based on their name"),
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
                        content="Please update your role preferences",
                        view=set_roles.RolePreferenceSelect(), ephemeral=True)
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
