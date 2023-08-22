import discord
from discord.ext import commands
import admin_settings
import user_settings
import register_user
import user_help
import yaml
import inhouse_queue
from yaml.loader import SafeLoader


def load_token():
    with open('../../credentials/discord_token.yml') as f:
        data = yaml.load(f, Loader=SafeLoader)
    return data['TOKEN']


def run_discord_bot():
    intents = discord.Intents.all()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print('bot now running!')

    @bot.command()
    async def user(ctx):
        await ctx.send("New user? Please register here:", view=register_user.RegisterButton())
        await ctx.send("Already registered? Please choose from the below options", view=user_settings.UserChoices())

    @bot.command()
    async def admin(ctx):
        await ctx.send("Admin options are below", view=admin_settings.AdminChoices())

    @bot.command()
    async def queue(ctx):
        await ctx.send("Click here to join the queue", view=inhouse_queue.InhouseQueue())

    @bot.command()
    async def get_help(ctx):
        await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    @bot.command()
    async def clear(ctx):
        await ctx.channel.purge()

    bot.run(load_token())


if __name__ == '__main__':
    run_discord_bot()
