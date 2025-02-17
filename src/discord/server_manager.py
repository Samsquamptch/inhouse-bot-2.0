from src.discord import admin_panel, select_menus, register_user, client_db_interface, inhouse_queue


class ChannelList:
    def __init__(self, server):
        self.chat_channel = client_db_interface.load_chat_channel(server)
        self.admin_channel = client_db_interface.load_admin_channel(server)
        self.queue_channel = client_db_interface.load_queue_channel(server)
        self.global_channel = client_db_interface.load_global_channel(server)


class ServerEmbeds:
    def __init__(self, server_id, inhouse_view, admin_view, admin_menu, user_menu, register_view):
        super().__init__()
        self.server = server_id
        self.inhouse_queue = inhouse_view
        self.admin_panel = admin_view
        self.admin_menu = admin_menu
        self.user_menu = user_menu
        self.register_buttons = register_view


class ServerManager:
    def __init__(self):
        self.server_list = []

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
        admin_view = admin_panel.AdminEmbed(channels.chat_channel, channels.admin_channel, server)
        admin_menu = select_menus.AdminOptions()
        print("Admin Channel embeds created")
        # Create Inhouse Channel items
        register_view = register_user.RegisterEmbed()
        user_menu = select_menus.UserOptions(channels.chat_channel, server)
        queue_settings = client_db_interface.load_server_settings(server)
        inhouse_view = inhouse_queue.InhouseQueue(server, channels.chat_channel, channels.queue_channel, queue_settings[0],
                                                  queue_settings[1], queue_settings[2], queue_settings[3])
        print("Inhouse Channel embeds created")
        embed_object = ServerEmbeds(server.id, inhouse_view, admin_view, admin_menu, user_menu, register_view)
        await self.send_embed_messages(server, embed_object, channels)
        self.server_list.append(embed_object)

    async def send_embed_messages(self, server, embeds, channels):
        await embeds.admin_panel.send_embed()
        admin_menu_message = await channels.admin_channel.send("More options are available via the below menu",
                                                               view=embeds.admin_menu)
        register_message = await channels.queue_channel.send("New user? Please register here:", view=embeds.register_buttons)
        user_menu_message = await channels.queue_channel.send("Already registered? More options are available via the below menu",
                                                              view=embeds.user_menu)
        await embeds.inhouse_queue.send_embed()
        # await embeds.
        message_id_list = [embeds.admin_panel.message.id, admin_menu_message.id, register_message.id, user_menu_message.id,
                           embeds.inhouse_queue.message.id, 100]
        client_db_interface.update_message_ids(server, message_id_list)
        return

    async def register_command(self, user, dotabuff_id, mmr):
        return

    async def remove_from_server_list(self, server):
        print("Clearing channels for server " + server.name)
        chosen_server = next(x for x in self.server_list if x.server == server.id)
        self.server_list.remove(chosen_server)
        await self.add_embeds(server)
