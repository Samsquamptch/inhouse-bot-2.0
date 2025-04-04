import admin_panel
import menu_admin_options
import register_user
import client_db_interface
import inhouse_queue
import initialisation
import menu_user_options
from src.discord.embed_superclass import AdminPanelUserList
from src.discord.embed_views import AdminEmbedView, UserEmbed, QueueEmbedView


class ChannelList:
    def __init__(self, server):
        self.chat_channel = client_db_interface.load_chat_channel(server)
        self.admin_channel = client_db_interface.load_admin_channel(server)
        self.queue_channel = client_db_interface.load_queue_channel(server)
        self.global_channel = client_db_interface.load_global_channel(server)


class ServerEmbeds:
    def __init__(self, server, inhouse_view, admin_view, admin_menu, user_menu, register_view):
        super().__init__()
        self.server = server.id
        self.chat_channel = client_db_interface.load_chat_channel(server)
        self.inhouse_queue = inhouse_view
        self.admin_panel = admin_view
        self.admin_menu = admin_menu
        self.user_menu = user_menu
        self.register_buttons = register_view


class ServerManager:
    def __init__(self, queue_manager):
        super().__init__()
        self.server_list = []
        self.queue_manager = queue_manager

    async def add_embeds(self, server):
        server_channels = ChannelList(server)
        await self.delete_messages(server, server_channels)
        await self.run_user_modules(server, server_channels)

    # TODO: Will need improving
    # Deletes all previous posts
    async def delete_messages(self, server, channel_list):
        message_id_list = client_db_interface.load_message_ids(server)
        i = 0
        while i < 2:
            try:
                bot_message = await channel_list.admin_channel.fetch_message(message_id_list[i])
                await bot_message.delete()
            except Exception:
                pass
            i += 1
        while i < 5:
            try:
                bot_message = await channel_list.queue_channel.fetch_message(message_id_list[i])
                await bot_message.delete()
            except Exception:
                pass
            i += 1

    async def run_user_modules(self, server, channels):
        # Create Admin Channel items
        admin_list = AdminPanelUserList(server)
        admin_view = admin_panel.AdminEmbed(server, AdminEmbedView(server), channels.chat_channel, channels.admin_channel, admin_list)
        admin_menu = menu_admin_options.AdminOptions(server)
        print("Admin Channel embeds created")
        # Create Inhouse Channel items
        register_view = register_user.RegisterEmbed(admin_list)
        user_menu = menu_user_options.UserOptions(channels.chat_channel, server, admin_list)
        inhouse_view = inhouse_queue.InhouseQueueEmbed(server, channels.chat_channel, channels.queue_channel, QueueEmbedView(server))
        print("Inhouse Channel embeds created")
        server_embeds = ServerEmbeds(server, inhouse_view, admin_view, admin_menu, user_menu, register_view)
        await self.send_embed_messages(server, server_embeds, channels)
        self.server_list.append(server_embeds)
        self.queue_manager.add_to_queue_list(inhouse_view)

    async def send_embed_messages(self, server, embeds, channels):
        await embeds.admin_panel.send_embed()
        admin_menu_message = await channels.admin_channel.send("Please use the below menus to edit settings or manage users",
                                                               view=embeds.admin_menu)
        register_message = await channels.queue_channel.send("New user? Please register here:", view=embeds.register_buttons)
        user_menu_message = await channels.queue_channel.send("Already registered? More options are available via the below menu",
                                                              view=embeds.user_menu)
        await embeds.inhouse_queue.send_embed()
        message_id_list = [embeds.admin_panel.message.id, admin_menu_message.id, register_message.id, user_menu_message.id,
                           embeds.inhouse_queue.message.id, 100]
        client_db_interface.update_message_ids(server, message_id_list)
        # await channels.chat_channel.send("Bot is now running, please feel free to join the queue.")
        return

    async def setup_command(self, ctx):
        await ctx.send("Beginning setup of inhouse bot")
        config_setup = initialisation.ConfigButtons()
        await config_setup.config_start(ctx)
        await config_setup.wait()
        if config_setup.completed:
            server_channels = ChannelList(ctx.guild)
            await self.run_user_modules(ctx.guild, server_channels)

    def start_check_loop(self):
        self.queue_manager.check_full_queues.start()

    async def refresh_command(self, ctx):
        if not client_db_interface.check_server_settings(ctx.guild):
            await ctx.send("Server not set up yet!")
        if not client_db_interface.check_admin(ctx.author, ctx.guild):
            await ctx.send("Only admins can use this role")
        await self.remove_from_server_list(ctx)

    async def remove_from_server_list(self, ctx):
        server = next((x for x in self.server_list if x.server == ctx.guild.id), None)
        if server:
            print("Clearing channels for server " + server.name)
            self.server_list.remove(server)
        await self.add_embeds(server)

    def check_channel(self, ctx):
        if not client_db_interface.check_server_settings(ctx.guild):
            return None
        chosen_server = next(x for x in self.server_list if x.server == ctx.guild.id)
        if chosen_server.chat_channel != ctx.message.channel:
            return None
        return chosen_server
