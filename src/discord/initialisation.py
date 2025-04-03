import discord
import client_db_interface
import admin_panel
import register_user
import menu_admin_options
import inhouse_queue


class SetupModal(discord.ui.Modal, title='Text Channels Configuration'):
    def __init__(self):
        super().__init__(timeout=None)
        self.confirmed = False

    admin_channel = discord.ui.TextInput(label='Set admin channel')
    queue_channel = discord.ui.TextInput(label='Set queue channel')
    global_channel = discord.ui.TextInput(label='Set global queue channel')
    chat_channel = discord.ui.TextInput(label='Set chat channel')
    admin_role = discord.ui.TextInput(label="Set Admin Role")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            queue_id = int(str(self.queue_channel))
            global_id = int(str(self.global_channel))
            chat_id = int(str(self.chat_channel))
            admin_id = int(str(self.admin_channel))
        except ValueError:
            await interaction.response.send_message(content="please only enter numbers for the Channel IDs",
                                                    ephemeral=True)
            return
        channel_list = [admin_id, queue_id, global_id, chat_id, admin_id]
        for channel in channel_list:
            print(channel)
            if not discord.utils.get(interaction.guild.channels, id=channel):
                await interaction.response.send_message(content="Channel ID " + str(channel) + " not found on server!",
                                                        ephemeral=True)
                return
        client_db_interface.register_server(interaction.guild, channel_list)
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
            self.completed = False

    async def config_start(self, ctx):
        self.config_user = ctx.author
        self.message = await ctx.channel.send(self.setup_guide[0], view=self)

    async def button_state(self, setup_status):
        # False means confirm button can be pressed (i.e. channels have been configured). True means setup is complete
        # and both buttons are disabled
        if not setup_status:
            self.confirm_button.disabled = False
        else:
            self.confirm_button.disabled = True
            self.set_channels_button.disabled = True
        await self.message.edit(view=self)

    @discord.ui.button(label="Set Channels", emoji="🔧",
                       style=discord.ButtonStyle.green)
    async def set_channels_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.config_user:
            return
        setup_modal = SetupModal()
        await interaction.response.send_modal(setup_modal)
        await setup_modal.wait()
        if setup_modal.confirmed:
            await self.button_state(False)

    @discord.ui.button(label="Confirm", emoji="✅",
                       style=discord.ButtonStyle.green, disabled=True)
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.config_user:
            return
        if client_db_interface.check_server_settings(interaction.guild):
            await interaction.response.send_message(
                content="default settings already configured",
                ephemeral=True)
        client_db_interface.add_default_settings(interaction.guild)
        await self.button_state(True)
        await interaction.response.send_message(
            content="Channels have been registered and default settings added. Please amend these via the admin panel",
            ephemeral=True)
        self.completed = True
        return

