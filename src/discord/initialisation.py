import discord

class ConfigButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def config_start(self, ctx):
        with open("../../data/setup.txt", "r") as setup:
            self.setup_guide = setup.read().split("\n\n")
            await ctx.channel.send(self.setup_guide[0], view=self)

    @discord.ui.button(label="Automated Setup", emoji="😀",
                       style=discord.ButtonStyle.green)
    async def easy_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Help goes here", ephemeral=True, delete_after=10)

    @discord.ui.button(label="Mixed Setup", emoji="😀",
                       style=discord.ButtonStyle.green)
    async def mixed_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Help goes here", ephemeral=True, delete_after=10)

    @discord.ui.button(label="Manual setup", emoji="😀",
                       style=discord.ButtonStyle.green)
    async def full_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Help goes here", ephemeral=True, delete_after=10)
