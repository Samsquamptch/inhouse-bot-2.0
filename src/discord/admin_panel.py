import discord
import check_user
import data_management


class AdminEmbed(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.unverified_list = []
        self.roles_id = None
        self.message = None

    view_status = True
    current_page = 1
    # Sep variable must be kept below 25 as embed fields limit is 25
    sep = 10

    async def send_embed(self, channel, server):
        self.create_register_list(server)
        self.message = await channel.send(view=self)
        await self.update_message(self.unverified_list, server)

    def registered_embed(self, data_list, server, interaction):
        all_embed = discord.Embed(title='Registered users', description=f'Showing all registered users',
                                  color=0x00ff00)
        icon_url = server.icon.url
        all_embed.set_thumbnail(url=f'{icon_url}')
        for user in data_list:
            user_data = data_management.view_user_data(user.id)
            # Due to how the role balancer calculations work, number weighting is saved the opposite to how users are used to
            # (which is higher number = more pref and lower number = less pref). This swap shows what users expect to see,
            # instead of what is actually happening behind the scenes (low num = more pref and high num = less pref)
            data_numbers = [3, 4, 5, 6, 7]
            for n in data_numbers:
                match user_data[n]:
                    case 1:
                        user_data[n] = 5
                    case 2:
                        user_data[n] = 4
                    case 3:
                        user_data[n] = 3
                    case 4:
                        user_data[n] = 2
                    case 5:
                        user_data[n] = 1
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

    async def update_message(self, list_data, server, interaction=None):
        if self.view_status:
            self.update_buttons()
            if list_data:
                user = list_data[0]
                user_data = data_management.view_user_data(user.id)
                update_embed = check_user.user_embed(user_data, user, server)
                if interaction:
                    update_embed.set_footer(
                        text=f'last accessed by {interaction.user.global_name} at {interaction.created_at}')
                await self.message.edit(embed=update_embed, view=self)
            else:
                await self.message.edit(embed=self.empty_embed(interaction), view=self)
        else:
            role_inhouse = discord.utils.get(server.roles, id=self.roles_id['registered_role'])
            user_list = [user for user in role_inhouse.members]
            self.update_buttons(len(user_list))
            user_list_page = self.get_current_page_data(user_list)
            await self.message.edit(embed=self.registered_embed(user_list_page, server, interaction), view=self)

    def update_register_list(self):
        registered_list = check_user.user_list("")
        if registered_list:
            for user in registered_list:
                self.unverified_list.append(user)
                check_user.user_list("Remove", user)

    def create_register_list(self, server):
        role_inhouse = discord.utils.get(server.roles, id=self.roles_id['registered_role'])
        role_verified = discord.utils.get(server.roles, id=self.roles_id['verified_role'])
        self.unverified_list = [user for user in role_inhouse.members if role_verified not in user.roles]

    def get_current_page_data(self, user_list):
        until_item = self.current_page * self.sep
        from_item = until_item - self.sep
        if self.current_page == 1:
            from_item = 0
            until_item = self.sep
        elif self.current_page == int(len(user_list) / self.sep):
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
            self.change_embed.label = "View Registered Users"
            if not self.unverified_list:
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
            self.change_embed.label = "View Unverified Users"
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
            notif_id = data_management.load_config_data(server, 'CHANNELS', 'notification_channel')
            notif_channel = discord.utils.get(server.channels, id=notif_id)
            role_verified = discord.utils.get(server.roles, id=self.roles_id['verified_role'])
            user_to_verify = self.unverified_list[0]
            await user_to_verify.add_roles(role_verified)
            await notif_channel.send(f'User <@{self.unverified_list[0].id}> has been verified for the inhouse')
            del self.unverified_list[0]
            self.update_register_list()
            await self.update_message(self.unverified_list, server, interaction)
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            self.current_page -= 1
            await self.update_message(self.unverified_list, server, interaction)

    @discord.ui.button(label="Refresh", emoji="♻",
                       style=discord.ButtonStyle.blurple)
    async def refresh_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if self.view_status:
            self.update_register_list()
            await self.update_message(self.unverified_list, server, interaction)
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            self.current_page = 1
            await self.update_message(self.unverified_list, server, interaction)

    @discord.ui.button(label="Reject User", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def reject_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if self.view_status:
            role_inhouse = discord.utils.get(server.roles, id=self.roles_id['registered_role'])
            user_to_reject = self.unverified_list[0]
            await user_to_reject.remove_roles(role_inhouse)
            del self.unverified_list[0]
            self.update_register_list()
            await self.update_message(self.unverified_list, server, interaction)
            await interaction.response.defer()
        else:
            await interaction.response.defer()
            self.current_page += 1
            await self.update_message(self.unverified_list, server, interaction)

    @discord.ui.button(label="View Registered Users", emoji="📋",
                       style=discord.ButtonStyle.grey)
    async def change_embed(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.view_status:
            self.view_status = False
            await self.update_message(self.unverified_list, interaction.guild, interaction)
            await interaction.response.defer()
        else:
            self.view_status = True
            self.update_register_list()
            await self.update_message(self.unverified_list, interaction.guild, interaction)
            await interaction.response.defer()
