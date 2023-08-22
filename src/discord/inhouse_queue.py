import discord


class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    queue_list = []
    queue_player_name = []

    async def send_embed(self, ctx):
        embed = discord.Embed(title="Inhouse queue", description="People currently in the inhouse queue", color=0x00ff00)
        #for user in queue:
        #    embed.add_field(name=user.global_name, value=f'Username: {user.name}', inline=False)
        await ctx.send(embed=embed, view=self)

    async def update_message(self, data):
        self.update_buttons()

    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        server = interaction.user.guild
        role = discord.utils.get(server.roles, name="inhouse")
        if role in interaction.user.roles:
            if interaction.user in self.queue_list:
                await interaction.response.send_message(content="You are already queued", ephemeral=True)
            else:
                self.queue_list.append(interaction.user)
                #await interaction.response.send_message(embed=self.send_embed(server, self.queue_list))
                #self.queue_player_name = [user.global_name for user in self.queue_list]
                await self.send_embed(channel, self.queue_list)
                # await interaction.response.send_message(content=f'Users currently in queue:'
                #                                                 f'{self.queue_player_name}')
                await interaction.response.send_message(content="You have joined the queue", ephemeral=True)
        else:
            await interaction.response.send_message(content="You cannot join the queue", ephemeral=True)

    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        channel = interaction.channel
        if interaction.user in self.queue_list:
            self.queue_list.remove(interaction.user)
            #self.queue_player_name.remove(interaction.user.global_name)
            await self.send_embed(channel, self.queue_list)
            # await interaction.response.send_message(content=f'Users currently in queue:'
            #                                                 f'{self.queue_player_name}')
            await interaction.response.send_message(content="You have left the queue", ephemeral=True)
        else:
            await interaction.response.send_message(content="You aren't in the queue", ephemeral=True)
