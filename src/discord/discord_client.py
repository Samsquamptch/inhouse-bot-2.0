import discord
from discord.ext import commands
import admin_panel
import select_menus
import register_user
import user_help
import yaml
import inhouse_queue
import data_management
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

    # @bot.command()
    # async def user(ctx):
    #     await ctx.send("New user? Please register here:", view=register_user.RegisterButton())
    #     await ctx.send("Already registered? Please choose from the below options", view=user_settings.UserChoices())

    @bot.command()
    # Used to post the admin panel and admin options menu
    async def admin(ctx):
        verify_view = admin_panel.AdminEmbed()
        await verify_view.send_embed(ctx)
        await ctx.send("More options are available via the drop-down menu below", view=select_menus.AdminOptions())

    @bot.command()
    # Used to post the regiser/view self/set roles buttons, additional user options, and inhouse queue
    async def queue(ctx):
        await ctx.send("New user? Please register here:", view=register_user.RegisterButton())
        await ctx.send("Already registered? More options are available via the drop-down menu below", view=select_menus.UserOptions())
        await inhouse_queue.InhouseQueue().send_embed(ctx)

    @bot.command()
    # Used to post the help button, currently not being worked on (name to be amended)
    async def get_help(ctx):
        await ctx.send("Require assistance? Check our help options", view=user_help.HelpButton())

    @bot.command()
    # Used to clear the channel of text (helps de-clutter during testing
    # TODO comment this out when ready for production
    async def clear(ctx):
        await ctx.channel.purge()

    @bot.command()
    async def check(ctx):
        queue_ids = [259370592984104960,367058803763445760,1070100769853943859,
                     376102816151896065,458993646012858368,230389532728492033,
                     206843167394365440,270954490578862081,128653806723530753,119172828867067906]
        test_data = data_management.queue_pop(queue_ids)
        print("Team 1")
        for i in test_data[0]:
            print(i)
        print("Team 2")
        for j in test_data[1]:
            print(j)
        # print(message.id)

    bot.run(load_token())

if __name__ == '__main__':
    run_discord_bot()
