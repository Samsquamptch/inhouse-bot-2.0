import discord
import data_management
import admin_panel
import register_user
import select_menus
import inhouse_queue


class SetRolesModal(discord.ui.Modal, title='User Roles Configuration'):
    def __init__(self):
        super().__init__(timeout=None)

    admin_role = discord.ui.TextInput(label='Set admin role')
    inhouse_role = discord.ui.TextInput(label='Set inhouse role')
    verified_role = discord.ui.TextInput(label='Set verified role')
    banned_role = discord.ui.TextInput(label='Set banned role')
    champions_role = discord.ui.TextInput(label='Set champions role')

    async def on_submit(self, interaction: discord.Interaction):
        admin_str = str(self.admin_role)
        inhouse_str = str(self.inhouse_role)
        verified_str = str(self.verified_role)
        banned_str = str(self.banned_role)
        champions_str = str(self.champions_role)
        roles_dict = {'admin_role': admin_str, 'registered_role': inhouse_str, 'verified_role': verified_str,
                      'champions_role': champions_str, 'banned_role': banned_str}
        premade_roles = await create_roles(interaction, roles_dict)
        role_list = [admin_str, inhouse_str, verified_str, banned_str, champions_str]
        yes_no = YesNoButtons()
        yes_no.config_user = interaction.user
        yes_no.setup_position = 4
        yes_no.clear_channel_list = [i for i in role_list if i not in premade_roles]
        await interaction.response.send_message(
            f'You\'ve created the following roles: \n'
            f'{role_list[0]} \n {role_list[1]} \n {role_list[2]} \n {role_list[3]} \n {role_list[4]} \n'
            f'Do you wish to keep these?', view=yes_no)


class SetupChannelsModal(discord.ui.Modal, title='Text Channels Configuration'):
    def __init__(self):
        super().__init__(timeout=None)

    inhouse_category = discord.ui.TextInput(label='Set inhouse channel category')
    admin_channel = discord.ui.TextInput(label='Set admin channel')
    queue_channel = discord.ui.TextInput(label='Set queue channel')
    notif_channel = discord.ui.TextInput(label='Set notification channel')
    chat_channel = discord.ui.TextInput(label='Set chat channel')

    async def on_submit(self, interaction: discord.Interaction):
        cat_str = str(self.inhouse_category)
        admin_str = str(self.admin_channel)
        queue_str = str(self.queue_channel)
        notif_str = str(self.notif_channel)
        chat_channel = str(self.chat_channel)
        channel_dict = {'admin_channel': admin_str, 'queue_channel': queue_str, 'notification_channel': notif_str,
                        'chat_channel': chat_channel}
        channel_list = [admin_str, queue_str, notif_str, chat_channel]
        category_and_channels = await create_channels(interaction, cat_str, channel_dict)
        yes_no = YesNoButtons()
        yes_no.config_user = interaction.user
        yes_no.setup_position = 3
        yes_no.category = category_and_channels[0]
        yes_no.clear_channel_list = [i for i in channel_list if i not in category_and_channels[1]]
        await interaction.response.send_message(
            f'You\'ve created the category {cat_str} with the channels: \n'
            f'{channel_list[0]} \n {channel_list[1]} \n {channel_list[2]} \n {channel_list[3]} \n'
            f'Do you wish to keep these?', view=yes_no)


class VoiceChannelButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.voice_category = None
        self.config_user = None

    @discord.ui.button(label="Yes", emoji="👍",
                       style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            await create_voice(interaction, self.voice_category)
            await interaction.response.send_modal(SetRolesModal())
            await interaction.message.delete()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="No", emoji="👎",
                       style=discord.ButtonStyle.green)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            await interaction.response.send_modal(SetRolesModal())
            await interaction.message.delete()
        else:
            await interaction.response.defer()


class YesNoButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.setup_position = 0
        self.config_user = None
        self.category = None
        self.clear_list = []

    async def automated_setup(self, interaction):
        channel_dict = data_management.load_default_config('CHANNELS')
        cat_str = channel_dict['inhouse_category']
        del channel_dict['inhouse_category']
        voice_category = await create_channels(interaction, cat_str, channel_dict)
        await create_voice(interaction, voice_category[0])
        roles_dict = data_management.load_default_config('ROLES')
        await create_roles(interaction, roles_dict)
        await confirm_configuration(interaction)
        await interaction.channel.send(
            "Automated setup has now finished. The bot will now run automatically on start.")
        await run_user_modules(interaction.guild)

    @discord.ui.button(label="Yes", emoji="👍",
                       style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            match self.setup_position:
                case 1:
                    await interaction.response.send_message(content="Proceeding with automated setup")
                    # An issue with the next function means the message doesn't get deleted later. this delete solves that
                    await interaction.message.delete()
                    await self.automated_setup(interaction)
                case 2:
                    await interaction.response.send_modal(SetupChannelsModal())
                case 3:
                    voice_buttons = VoiceChannelButtons()
                    voice_buttons.config_user = interaction.user
                    voice_buttons.voice_category = self.category
                    await interaction.response.send_message("Do you want to add voice channels?", view=voice_buttons)
                case 4:
                    await confirm_configuration(interaction)
                    await interaction.response.send_message(
                        "Thank you for completing setup. The bot will now run automatically on start.")
                    await run_user_modules(interaction.guild)
            try:
                await interaction.message.delete()
            except discord.errors.NotFound:
                print("Message already deleted")
        else:
            await interaction.response.defer()

    @discord.ui.button(label="No", emoji="👎",
                       style=discord.ButtonStyle.green)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            match self.setup_position:
                case 1 | 2:
                    self.setup_position = 0
                    await interaction.response.defer()
                case 3:
                    if self.clear_list:
                        for channel in self.clear_list:
                            del_channel = discord.utils.get(interaction.guild.channels, name=channel)
                            await del_channel.delete(reason="inhouse bot instructed")
                    await interaction.response.send_modal(SetupChannelsModal())
                case 4:
                    if self.clear_list:
                        for role in self.clear_list:
                            del_role = discord.utils.get(interaction.guild.roles, name=role)
                            await del_role.delete(reason="inhouse bot instructed")
                    await interaction.response.send_modal(SetRolesModal())
            await interaction.message.delete()
        else:
            await interaction.response.defer()


class ConfigButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        with open("../../data/setup.txt", "r") as setup:
            self.setup_guide = setup.read().split("\n\n")
            self.config_user = None
            self.message = None

    async def config_start(self, ctx):
        self.config_user = ctx.author
        self.message = await ctx.channel.send(self.setup_guide[0], view=self)

    async def select_option(self, channel):
        self.message = await channel.send(content="", view=self)

    async def update_buttons(self, num=0):
        if num == 0:
            self.auto_setup.disabled = False
            self.manual_setup.disabled = False
        else:
            self.auto_setup.disabled = True
            self.manual_setup.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Automated Setup", emoji="🤖",
                       style=discord.ButtonStyle.green)
    async def auto_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            yes_no_view = YesNoButtons()
            yes_no_view.setup_position = 1
            yes_no_view.config_user = self.config_user
            await self.update_buttons(yes_no_view.setup_position)
            await interaction.response.send_message(content="Automated setup was selected. Confirm?", view=yes_no_view)
            await yes_no_view.wait()
            if yes_no_view.setup_position == 0:
                await self.update_buttons(yes_no_view.setup_position)
                await interaction.response.defer()
            else:
                await interaction.response.defer()
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Manual Setup", emoji="👨‍💻",
                       style=discord.ButtonStyle.green)
    async def manual_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.config_user:
            yes_no_view = YesNoButtons()
            yes_no_view.setup_position = 2
            yes_no_view.config_user = self.config_user
            await self.update_buttons(yes_no_view.setup_position)
            await interaction.response.send_message(content="Manual setup was selected. Confirm?", view=yes_no_view)
            await yes_no_view.wait()
            if yes_no_view.setup_position == 0:
                await self.update_buttons(yes_no_view.setup_position)
                await interaction.response.defer()
            else:
                await interaction.response.defer()
        else:
            await interaction.response.defer()


