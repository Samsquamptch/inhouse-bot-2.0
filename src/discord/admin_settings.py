import discord
import check_user
import data_management

class VerifyMenu(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def send_embed(self, ctx):
        self.update_register_list(ctx.guild)
        self.message = await ctx.send(view=self)
        await self.update_message(self.data, ctx.guild)

    def empty_embed(self):
        empty_embed = discord.Embed(title="No unverified users", description=f'There\'s nobody to verify!',
                                    color=0xFF0000)
        empty_embed.set_image(url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')
        return empty_embed

    async def update_message(self, data, server):
        self.update_buttons()
        if data:
            user = data[0]
            user_data = data_management.view_user_data(user.id)
            await self.message.edit(embed=check_user.user_embed(user_data, user, server), view=self)
        else:
            await self.message.edit(embed=self.empty_embed(), view=self)

    def update_register_list(self, server):
        registered_users = discord.utils.get(server.roles, name="inhouse")
        vouched_users = discord.utils.get(server.roles, name="verified")
        for user in registered_users.members:
            if vouched_users not in user.roles and user not in self.data:
                self.data.append(user)

    def update_buttons(self):
        if not self.data:
            self.verify_user.disabled = True
            self.reject_user.disabled = True
        else:
            self.verify_user.disabled = False
            self.reject_user.disabled = False

    @discord.ui.button(label="Verify User", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def verify_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="verified")
        user_to_verify = self.data[0]
        await user_to_verify.add_roles(role)
        del self.data[0]
        await self.update_message(self.data, server)
        await interaction.response.defer()

    @discord.ui.button(label="Refresh", emoji="♻️",
                       style=discord.ButtonStyle.blurple)
    async def refresh_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        self.update_register_list(server)
        await self.update_message(self.data, server)
        await interaction.response.defer()


    @discord.ui.button(label="Reject User", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def reject_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        user_to_reject = self.data[0]
        await user_to_reject.remove_roles(role)
        del self.data[0]
        await self.update_message(self.data, server)
        await interaction.response.defer()


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

    def registered_embed(self, data_list, server):
        all_embed = discord.Embed(title='Registered users', description=f'Showing all registered users',
                                  color=0x00ff00)
        icon_url = server.icon.url
        all_embed.set_thumbnail(url=f'{icon_url}')
        for user in data_list:
            user_data = data_management.view_user_data(user.id)
            role = discord.utils.get(server.roles, name="verified")
            if role in user.roles:
                verified_status = "Yes"
            else:
                verified_status = "No"
            all_embed.add_field(name=user.global_name,
                                value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) | Verified: {verified_status})',
                                inline=False)
        return all_embed

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        server = interaction.user.guild
        if user_name == "all":
            role = discord.utils.get(server.roles, name="inhouse")
            user_list = []
            for user in role.members:
                user_list.append(user)
            user = interaction.user
            await user.send(embed=self.registered_embed(user_list, server))
            await interaction.response.defer()
            # await interaction.response.send_message(embed=self.registered_embed(user_list, server), ephemeral=True)
        else:
            check_if_exists = check_user.user_exists(server, user_name)
            if check_if_exists[0]:
                user_data = data_management.view_user_data(check_if_exists[1].id)
                await interaction.response.send_message(embed=check_user.user_embed(user_data, check_if_exists[1], server),
                                                        ephemeral=True)
                await interaction.response.defer()
            else:
                await interaction.response.send_message(content=f'User {user_name} is not registered', ephemeral=True,
                                                        delete_after=10)
                await interaction.response.defer()


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
        discord.SelectOption(label="Edit", emoji="🖊️", description="Edit a user's details and status"),
        discord.SelectOption(label="View", emoji="👀", description="View all registered or a specific user"),
        discord.SelectOption(label="Remove", emoji="❌", description="Delete a registered user"),
        discord.SelectOption(label="Refresh", emoji="♻", description="Select to allow you to refresh options")
    ]
                       )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        match select.values[0]:
            case "Edit":
                await interaction.response.send_modal(EditUserModal())
            case "View":
                await interaction.response.send_modal(ViewUsersModal())
            case "Remove":
                await interaction.response.send_modal(RemoveUserModal())
            case "Refresh":
                await interaction.response.defer()
