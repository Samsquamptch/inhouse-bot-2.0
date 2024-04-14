import discord
from discord.ext import commands
import initialisation
import data_management
import check_user
import register_user
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
            if not isfile(f'../../data/inhouse_{server.id}.db'):
                data_management.initialise_database(server)
            if not isfile(f'../../data/{server.id}_config.yml'):
                copyfile(f'../../data/default_config.yml', f'../../data/{server.id}_config.yml')
            check_config = data_management.load_config_data(server.id, 'CONFIG', 'setup_complete')
            if check_config == 'Yes':
                server_list.append(await initialisation.run_user_modules(server))

    @bot.command()
    @commands.is_owner()
    async def setup(ctx):
        await ctx.send("Beginning setup of inhouse bot")
        await initialisation.ConfigButtons().config_start(ctx)

    @bot.command(aliases=['vk'])
    async def votekick(ctx, user):
        chat_channel = data_management.load_config_data(ctx.guild.id, 'CHANNELS', 'chat_channel')
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return
        elif '<@' == user[0:2]:
            user_acc = await ctx.guild.fetch_member(user[2:-1])
        else:
            user_check, user_acc = check_user.user_exists(ctx.guild, user)
        chosen_server = next((x for x in server_list if x.server == ctx.guild.id), None)
        if chosen_server is None:
            await ctx.send(content=f'Commands are not yet working, please ensure setup has been completed and the bot has been restarted',
                           ephemeral=True)
        elif ctx.author not in chosen_server.inhouse.queued_players:
            await ctx.send(content=f'You aren\'t in the queue!', ephemeral=True)
        elif len(chosen_server.inhouse.queued_players) < 10:
            await ctx.send(content=f'Votekick can only be used when the queue is full', ephemeral=True)
        elif user_acc not in chosen_server.inhouse.queued_players:
            await ctx.send(content=f'{user} isn\'t in the queue', ephemeral=True)
        else:
            await chosen_server.inhouse.vote_kick(ctx.guild, user_acc, ctx.author, channel=ctx.channel)

    @bot.command(aliases=['wh', 'whois'])
    async def who(ctx, user=None):
        chat_channel = data_management.load_config_data(ctx.guild.id, 'CHANNELS', 'chat_channel')
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return
        elif user is None:
            user_acc = await ctx.guild.fetch_member(ctx.author.id)
            user_check = data_management.check_for_value("disc", ctx.author.id, ctx.guild)
        elif '<@' == user[0:2]:
            user_acc = await ctx.guild.fetch_member(user[2:-1])
            user_check = data_management.check_for_value("disc", int(user[2:-1]), ctx.guild)
        else:
            user_check, user_acc = check_user.user_exists(ctx.guild, user)
        chosen_server = next((x for x in server_list if x.server == ctx.guild.id), None)
        if chosen_server is None:
            await ctx.send(
                content=f'Commands are not yet working, please ensure setup has been completed and the bot has been restarted',
                ephemeral=True)
        elif not user_check:
            await ctx.send(content=f'{user_acc.display_name} not found', ephemeral=True)
        else:
            user_data = data_management.view_user_data(user_acc.id, ctx.guild)
            await ctx.send(embed=check_user.user_embed(user_data, user_acc, ctx.guild))

    @bot.command()
    async def register(ctx, dotabuff_id: int, mmr: int):
        chat_channel = data_management.load_config_data(ctx.guild.id, 'CHANNELS', 'chat_channel')
        registered_role_id = data_management.load_config_data(ctx.guild.id, 'ROLES', 'registered_role')
        registered_role = discord.utils.get(ctx.guild.roles, id=registered_role_id)
        disc_reg = data_management.check_for_value("disc", ctx.author.id, ctx.guild)
        steam_reg = data_management.check_for_value("steam", dotabuff_id, ctx.guild)
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return
        elif registered_role in ctx.author.roles or disc_reg:
            await ctx.send("Your discord account is already registered!")
            return
        elif steam_reg:
            await ctx.send("Your steam account is already registered!")
            return
        chosen_server = next((x for x in server_list if x.server == ctx.guild.id), None)
        if chosen_server is None:
            await ctx.send(
                content=f'Commands are not yet working, please ensure setup has been completed and the bot has been restarted',
                ephemeral=True)
        else:
            chosen_server.admin.unverified_list.append(ctx.author)
            await register_user.register(ctx.author, dotabuff_id, mmr, ctx.guild)
            await ctx.send("You have been registered. Please set your roles using !roles")

    #Use this if the bot is being updated from an older version to a newer one (post database).
    #This initialises the missing tables (one is useless, the other needed for autolobby)
    @bot.command()
    @commands.is_owner()
    async def forward_assist(ctx):
        data_management.initialise_database(ctx.guild)

    @bot.command()
    @commands.is_owner()
    async def stop_lobby(ctx):
        data_management.update_autolobby(ctx.guild.id, [0, 1])

    # @bot.command(aliases=['reset'])
    # @commands.is_owner()
    # async def clear_roles(ctx):
    #     role_id = data_management.load_config_data(ctx.guild, 'ROLES')
    #     registered_role = discord.utils.get(ctx.guild.roles, id=role_id['registered_role'])
    #     verified_role = discord.utils.get(ctx.guild.roles, id=role_id['verified_role'])
    #     user_list = [x for x in ctx.guild.members if verified_role in x.roles]
    #     for user in user_list:
    #         print(user.display_name)
    #         await user.remove_roles(verified_role)
    #         await user.remove_roles(registered_role)
    #     await ctx.send("roles cleared")

    @bot.command()
    async def roles(ctx, pos1: int, pos2: int, pos3: int, pos4: int, pos5: int):
        chat_channel = data_management.load_config_data(ctx.guild.id, 'CHANNELS', 'chat_channel')
        registered_role_id = data_management.load_config_data(ctx.guild.id, 'ROLES', 'registered_role')
        registered_role = discord.utils.get(ctx.guild.roles, id=registered_role_id)
        roles_list = [pos1, pos2, pos3, pos4, pos5]
        if ctx.channel != discord.utils.get(ctx.guild.channels, id=chat_channel):
            return
        elif not registered_role:
            await ctx.send("You need to register before you set your roles!")
            return
        elif not (all(x <= 5 for x in roles_list)) or not (all(x >= 1 for x in roles_list)):
            await ctx.send("Role preferences can only be between 1 (low) and 5 (high)")
            return
        roles_list = check_user.flip_values(roles_list, True)
        data_management.update_user_data(ctx.author.id, "roles", roles_list, ctx.guild)
        await ctx.send("Thank you for updating your roles.")

    @register.error
    async def arg_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Please input your Dotabuff id and your MMR when using the register command. For example:"
                           f"```\n!register 28707060 2600```\n")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Please only input integer values for your Dotabuff ID and MMR.")
        else:
            await ctx.send(f"Something went wrong. Please try again.")

    @roles.error
    async def arg_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Please input your role preferences when using the roles command. If you wanted to play support, "
                           f"for example, you would enter:```\n!roles 1 1 1 5 5```\n")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Please only input integer values for your Dotabuff ID and MMR.")
        else:
            await ctx.send(f"Something went wrong. Please try again.")

    @votekick.error
    async def arg_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Please input the user you wish to kick"
                f"```\n!vk Jam!```\n")
        else:
            await ctx.send(f"Something went wrong. Please try again.")

    @who.error
    async def arg_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Please input the user you wish to look up"
                f"```\n!wh Jam!```\n")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"User is not registered with inhouse bot")
        else:
            await ctx.send(f"User not found, they probably aren't registered!")

    # @bot.command()
    # # Used to post the help button, currently not being worked on (name to be amended)
    # async def get_help(ctx):
    #     await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    bot.run(data_management.discord_credentials('TOKEN'))

run_discord_bot()

#
# if __name__ == '__main__':
#     run_discord_bot()
