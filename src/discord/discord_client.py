import discord
from discord.ext import commands, tasks
import user_help
import initialisation
import data_management
import team_balancer
from os.path import isfile
from shutil import copyfile
import pytz

def run_discord_bot():
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print('bot now running!')
        # for server in bot.guilds:
        #     if not isfile(f'../../data/{server.id}_config.yml'):
        #         print(f'No config file found for {server}')
        #     else:
        #         check_config = data_management.load_config_data(server, 'CONFIG', 'setup_complete')
        #         if check_config == 'Yes':
        #             await initialisation.run_user_modules(server)

    # @tasks.loop(seconds = 15)
    # async def test_stuff():
    #     utc = pytz.UTC
    #     server = discord.utils.get(bot.guilds, id=1072625693185294407)
    #     jam = discord.utils.get(server.members, id=215529156031545344)
    #     boo = discord.utils.get(server.members, id=181839327985139713)
    #     channel = discord.utils.get(server.channels, id=1149120451335962625)
    #     list = [jam, boo]
    #     for user in list:
    #         messages = [message async for message in channel.history(limit=100) if message.author.id == user.id]
    #         naive = messages[0].created_at.replace(tzinfo=None)
    #         print(naive)
    #         print(datetime.datetime.now()-datetime.timedelta(minutes=61))
    #         if naive < datetime.datetime.now(tz=None)-datetime.timedelta(minutes=61):
    #             print(f'{user} last message was older than 1 minute')
    #         else:
    #             print(f'{user} last message was newer than 1 minute')


    @bot.command()
    @commands.is_owner()
    async def setup(ctx):
        await ctx.send("Beginning setup of inhouse bot")
        if not isfile(f'../../data/{ctx.guild.id}_config.yml'):
            copyfile(f'../../data/default_config.yml', f'../../data/{ctx.guild.id}_config.yml')
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
    async def test(ctx):
        # list = [4620, 4250, 4000, 3888, 3700, 3150, 2900, 2540, 2260, 1840]
        # team_balancer.sort_balancer(list)
        list = [181839327985139713, 162236558529789963, 244038277106106369, 202441334726852608, 238402271849742336,
                367058803763445760, 303493411242115073, 270954490578862081, 242587573350957056, 202520217082003457]
        test = data_management.assign_teams(list)
        print(test[0])
        print(test[1])
        # # role_id = data_management.load_config_data(ctx.guild, 'ROLES', 'admin_role')
        # # notif_id = data_management.load_config_data(ctx.guild, 'CHANNELS', 'notification_channel')
        # # notif_channel = discord.utils.get(ctx.guild.channels, id=notif_id)
        # # await notif_channel.send(f'<@&{role_id}> user <@{ctx.author.id}> has registered for the inhouse')

    @bot.command()
    # Used to post the help button, currently not being worked on (name to be amended)
    async def get_help(ctx):
        await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    # Old commands which are no longer required
    # @bot.command()
    # # Used to post the admin panel and admin options menu
    # async def admin(ctx):
    #     verify_view = admin_panel.AdminEmbed()
    #     await verify_view.send_embed(ctx.channel, ctx.guild)
    #     await ctx.send("More options are available via the drop-down menu below", view=select_menus.AdminOptions())
    #
    # @bot.command()
    # # Used to post the regiser/view self/set roles buttons, additional user options, and inhouse queue
    # async def queue(ctx):
    #     await ctx.send("New user? Please register here:", view=register_user.RegisterButton())
    #     await ctx.send("Already registered? More options are available via the drop-down menu below",
    #                    view=select_menus.UserOptions())
    #     await inhouse_queue.InhouseQueue().send_embed(ctx.channel, ctx.guild)
    #
    # @bot.command()
    # # Used to clear the channel of text (helps de-clutter during testing)
    # async def clear(ctx):
    #     await ctx.channel.purge()

    # @bot.command()
    # async def check(ctx):

    bot.run(data_management.load_token())


if __name__ == '__main__':
    run_discord_bot()
