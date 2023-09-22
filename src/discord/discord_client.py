import discord
from discord.ext import commands
import user_help
import initialisation
import data_management
import check_user
from os.path import isfile
from shutil import copyfile


def run_discord_bot():
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print('bot now running!')
        global server_list
        server_list = []
        for server in bot.guilds:
            if not isfile(f'../../data/{server.id}_config.yml'):
                copyfile(f'../../data/default_config.yml', f'../../data/{server.id}_config.yml')
            check_config = data_management.load_config_data(server, 'CONFIG', 'setup_complete')
            if check_config == 'Yes':
                server_list.append(await initialisation.run_user_modules(server))
            print(server_list)

    @bot.command()
    @commands.is_owner()
    async def setup(ctx):
        await ctx.send("Beginning setup of inhouse bot")
        await initialisation.ConfigButtons().config_start(ctx)

    # @bot.command()
    # async def refresh(ctx):
    #     check_config = data_management.load_config_data(ctx.guild, 'CONFIG', 'setup_complete')
    #     admin_role_id = data_management.load_config_data(ctx.guild, 'ROLES', 'admin_role')
    #     admin_role = discord.utils.get(ctx.guild.roles, id=admin_role_id)
    #     if check_config != 'Yes':
    #         await ctx.send(
    #             content="Config setup has not been completed. Please run !setup and follow the instructions to use this command")
    #     elif admin_role in ctx.author.roles:
    #         await initialisation.run_user_modules(ctx.guild)

    @bot.command()
    async def vk(ctx, user):
        chat_channel = data_management.load_config_data(ctx.guild, 'CHANNELS', 'chat_channel')
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return
        user_id = user[2:-1]
        user_acc = await ctx.guild.fetch_member(user_id)
        chosen_server = next((x for x in server_list if x.server == ctx.guild))
        if not chosen_server:
            await ctx.send(content=f'Commands are not yet working, please ensure setup has been completed and the bot has been restarted',
                           ephemeral=True)
        elif ctx.message.author not in chosen_server.queued_players:
            await ctx.send(content=f'You aren\'t in the queue!', ephemeral=True)
        elif len(chosen_server.queued_players) < 10:
            await ctx.send(content=f'Votekick can only be used when the queue is full', ephemeral=True)
        elif user_acc not in chosen_server.queued_players:
            await ctx.send(content=f'{user} isn\'t in the queue', ephemeral=True)
        else:
            await chosen_server.vote_kick(ctx.guild, user_acc, ctx.author, ctx.channel)

    @bot.command()
    async def wh(ctx, user):
        chat_channel = data_management.load_config_data(ctx.guild, 'CHANNELS', 'chat_channel')
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return
        user_id = user[2:-1]
        user_acc = await ctx.guild.fetch_member(user_id)
        user_check = check_user.registered_check(int(user_id))
        chosen_server = next((x for x in server_list if x.server == ctx.guild))
        if not chosen_server:
            await ctx.send(
                content=f'Commands are not yet working, please ensure setup has been completed and the bot has been restarted',
                ephemeral=True)
        elif not user_check:
            await ctx.send(content=f'{user_acc.display_name} not found', ephemeral=True)
        else:
            user_data = data_management.view_user_data(user_id)
            await ctx.send(embed=check_user.user_embed(user_data, user_acc, ctx.guild))

    @bot.command()
    async def register(ctx, dotabuff_id, mmr):
        print(dotabuff_id)
        print(mmr)
        chat_channel = data_management.load_config_data(ctx.guild, 'CHANNELS', 'chat_channel')
        registered_role_id = data_management.load_config_data(ctx.guild, 'ROLES', 'registered_role')
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return

    @bot.command()
    async def testing(ctx, chosen_string):
        user = next((x for x in ctx.guild.members if chosen_string.lower() in x.display_name.lower()))
        await ctx.send(user.display_name)

    @bot.command()
    # Used to post the help button, currently not being worked on (name to be amended)
    async def get_help(ctx):
        await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    # @bot.command()
    # @bot.is_owner()
    # # Used to clear the channel of text (helps de-clutter during testing)
    # async def clear(ctx):
    #     await ctx.channel.purge()

    bot.run(data_management.load_token())


if __name__ == '__main__':
    run_discord_bot()
