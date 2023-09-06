import discord
from discord.ext import commands
import admin_panel
import select_menus
import register_user
import user_help
import inhouse_queue
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

    @bot.command()
    @commands.is_owner()
    async def setup(ctx):
        await ctx.send("Beginning setup of inhouse bot")
        if not isfile(f'../../data/{ctx.guild.id}_config.yml'):
            copyfile(f'../../data/default_config.yml', f'../../data/{ctx.guild.id}_config.yml')
        await initialisation.ConfigButtons().config_start(ctx)

    @bot.command()
    async def run(ctx):
        check_config = data_management.load_config_data(ctx, 'CONFIG', 'setup_complete')
        admin_role_id = data_management.load_config_data(ctx, 'ROLES', 'admin_role')
        admin_role = discord.utils.get(ctx.guild.roles, id=admin_role_id)
        if check_config != 'Yes':
            await ctx.send(
                content="Config setup has not been completed. Please run !setup and follow the instructions to use this command")
        elif admin_role in ctx.author.roles:
            admin_channel_id = data_management.load_config_data(ctx, 'CHANNELS', 'admin_channel')
            queue_channel_id = data_management.load_config_data(ctx, 'CHANNELS', 'queue_channel')
            admin_channel = discord.utils.get(ctx.guild.channels, id=admin_channel_id)
            queue_channel = discord.utils.get(ctx.guild.channels, id=queue_channel_id)
            # Send admin panel to admin channel
            verify_view = admin_panel.AdminEmbed()
            await verify_view.send_embed(admin_channel, ctx.guild)
            await admin_channel.send("More options are available via the drop-down menu below",
                                     view=select_menus.AdminOptions())
            # Send queue buttons and panel to queue channel
            await queue_channel.send("New user? Please register here:", view=register_user.RegisterButton())
            await queue_channel.send("Already registered? More options are available via the drop-down menu below",
                                     view=select_menus.UserOptions())
            await inhouse_queue.InhouseQueue().send_embed(queue_channel, ctx.guild)

    @bot.command()
    # Used to post the admin panel and admin options menu
    async def admin(ctx):
        verify_view = admin_panel.AdminEmbed()
        await verify_view.send_embed(ctx.channel, ctx.guild)
        await ctx.send("More options are available via the drop-down menu below", view=select_menus.AdminOptions())

    @bot.command()
    # Used to post the regiser/view self/set roles buttons, additional user options, and inhouse queue
    async def queue(ctx):
        await ctx.send("New user? Please register here:", view=register_user.RegisterButton())
        await ctx.send("Already registered? More options are available via the drop-down menu below",
                       view=select_menus.UserOptions())
        await inhouse_queue.InhouseQueue().send_embed(ctx.channel, ctx.guild)

    @bot.command()
    # Used to post the help button, currently not being worked on (name to be amended)
    async def get_help(ctx):
        await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    @bot.command()
    # Used to clear the channel of text (helps de-clutter during testing
    # TODO comment this out when ready for production
    async def clear(ctx):
        await ctx.channel.purge()

    # @bot.command()
    # async def check(ctx):

    bot.run(data_management.load_token())


if __name__ == '__main__':
    run_discord_bot()
