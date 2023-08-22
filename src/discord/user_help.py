import discord

class HelpButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click for help", emoji="❓",
                       style=discord.ButtonStyle.green)
    async def get_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(content="Help goes here", ephemeral=True, delete_after=10)
