import discord
import data_management
import check_user
from datetime import datetime


class AdminKickPlayerModal(discord.ui.Modal, title='Kick User in Queue'):
    player_name = discord.ui.TextInput(label='User\'s global name or username')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        await interaction.response.defer()

class VoteKickPlayerModal(discord.ui.Modal, title='Votekick User in Queue'):
    player_name = discord.ui.TextInput(label='User\'s global name or username')

    async def on_submit(self, interaction: discord.Interaction):
        user_name = str(self.player_name)
        await interaction.response.defer()

class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.data = []

    async def send_embed(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.data, ctx.guild)

    def create_embed(self, data, server):
        if data:
            champions = discord.utils.get(server.roles, name="current champions")
            out = any(check in data for check in champions.members)
            if out:
                embed_desc = "A champion is in the queue!"
                embed_clr = 0xFFD700
            else:
                embed_desc = "People currently in the inhouse queue"
                embed_clr = 0x00ff00
        else:
            embed_desc = "Inhouse queue is currently empty"
            embed_clr = 0xFF0000
        queue_embed = discord.Embed(title="Inhouse queue", description=f'{embed_desc}',
                                    color=embed_clr)
        icon_url = server.icon.url
        queue_embed.set_thumbnail(url=f'{icon_url}')
        mmr_total = 0
        for user in data:
            user_data = data_management.view_user_data(user.id)
            mmr_total = mmr_total + user_data[2]
            role_preference = check_user.check_role_priority(user_data)
            queue_embed.add_field(name=user.global_name,
                                  value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) | Preference: {role_preference}',
                                  inline=False)
        update_time = datetime.now().strftime("%H:%M:%S")
        if data:
            average_mmr = mmr_total/len(data)
            queue_embed.set_footer(text=f'Queue updated at: {update_time} | Average MMR: {average_mmr}')
        else:
            queue_embed.set_footer(text=f'Queue updated at: {update_time}')
        return queue_embed

    async def update_message(self, data, server):
        await self.message.edit(embed=self.create_embed(data, server), view=self)

    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        verify = discord.utils.get(server.roles, name="verified")
        banned = discord.utils.get(server.roles, name="queue ban")
        if banned in interaction.user.roles:
            await interaction.response.send_message(content="You are currently banned from joining the queue", ephemeral=True, delete_after=5)
        else:
            if verify in interaction.user.roles:
                if interaction.user in self.data:
                    await interaction.response.send_message(content="You are already queued", ephemeral=True,
                                                            delete_after=5)
                else:
                    self.data.append(interaction.user)
                    await self.update_message(self.data, server)
                    await interaction.response.defer()
            else:
                await interaction.response.send_message(content="You cannot join the queue", ephemeral=True, delete_after=5)

    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        if interaction.user in self.data:
            self.data.remove(interaction.user)
            await self.update_message(self.data, server)
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content="You aren't in the queue", ephemeral=True, delete_after=5)

    @discord.ui.button(label="Kick User", emoji="🥾",
                       style=discord.ButtonStyle.blurple)
    async def kick_from_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        admin = discord.utils.get(server.roles, name="admin")
        if admin in interaction.user.roles:
            await interaction.response.send_modal(AdminKickPlayerModal())
        elif len(self.data) == 10 and interaction.user in self.data:
            await interaction.response.send_modal(VoteKickPlayerModal())
        else:
            await interaction.response.defer()
