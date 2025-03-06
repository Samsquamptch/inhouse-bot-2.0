import discord
from discord.ext import commands
import client_db_interface
from server_manager import ServerManager
from src.discord.bot_commands import Commands
from src.discord.queue_manager import QueueManager


class DiscordBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='/', intents=intents)
        self.server_manager = ServerManager(QueueManager())

    async def on_ready(self):
        print('Bot now running!')
        for server in bot.guilds:
            if not client_db_interface.check_server_in_db(server):
                client_db_interface.add_server_to_db(server)
            if client_db_interface.check_server_settings(server):
                await self.server_manager.add_embeds(server)
        print('Channels loaded')
        await self.add_cog(Commands(self.server_manager))
        self.server_manager.start_check_loop()


bot = DiscordBot(discord.Intents.all())
bot.run(client_db_interface.get_discord_token())

