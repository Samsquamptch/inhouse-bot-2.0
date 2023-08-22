import discord


class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def send_embed(self, ctx):
        self.message = await ctx.send(view=self)
        await self.update_message(self.data)

    def create_embed(self, data):
        queue_embed = discord.Embed(title="Inhouse queue", description="People currently in the inhouse queue",
                                    color=0x00ff00)
        queue_embed.set_thumbnail(url="https://riki.dotabuff.com/leagues/14994/banner.png")
        counter = 0
        for user in data:
            if counter == 5:
                queue_embed.add_field(name="\u200B", value="\u200B")
            queue_embed.add_field(name=user.global_name, value=f'Username: {user.name}', inline=True)
            counter += 1
        return queue_embed

    async def update_message(self, data):
        await self.message.edit(embed=self.create_embed(data), view=self)

    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        if role in interaction.user.roles:
            if interaction.user in self.data:
                await interaction.response.send_message(content="You are already queued", ephemeral=True,
                                                        delete_after=5)
            else:
                self.data.append(interaction.user)
                await self.update_message(self.data)
                # await self.send_embed(channel, self.queue_list)
                # await interaction.response.send_message(content=f'Users currently in queue:'
                #                                                 f'{self.queue_player_name}')
                await interaction.response.send_message(content="You have joined the queue", ephemeral=True,
                                                        delete_after=5)
        else:
            await interaction.response.send_message(content="You cannot join the queue", ephemeral=True, delete_after=5)

    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        channel = interaction.channel
        if interaction.user in self.data:
            self.data.remove(interaction.user)
            await self.update_message(self.data)
            # await interaction.response.send_message(content=f'Users currently in queue:'
            #                                                 f'{self.queue_player_name}')
            await interaction.response.send_message(content="You have left the queue", ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message(content="You aren't in the queue", ephemeral=True, delete_after=5)
