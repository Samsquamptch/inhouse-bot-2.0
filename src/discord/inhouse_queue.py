import discord
import data_management


class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def send_embed(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.data, ctx.guild)

    def create_embed(self, data, server):
        if data:
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
            queue_embed.add_field(name=user.global_name,
                                  value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]})',
                                  inline=False)
        if data:
            average_mmr = mmr_total/len(data)
            queue_embed.set_image(url=f'{data[-1].avatar}')
            queue_embed.set_footer(text=f'Average MMR: {average_mmr}')
        return queue_embed

    async def update_message(self, data, server):
        await self.message.edit(embed=self.create_embed(data, server), view=self)

    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="verified")
        if role in interaction.user.roles:
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
