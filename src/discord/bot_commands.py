import discord
from discord.ext import commands
from src.discord import client_db_interface, validate_user


class Commands(discord.ext.commands.Cog, name='Commands module'):
    def __init__(self, manager):
        self.manager = manager

    @commands.command()
    @commands.is_owner()
    async def setup(self, ctx):
        await self.manager.setup_command(ctx)

    @commands.command()
    async def refresh(self, ctx):
        await self.manager.remove_from_server_list(ctx)

    # @commands.command()
    # async def stop_lobby(self, ctx):
    #     if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
    #         return
    #     if not client_db_interface.check_admin(ctx.author, ctx.guild):
    #         await ctx.send("Only admins are allowed to use this command")
    #         return
    #     else:
    #         client_db_interface.update_autolobby(ctx.guild.id, [0, 1])
    #         await ctx.send("Please wait for up to a minute for the queue to clear")
    #
    # @commands.command()
    # async def start_lobby(self, ctx):
    #     if ctx.channel != client_db_interface.load_chat_channel(ctx.guild):
    #         return
    #     if not client_db_interface.check_admin(ctx.author, ctx.guild):
    #         await ctx.send("Only admins are allowed to use this command")
    #         return
    #     else:
    #         client_db_interface.update_autolobby(ctx.guild.id, [1, 1])
    #         await ctx.send("Please wait for up to a minute for the lobby to start")

