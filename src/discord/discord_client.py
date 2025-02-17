import discord
from discord.ext import commands
import client_db_interface
import server_manager
from src.discord.bot_commands import Commands





class InhouseBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='!', intents=intents)
        self.server_manager = server_manager.ServerManager()

    async def on_ready(self):
        print('Bot now running!')
        for server in bot.guilds:
            if not client_db_interface.check_server_in_db(server):
                client_db_interface.add_server_to_db(server)
            if client_db_interface.check_server_settings(server):
                await self.server_manager.add_embeds(server)
        print('Channels loaded')
        await self.add_cog(Commands(self.server_manager))


bot = InhouseBot(discord.Intents.all())
bot.run(client_db_interface.get_discord_token())

# print(client_db_interface.count_users(1072625693185294407, "Verified"))
# print(client_db_interface.count_users(1072625693185294407, "Banned"))
# print(client_db_interface.load_server_settings(1072625693185294407))
