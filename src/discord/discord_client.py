import discord
from discord.ext import commands
import initialisation
import client_db_interface
from src.discord.bot_commands import Commands


class InhouseBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='!', intents=intents)
        self.server_list = []

    async def on_ready(self):
        print('Bot now running!')
        for server in bot.guilds:
            if not client_db_interface.check_server_in_db(server):
                client_db_interface.add_server_to_db(server)
            if client_db_interface.check_server_settings(server):
                bot.server_list.append(await initialisation.run_user_modules(server))
        print('Channels loaded')
        await self.add_cog(Commands(self))

    async def register_command(self, user, dotabuff_id, mmr):
        return



token = client_db_interface.get_discord_token()
intents = discord.Intents.all()
intents.message_content = True
bot = InhouseBot(intents)

bot.run(token)

#
# intents = discord.Intents.all()
# intents.message_content = True
# discord_bot = DiscordClient(intents)
# discord_bot.run()

#
# if __name__ == '__main__':
#     run_discord_bot()
