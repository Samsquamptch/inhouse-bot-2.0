import discord
from discord.ext import commands
from src.discord import client_db_interface, check_user, initialisation


class Commands(discord.ext.commands.Cog, name='Greetings module'):
    def __init__(self, manager):
        self.manager = manager

    @commands.command()
    @commands.is_owner()
    async def setup(self, ctx):
        await self.manager.setup_command(ctx)

    @commands.command()
    async def refresh(self, ctx):
        await self.manager.remove_from_server_list(ctx)

    @commands.command(aliases=['vk'])
    async def votekick(self, ctx, user):
        if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
            return
        elif '<@' == user[0:2]:
            user_acc = await ctx.guild.fetch_member(user[2:-1])
        else:
            user_check, user_acc = check_user.user_exists(ctx.guild, user)
        chosen_server = next((x for x in self.manager.server_list if x.server == ctx.guild.id), None)
        if chosen_server is None:
            await ctx.send(content=f'Commands are not yet working, please ensure setup has been completed',
                           ephemeral=True)
        elif ctx.author not in chosen_server.inhouse.queued_players:
            await ctx.send(content=f'You aren\'t in the queue!', ephemeral=True)
        elif len(chosen_server.inhouse.queued_players) < 10:
            await ctx.send(content=f'Votekick can only be used when the queue is full', ephemeral=True)
        elif user_acc not in chosen_server.inhouse.queued_players:
            await ctx.send(content=f'{user} isn\'t in the queue', ephemeral=True)
        else:
            await chosen_server.inhouse.vote_kick(ctx.guild, user_acc, ctx.author, channel=ctx.channel)

    @commands.command(aliases=['wh', 'whois'])
    async def who(self, ctx, user=None):
        await self.manager.who_command(ctx, user)
        # if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
        #     return
        # elif user is None:
        #     user_acc = await ctx.guild.fetch_member(ctx.author.id)
        #     user_check = client_db_interface.check_discord_exists(ctx.author.id)
        # elif '<@' == user[0:2]:
        #     user_acc = await ctx.guild.fetch_member(user[2:-1])
        #     user_check = client_db_interface.check_discord_exists(int(user[2:-1]))
        # else:
        #     user_check, user_acc = check_user.user_exists(ctx.guild, user)
        # chosen_server = next((x for x in self.manager.server_list if x.server == ctx.guild.id), None)
        # if chosen_server is None:
        #     await ctx.send(
        #         content=f'Commands are not yet working, please ensure setup has been completed',
        #         ephemeral=True)
        # elif not user_check:
        #     await ctx.send(content=f'{user_acc.display_name} not found', ephemeral=True)
        # else:
        #     user_data = client_db_interface.view_user_data(user_acc.id)
        #     await ctx.send(embed=check_user.user_embed(user_data, user_acc, ctx.guild))


    @commands.command()
    async def register(self, ctx):
        return

    @commands.command()
    async def register(self, ctx, dotabuff_id: int, mmr: int):
        return
        # if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
        #     return
        # registered_role_id = client_db_interface.load_config_data(ctx.guild.id, 'ROLES', 'registered_role')
        # registered_role = discord.utils.get(ctx.guild.roles, id=registered_role_id)
        # disc_reg = client_db_interface.check_for_value("disc", ctx.author.id)
        # steam_reg = client_db_interface.check_for_value("steam", dotabuff_id)
        # if registered_role in ctx.author.roles or disc_reg:
        #     await ctx.send("Your discord account is already registered!")
        #     return
        # elif steam_reg:
        #     await ctx.send("Your steam account is already registered!")
        #     return
        # chosen_server = next((x for x in self.bot.server_list if x.server == ctx.guild.id), None)
        # if chosen_server is None:
        #     await ctx.send(
        #         content=f'Commands are not yet working, please ensure setup has been completed',
        #         ephemeral=True)
        # else:
        #     chosen_server.admin.unverified_list.append(ctx.author)
        #     await self.bot.register_command(ctx.author, dotabuff_id, mmr)
        #     await ctx.send("You have been registered. Please set your roles using !roles")

    @commands.command()
    async def stop_lobby(self, ctx):
        if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
            return
        if not client_db_interface.check_admin(ctx.author, ctx.guild):
            await ctx.send("Only admins are allowed to use this command")
            return
        else:
            client_db_interface.update_autolobby(ctx.guild.id, [0, 1])
            await ctx.send("Please wait for up to a minute for the queue to clear")

    @commands.command()
    async def start_lobby(self, ctx):
        if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
            return
        if not client_db_interface.check_admin(ctx.author, ctx.guild):
            await ctx.send("Only admins are allowed to use this command")
            return
        else:
            client_db_interface.update_autolobby(ctx.guild.id, [1, 1])
            await ctx.send("Please wait for up to a minute for the lobby to start")

    @commands.command()
    async def roles(self, ctx, pos1: int, pos2: int, pos3: int, pos4: int, pos5: int):
        if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
            return
        roles_list = [pos1, pos2, pos3, pos4, pos5]
        if not client_db_interface.user_registered(ctx.author, ctx.guild):
            await ctx.send("You need to register before you set your roles!")
            return
        elif not (all(x <= 5 for x in roles_list)) or not (all(x >= 1 for x in roles_list)):
            await ctx.send("Role preferences can only be between 1 (low) and 5 (high)")
            return
        client_db_interface.update_user_data(ctx.author.id, "roles", roles_list)
        await ctx.send("Thank you for updating your roles.")

    @register.error
    async def arg_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Please input your Dotabuff id and your MMR when using the register command. For example:"
                           f"```\n!register 28707060 2600```\n")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Please only input integer values for your Dotabuff ID and MMR.")
        else:
            await ctx.send(f"Something went wrong. Please try again.")

    @roles.error
    async def arg_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Please input your role preferences when using the roles command. If you wanted to play support, "
                           f"for example, you would enter:```\n!roles 1 1 1 5 5```\n")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"Please only input integer values for your Dotabuff ID and MMR.")
        else:
            await ctx.send(f"Something went wrong. Please try again.")

    @votekick.error
    async def arg_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Please input the user you wish to kick"
                f"```\n!vk Jam!```\n")
        else:
            await ctx.send(f"Something went wrong. Please try again.")

    @who.error
    async def arg_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"Please input the user you wish to look up"
                f"```\n!wh Jam!```\n")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"User is not registered with inhouse bot")
        else:
            await ctx.send(f"User not found, they probably aren't registered!")