async def confirm_configuration(interaction):
    channel_id = data_management.load_config_data(interaction.guild, 'CHANNELS', 'admin_channel')
    role_id = data_management.load_config_data(interaction.guild, 'ROLES', 'admin_role')
    admin_channel = discord.utils.get(interaction.guild.channels, id=channel_id)
    admin_role = discord.utils.get(interaction.guild.roles, id=role_id)
    await admin_channel.set_permissions(admin_role, read_messages=True)
    data_management.update_config(interaction.guild, 'CONFIG', 'server_id', interaction.guild.id)
    data_management.update_config(interaction.guild, 'CONFIG', 'setup_complete', 'Yes')


async def create_voice(interaction, voice_category):
    channel_list = ["Casting Channel", "Waiting Room", "Radiant Voice", "Dire Voice"]
    for channel in channel_list:
        check_chann = discord.utils.get(voice_category.voice_channels, name=channel)
        if not check_chann:
            await interaction.guild.create_voice_channel(name=channel, category=voice_category)


async def create_roles(interaction, roles_dict):
    premade_roles = []
    for role in roles_dict:
        check_user = discord.utils.get(interaction.guild.roles, name=roles_dict[role])
        if not check_user:
            await interaction.guild.create_role(name=roles_dict[role])
            check_user = discord.utils.get(interaction.guild.roles, name=roles_dict[role])
        else:
            premade_roles.append(roles_dict[role])
        data_management.update_config(interaction.guild, 'ROLES', role, check_user.id)
    return premade_roles


async def create_channels(interaction, cat_str, channel_dict):
    check_categ = discord.utils.get(interaction.guild.categories, name=cat_str)
    if not check_categ:
        await interaction.guild.create_category(name=cat_str)
        check_categ = discord.utils.get(interaction.guild.categories, name=cat_str)
    data_management.update_config(interaction.guild, 'CHANNELS', 'inhouse_category', check_categ.id)
    set_category = discord.utils.get(interaction.guild.categories, name=cat_str)
    premade_channels = []
    for channel in channel_dict:
        check_chann = discord.utils.get(set_category.text_channels, name=channel_dict[channel])
        if not check_chann:
            match channel:
                case 'admin_channel':
                    overwrites = {
                        interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
                    }
                case 'queue_channel' | 'notification_channel':
                    overwrites = {
                        interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                        interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                    }
                case _:
                    overwrites = {
                        interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                    }
            await interaction.guild.create_text_channel(name=channel_dict[channel], category=set_category,
                                                        overwrites=overwrites)
            check_chann = discord.utils.get(set_category.text_channels, name=channel_dict[channel])
        else:
            premade_channels.append(channel_dict[channel])
        data_management.update_config(interaction.guild, 'CHANNELS', channel, check_chann.id)
    return set_category, premade_channels


async def run_user_modules(server):
    channel_id = data_management.load_config_data(server, 'CHANNELS')
    admin_channel = discord.utils.get(server.channels, id=channel_id['admin_channel'])
    queue_channel = discord.utils.get(server.channels, id=channel_id['queue_channel'])
    # Send admin panel to admin channel
    await admin_channel.purge()
    verify_view = admin_panel.AdminEmbed()
    verify_view.roles_id = data_management.load_config_data(server, 'ROLES')
    await verify_view.send_embed(admin_channel, server)
    await admin_channel.send("More options are available via the drop-down menu below",
                             view=select_menus.AdminOptions())
    print("Admin settings created")
    # Send queue buttons and panel to queue channel
    await queue_channel.purge()
    regiser_view = register_user.RegisterButton()
    inhouse_id = data_management.load_config_data(server, 'ROLES', 'registered_role')
    regiser_view.role_inhouse = discord.utils.get(server.roles, id=inhouse_id)
    await queue_channel.send("New user? Please register here:", view=regiser_view)
    await queue_channel.send("Already registered? More options are available via the drop-down menu below",
                             view=select_menus.UserOptions())
    inhouse_view = inhouse_queue.InhouseQueue()
    inhouse_view.server = server
    inhouse_view.roles_id = data_management.load_config_data(server, 'ROLES')
    inhouse_view.channel_id = data_management.load_config_data(server, 'CHANNELS')
    inhouse_view.config_data = data_management.load_config_data(server, 'CONFIG')
    await inhouse_view.send_embed(queue_channel)
    print("User settings created")
