import discord
from discord.ext import commands
import client_db_interface
from src.discord import admin_panel, select_menus, register_user, inhouse_queue
from src.discord.bot_commands import Commands


class ChannelList:
    def __init__(self, server):
        self.chat_channel = client_db_interface.load_chat_channel(server)
        self.admin_channel = client_db_interface.load_admin_channel(server)
        self.queue_channel = client_db_interface.load_queue_channel(server)
        self.global_channel = client_db_interface.load_global_channel(server)


class ServerViews:
    def __init__(self, server_id, inhouse_view, admin_view):
        super().__init__()
        self.server = server_id
        self.inhouse = inhouse_view
        self.admin = admin_view


class InhouseBot(commands.Bot):
    def __init__(self, intents):
        super().__init__(command_prefix='!', intents=intents)
        self.server_list = []
        self.bot_member = None

    async def on_ready(self):
        self.intents.message_content = True
        print('Bot now running!')
        for server in bot.guilds:
            if not client_db_interface.check_server_in_db(server):
                client_db_interface.add_server_to_db(server)
            if client_db_interface.check_server_settings(server):
                server_channels = ChannelList(server)
                await self.delete_messages(server, server_channels)
                await self.run_user_modules(server, server_channels)
        print('Channels loaded')
        await self.add_cog(Commands(self))

    async def register_command(self, user, dotabuff_id, mmr):
        return

    #TODO: Will need improving
    # Deletes all previous posts
    async def delete_messages(self, server, channel_list):
        message_id_list = client_db_interface.load_message_ids(server)
        if not message_id_list[0]:
            return
        i = 0
        while i < 2:
            bot_message = await channel_list.admin_channel.fetch_message(message_id_list[i])
            await bot_message.delete()
            i += 1
        while i < 5:
            bot_message = await channel_list.queue_channel.fetch_message(message_id_list[i])
            await bot_message.delete()
            i += 1


    async def run_user_modules(self, server, channels):
        # Send admin panel to admin channel
        admin_view = admin_panel.AdminEmbed(channels.chat_channel, channels.admin_channel, server)
        await admin_view.send_embed()
        admin_menu_message = await channels.admin_channel.send(
            "More options are available via the drop-down menu below",
            view=select_menus.AdminOptions())
        print("Admin settings created")
        # Send queue buttons and panel to queue channel
        register_view = register_user.RegisterEmbed(admin_view)
        register_message = await channels.queue_channel.send("New user? Please register here:", view=register_view)
        user_menu_message = await channels.queue_channel.send(
            "Already registered? More options are available via the drop-down menu below",
            view=select_menus.UserOptions(channels.chat_channel, server))
        queue_settings = client_db_interface.load_server_settings(server)
        inhouse_view = inhouse_queue.InhouseQueue(server, channels.chat_channel, channels.queue_channel,
                                                  queue_settings[0],
                                                  queue_settings[1], queue_settings[2], queue_settings[3])
        await inhouse_view.send_embed()
        print("User settings created")
        message_id_list = [admin_view.message.id, admin_menu_message.id, register_message.id, user_menu_message.id,
                           inhouse_view.message.id, 100]
        client_db_interface.update_message_ids(server, message_id_list)
        self.server_list.append(ServerViews(server.id, inhouse_view, admin_view))


bot = InhouseBot(discord.Intents.all())
bot.run(client_db_interface.get_discord_token())
