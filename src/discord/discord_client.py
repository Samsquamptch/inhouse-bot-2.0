import discord
from discord.ext import commands, tasks
import user_help
import initialisation
import data_management
from os.path import isfile
from shutil import copyfile


def run_discord_bot():
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print('bot now running!')
        for server in bot.guilds:
            if not isfile(f'../../data/{server.id}_config.yml'):
                copyfile(f'../../data/default_config.yml', f'../../data/{server.id}_config.yml')
            check_config = data_management.load_config_data(server, 'CONFIG', 'setup_complete')
            if check_config == 'Yes':
                await initialisation.run_user_modules(server)

    @bot.command()
    @commands.is_owner()
    async def setup(ctx):
        await ctx.send("Beginning setup of inhouse bot")
        await initialisation.ConfigButtons().config_start(ctx)

    @bot.command()
    async def refresh(ctx):
        check_config = data_management.load_config_data(ctx.guild, 'CONFIG', 'setup_complete')
        admin_role_id = data_management.load_config_data(ctx.guild, 'ROLES', 'admin_role')
        admin_role = discord.utils.get(ctx.guild.roles, id=admin_role_id)
        if check_config != 'Yes':
            await ctx.send(
                content="Config setup has not been completed. Please run !setup and follow the instructions to use this command")
        elif admin_role in ctx.author.roles:
            await initialisation.run_user_modules(ctx.guild)

    @bot.command()
    # Used to post the help button, currently not being worked on (name to be amended)
    async def get_help(ctx):
        await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    @bot.command()
    # Used to clear the channel of text (helps de-clutter during testing)
    async def clear(ctx):
        await ctx.channel.purge()

    bot.run(data_management.load_token())


if __name__ == '__main__':
    run_discord_bot()
