import discord
from discord.ext import commands
import file_loader

class Commands(discord.ext.commands.Cog, name='Commands module'):
    def __init__(self, manager):
        self.manager = manager

    @commands.command()
    @commands.is_owner()
    async def setup(self, ctx):
        await self.manager.setup_command(ctx)

    @commands.command()
    async def refresh(self, ctx):
        await self.manager.refresh_command(ctx)

    @commands.command()
    async def post_message(self, ctx):
        image = file_loader.load_setup_image()
        await ctx.send(file=discord.File(image))

    @commands.command()
    async def stop_lobby(self, ctx):
        await self.manager.stop_lobby_command(ctx)
