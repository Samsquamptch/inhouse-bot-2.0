from src.discord import admin_panel, select_menus, register_user, client_db_interface, inhouse_queue, check_user, \
    initialisation


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
        server_embeds = ServerEmbeds(server, inhouse_view, admin_view, admin_menu, user_menu, register_view)
        await self.send_embed_messages(server, server_embeds, channels)
        self.server_list.append(server_embeds)

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

    async def register_command(self, ctx, user, dotabuff_id, mmr):
        server = self.check_channel(ctx)
        if not server:
            return
        ctx.response.send_message()
        disc_reg = client_db_interface.check_for_value("disc", ctx.author.id)
        steam_reg = client_db_interface.check_for_value("steam", dotabuff_id)
        if registered_role in ctx.author.roles or disc_reg:
            await ctx.send("Your discord account is already registered!")
            return
        elif steam_reg:
            await ctx.send("Your steam account is already registered!")
            return
        else:
            await self.bot.register_command(ctx.author, dotabuff_id, mmr)
            await ctx.send("You have been registered. Please set your roles using !roles")

    async def refresh_command(self, ctx):
        if not client_db_interface.check_server_settings(ctx.guild):
            await ctx.send("Server not set up yet!")
        if not client_db_interface.check_admin(ctx.author, ctx.guild):
            await ctx.send("Only admins can use this role")
        await self.remove_from_server_list(ctx)

    async def remove_from_server_list(self, ctx):
        server = next(x for x in self.server_list if x.server == ctx.guild.id)
        print("Clearing channels for server " + server.name)
        self.server_list.remove(server)
        await self.add_embeds(server)

    async def check_channel(self, ctx):
        if not client_db_interface.check_server_settings(ctx.guild):
            await ctx.send(content=f'Please ensure setup has been completed before using commands', ephemeral=True)
            return False
        if not client_db_interface.check_chat_channel(ctx.message, ctx.guild):
            return False
        else:
            chosen_server = next(x for x in self.server_list if x.server == ctx.guild.id)
            return chosen_server

    async def who_command(self, ctx, user=None):
        server = self.check_channel(ctx)
        if not server:
            return
        if user is None:
            user_acc = await ctx.guild.fetch_member(ctx.author.id)
            user_check = client_db_interface.check_discord_exists(ctx.author.id)
        elif user[0:2] == '<@':
            user_acc = await ctx.guild.fetch_member(user[2:-1])
            user_check = client_db_interface.check_discord_exists(int(user[2:-1]))
        else:
            user_check, user_acc = check_user.user_exists(ctx.guild, user)
        if not user_check:
            await ctx.send(content=f'{user_acc.display_name} not found', ephemeral=True)
        else:
            user_data = client_db_interface.view_user_data(user_acc.id)
            await ctx.send(embed=check_user.UserEmbed.user_embed(user_data, user_acc, ctx.guild))
