import discord
import check_user
import data_management


class AdminEmbed(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.data = []

    view_status = True
    current_page = 1
    sep = 10

    async def send_embed(self, ctx):
        self.create_register_list(ctx.guild)
        self.message = await ctx.send(view=self)
        await self.update_message(self.data, ctx.guild)

    def registered_embed(self, data_list, server, interaction):
        all_embed = discord.Embed(title='Registered users', description=f'Showing all registered users',
                                  color=0x00ff00)
        icon_url = server.icon.url
        all_embed.set_thumbnail(url=f'{icon_url}')
        for user in data_list:
            user_data = data_management.view_user_data(user.id)
            role = discord.utils.get(server.roles, name="verified")
            all_embed.add_field(name=user.global_name,
                                value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) | Roles: {user_data[3]} {user_data[4]} {user_data[5]} {user_data[6]} {user_data[7]}',
                                inline=False)
        all_embed.set_footer(text=f'last accessed by {interaction.user.global_name} at {interaction.created_at}')
        return all_embed

    def empty_embed(self, interaction):
        empty_embed = discord.Embed(title="No unverified users", description=f'There\'s nobody to verify!',
                                    color=0xFF0000)
        empty_embed.set_image(
            url=f'https://static.ffx.io/images/$width_620%2C$height_414/t_crop_fill/q_86%2Cf_auto/4cd67e7495a14e514c82a814124bf47e9390b7d9')
        if interaction:
            empty_embed.set_footer(text=f'last accessed by {interaction.user.global_name} at {interaction.created_at}')
        return empty_embed

    async def update_message(self, data, server, interaction=None):
        if self.view_status:
            self.update_buttons()
            if data:
                user = data[0]
                user_data = data_management.view_user_data(user.id)
                update_embed = check_user.user_embed(user_data, user, server)
                if interaction:
                    update_embed.set_footer(
                        text=f'last accessed by {interaction.user.global_name} at {interaction.created_at}')
                await self.message.edit(embed=update_embed, view=self)
            else:
                await self.message.edit(embed=self.empty_embed(interaction), view=self)
        else:
            role = discord.utils.get(server.roles, name="inhouse")
            user_list = []
            for user in role.members:
                user_list.append(user)
            self.update_buttons(len(user_list))
            user_list_page = self.get_current_page_data(user_list)
            await self.message.edit(embed=self.registered_embed(user_list_page, server, interaction), view=self)

    def update_register_list(self):
        registered_list = check_user.user_list("")
        if registered_list:
            for user in registered_list:
                self.data.append(user)
                check_user.user_list("Remove", user)

    def create_register_list(self, server):
        registered_users = discord.utils.get(server.roles, name="inhouse")
        vouched_users = discord.utils.get(server.roles, name="verified")
        for user in registered_users.members:
            if vouched_users not in user.roles and user not in self.data:
                self.data.append(user)

    def get_current_page_data(self, user_list):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        if self.current_page == int(len(user_list) / self.sep):
            from_item = self.current_page * self.sep - self.sep
            until_item = len(user_list)
        return user_list[from_item:until_item]

    def update_buttons(self, list_length=None):
        if self.view_status:
            self.verify_user.style = discord.ButtonStyle.green
            self.verify_user.label = "Verify User"
            self.verify_user.emoji = "✅"
            self.refresh_embed.style = discord.ButtonStyle.blurple
            self.refresh_embed.label = "Refresh"
            self.refresh_embed.emoji = "♻"
            self.reject_user.style = discord.ButtonStyle.red
            self.reject_user.label = "Reject User"
            self.reject_user.emoji = "❌"
            self.refresh_embed.disabled = False
            if not self.data:
                self.verify_user.disabled = True
                self.reject_user.disabled = True
            else:
                self.verify_user.disabled = False
                self.reject_user.disabled = False
        else:
            self.verify_user.style = discord.ButtonStyle.blurple
            self.verify_user.label = "Left"
            self.verify_user.emoji = "⬅"
            self.refresh_embed.style = discord.ButtonStyle.blurple
            self.refresh_embed.label = "Reset"
            self.refresh_embed.emoji = "↩"
            self.reject_user.style = discord.ButtonStyle.blurple
            self.reject_user.label = "Right"
            self.reject_user.emoji = "➡"
            self.change_embed.label = "View Unregistered Users"
            if list_length <= self.sep:
                self.verify_user.disabled = True
                self.refresh_embed.disabled = True
                self.reject_user.disabled = True
            elif self.current_page == 1:
                self.verify_user.disabled = True
                self.refresh_embed.disabled = True
                self.reject_user.disabled = False
            elif self.current_page >= (list_length / self.sep):
                self.reject_user.disabled = True
                self.verify_user.disabled = False
                self.refresh_embed.disabled = False
            else:
                self.verify_user.disabled = False
                self.refresh_embed.disabled = False

    @discord.ui.button(label="Verify User", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def verify_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if self.view_status:
            role = discord.utils.get(server.roles, name="verified")
            user_to_verify = self.data[0]
            await user_to_verify.add_roles(role)
            del self.data[0]
            self.update_register_list()
            await self.update_message(self.data, server, interaction)
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            self.current_page -= 1
            await self.update_message(self.data, server, interaction)

    @discord.ui.button(label="Refresh", emoji="♻",
                       style=discord.ButtonStyle.blurple)
    async def refresh_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if self.view_status:
            self.update_register_list()
            await self.update_message(self.data, server, interaction)
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            self.current_page = 1
            await self.update_message(self.data, server, interaction)

    @discord.ui.button(label="Reject User", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def reject_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if self.view_status:
            role = discord.utils.get(server.roles, name="inhouse")
            user_to_reject = self.data[0]
            await user_to_reject.remove_roles(role)
            del self.data[0]
            self.update_register_list()
            await self.update_message(self.data, server, interaction)
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            self.current_page += 1
            await self.update_message(self.data, server, interaction)

    @discord.ui.button(label="View Registered Users", emoji="📋",
                       style=discord.ButtonStyle.grey)
    async def change_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.view_status:
            self.view_status = False
            await self.update_message(self.data, interaction.guild, interaction)
            await interaction.response.defer()
        else:
            self.view_status = True
            await self.update_message(self.data, interaction.guild, interaction)
            await interaction.response.defer()
