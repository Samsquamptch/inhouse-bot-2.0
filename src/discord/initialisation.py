import discord
import discord_service
import admin_panel
import register_user
import select_menus
import inhouse_queue


class ServerViews:
    def __init__(self, server_id, inhouse_view, admin_view):
        super().__init__()
        self.server = server_id
        self.inhouse = inhouse_view
        self.admin = admin_view

class SetupModal(discord.ui.Modal, title='Text Channels Configuration'):
    def __init__(self):
        super().__init__(timeout=None)
        self.confirmed = False

    admin_channel = discord.ui.TextInput(label='Set admin channel')
    queue_channel = discord.ui.TextInput(label='Set queue channel')
    global_channel = discord.ui.TextInput(label='Set global queue channel')
    chat_channel = discord.ui.TextInput(label='Set chat channel')
    async def on_submit(self, interaction: discord.Interaction):
        try:
            admin_str = str(self.admin_channel)
            queue_str = str(self.queue_channel)
            global_str = str(self.global_channel)
            chat_str = str(self.chat_channel)
            admin_id = int(admin_str)
            queue_id = int(queue_str)
            global_id = int(global_str)
            chat_id = int(chat_str)
        except ValueError:
            await interaction.response.send_message(content="please only enter numbers for the Channel IDs",
                                                     ephemeral=True)
            return
        channel_list = [admin_id, queue_id, global_id, chat_id]
        for channel in channel_list:
            print(channel)
            if not discord.utils.get(interaction.guild.channels, id=channel):
                await interaction.response.send_message(content="Channel ID " + str(channel) + " not found on server!",
                                                        ephemeral=True)
                return
        discord_service.register_server(interaction.guild, channel_list)
        await interaction.response.send_message(content="Channels set",
                                                ephemeral=True)
        self.confirmed = True
        return

class ConfigButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        with open("../../data/setup.txt", "r") as setup:
            self.setup_guide = setup.read().split("\n\n")
            self.config_user = None
            self.message = None

    async def config_start(self, ctx):
        self.config_user = ctx.author
        await self.button_state(False)
        self.message = await ctx.channel.send(self.setup_guide[0], view=self)

    async def button_state(self, setup_status):
        print(setup_status)
        if not setup_status:
            self.confirm_button.disabled = True
        else:
            self.confirm_button.disabled = False


    @discord.ui.button(label="Set Channels", emoji="🔧",
                       style=discord.ButtonStyle.green)
    async def set_channels_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.config_user:
            return
        setup_modal = SetupModal()
        await interaction.response.send_modal(setup_modal)
        await setup_modal.wait()
        await self.button_state(setup_modal.confirmed)

    @discord.ui.button(label="Confirm", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.config_user:
            return
        discord_service.add_default_settings(interaction.guild)
        await interaction.response.send_message(
            content="Channels have been registered and defauls settings added. Please amend these via the admin panel",
            ephemeral=True)
        return


async def run_user_modules(server):
    channel_id = discord_service.load_config_data(server.id, 'CHANNELS')
    admin_channel = discord.utils.get(server.channels, id=channel_id['admin_channel'])
    queue_channel = discord.utils.get(server.channels, id=channel_id['queue_channel'])
    # Send admin panel to admin channel
    await admin_channel.purge()
    verify_view = admin_panel.AdminEmbed(discord_service.load_config_data(server.id, 'ROLES'))
    await verify_view.send_embed(admin_channel, server)
    await admin_channel.send("More options are available via the drop-down menu below",
                             view=select_menus.AdminOptions())
    print("Admin settings created")
    # Send queue buttons and panel to queue channel
    await queue_channel.purge()
    inhouse_id = discord_service.load_config_data(server.id, 'ROLES', 'registered_role')
    register_view = register_user.RegisterButton(discord.utils.get(server.roles, id=inhouse_id), verify_view)
    await queue_channel.send("New user? Please register here:", view=register_view)
    await queue_channel.send("Already registered? More options are available via the drop-down menu below",
                             view=select_menus.UserOptions())
    inhouse_view = inhouse_queue.InhouseQueue(server, discord_service.load_config_data(server.id, 'ROLES'),
                                              discord_service.load_config_data(server.id, 'CHANNELS'),
                                              discord_service.load_config_data(server.id, 'CONFIG'))
    await inhouse_view.send_embed(queue_channel)
    print("User settings created")
    return ServerViews(server.id, inhouse_view, verify_view)
