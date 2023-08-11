import discord
from discord import ui, app_commands
from discord.ext import commands
from datetime import datetime
import yaml
from yaml.loader import SafeLoader
import pickle
import os
import psycopg2

currentQueue = {}

def saveRegistered():
	with open('../../data/Registered.pklz', 'wb') as f:
		pickle.dump(RegisteredPlayers, f)

def loadRegistered():
	if os.path.getsize('../../data/Registered.pklz') > 0:   
		with open('../../data/Registered.pklz', 'rb') as f:
			rp = pickle.load(f)
			print(f'registered players loaded from file: {rp}')
			return rp

def saveVouched():
	with open('../../data/Vouched.pklz', 'wb') as f:
		pickle.dump(VouchedPlayers, f)

def loadVouched():
	if os.path.getsize('../../data/Vouched.pklz') > 0:   
		with open('../../data/Vouched.pklz', 'rb') as f:
			rp = pickle.load(f)
			print(f'Vouched players loaded from file: {rp}')
			return rp
	else:
		return {}
RegisteredPlayers = loadRegistered()
# for i in range(1, 10):
# 	RegisteredPlayers['player' + str(i)] = {'dota id': '1', 'mmr': '2'}
VouchedPlayers = loadVouched()
# for i in range(1, 20):
# 	VouchedPlayers['player' + str(i)] = {'dota id': '1', 'mmr': '2'}

class RegisterModal(ui.Modal, title='Register for inhouse'):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		answer1 = ui.TextInput(label='dota id', style=discord.TextStyle.short, required=True)
		answer2 = ui.TextInput(label='mmr', style=discord.TextStyle.short, required=True)
		self.add_item(answer1)
		self.add_item(answer2)

	async def on_submit(self, interaction: discord.Interaction):
		RegisteredPlayers[interaction.user.name] = {self.children[0].label : self.children[0].value, self.children[1].label : self.children[1].value}
		saveRegistered()
		await interaction.response.send_message(f'{interaction.user.name} you registered with {self.children[0].label}: {self.children[0].value} and {self.children[1].label}: {self.children[1].value}', ephemeral=True, delete_after=5)

def loadToken():
	with open('../../credentials/discord_credentials.yml') as f:
		data = yaml.load(f, Loader=SafeLoader)
	return data['TOKEN']

def formattedQueue():
	text = '---------------------------------------------------------------------------------------------------------- \n'
	text += str(currentQueue) + '\n'
	text += '----------------------------------------------------------------------------------------------------------'
	return text

# from: https://github.com/Rapptz/discord.py/blob/master/examples/views/persistent.py
# Define a simple View that persists between bot restarts
# In order for a view to persist between restarts it needs to meet the following conditions:
# 1) The timeout of the View has to be set to None
# 2) Every item in the View has to have a custom_id set
# It is recommended that the custom_id be sufficiently unique to
# prevent conflicts with other buttons the bot sends.
# For this example the custom_id is prefixed with the name of the bot.
# Note that custom_ids can only be up to 100 characters long.
class RegisterButton(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Register', style=discord.ButtonStyle.grey, custom_id='persistent_view:Register', row=4)
	async def modal_popup(self, interaction: discord.Interaction, button: discord.ui.Button):
		if interaction.user.name in RegisteredPlayers:
			await interaction.response.send_message(f'you already registered, you need to be vouched before you can queue', ephemeral=True, delete_after=5)
		else:
			await interaction.response.send_modal(RegisterModal())
		if interaction.user.name in VouchedPlayers:
			await interaction.response.send_message(f'you already registered and vouched, you can join the queue', ephemeral=True, delete_after=5)


class JoinAndLeaveButtons(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='Join queue', style=discord.ButtonStyle.green, custom_id='persistent_view:join')
	async def joinQueue(self, interaction: discord.Interaction, button: discord.ui.Button):
		name = interaction.user.name
		if name in VouchedPlayers:
			currentQueue[name] = VouchedPlayers[name]['mmr']
			await interaction.response.send_message(f'you just joined the queue', ephemeral=True, delete_after=5)
		if name not in RegisteredPlayers and name not in VouchedPlayers:
			await interaction.response.send_message(f'you need to register before you can queue, use the register button', ephemeral=True, delete_after=5)
		if name in RegisteredPlayers and name not in VouchedPlayers:
			await interaction.response.send_message(f'you need to be vouched by an admin before you can join the queue', ephemeral=True, delete_after=5)

		lastMessage = await interaction.channel.fetch_message(interaction.channel.last_message_id)
		await lastMessage.edit(content=formattedQueue())

	@discord.ui.button(label='leave queue', style=discord.ButtonStyle.red, custom_id='persistent_view:leave')
	async def leaveQueue(self, interaction: discord.Interaction, button: discord.ui.Button):
		name = interaction.user.name
		if name in currentQueue:
			del currentQueue[name]
			await interaction.response.send_message(f'you just left the queue', ephemeral=True, delete_after=5)
		else:
			await interaction.response.send_message(f'you are currently not in the queue', ephemeral=True, delete_after=5)

		lastMessage = await interaction.channel.fetch_message(interaction.channel.last_message_id)
		await lastMessage.edit(content=formattedQueue())

class VouchModal(ui.Modal, title=''):
	def __init__(self, player, parent_view, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.parent_view = parent_view
		self.player = player
		self.title = f'you are vouching {player}'
		answer1 = ui.TextInput(label='dota id', style=discord.TextStyle.short, required=True, default=RegisteredPlayers[self.player]['dota id'])
		answer2 = ui.TextInput(label='mmr', style=discord.TextStyle.short, required=True, default=RegisteredPlayers[self.player]['mmr'])
		self.add_item(answer1)
		self.add_item(answer2)

	async def on_submit(self, interaction: discord.Interaction):
		RegisteredPlayers[interaction.user.name] = {self.children[0].label : self.children[0].value, self.children[1].label : self.children[1].value}
		VouchedPlayers[self.player] = RegisteredPlayers[self.player]
		del RegisteredPlayers[self.player]

		saveRegistered()
		saveVouched()
		# For DB access.
		dotesID = VouchedPlayers[self.player]['dota id']
		dotesmmr = VouchedPlayers[self.player]["mmr"]
		with open("../../credentials/databaseconnect.yml", "r") as con_info:
			con = (yaml.safe_load(con_info))
			host = con['HOST']
			port = con['PORT']
			user = con['USER']
			password = con['PASSWORD']

		try:
			connection = psycopg2.connect(user=user, host=host, password=password, port=port, database='doghouse')
			cursor = connection.cursor()

			cursor.execute(f"INSERT INTO players (DotaID, MMR) VALUES ({str(dotesID)}, {str(dotesmmr)}) RETURNING *;")
			connection.commit()

		except (psycopg2.errors.UniqueViolation) as error:
			print("Error while connecting to PostgreSQL or inserting:", error)

		self.parent_view = adminPanelRegisteredButtons()
		for player in RegisteredPlayers.keys():
			button = VouchButton(parent_view=self.parent_view, label=f"vouch {player}", style=discord.ButtonStyle.green, player=player)
			self.parent_view.add_item(button)
		await interaction.response.edit_message(content='registered players \n', view=self.parent_view)
		
		await interaction.followup.send(content=f'you vouched {self.player} with {self.children[0].label}: {self.children[0].value} and {self.children[1].label}: {self.children[1].value}', ephemeral=True)

class EditVouchedModal(ui.Modal, title=''):
	def __init__(self, player, parent_view, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		self.parent_view = parent_view
		self.player = player
		self.title = f'you are editing {player}'
		answer1 = ui.TextInput(label='dota id', style=discord.TextStyle.short, required=True, default=VouchedPlayers[self.player]['dota id'])
		answer2 = ui.TextInput(label='mmr', style=discord.TextStyle.short, required=True, default=VouchedPlayers[self.player]['mmr'])
		self.add_item(answer1)
		self.add_item(answer2)

	async def on_submit(self, interaction: discord.Interaction):
		VouchedPlayers[interaction.user.name] = {self.children[0].label : self.children[0].value, self.children[1].label : self.children[1].value}
		#saveVouched()
		await interaction.response.send_message(content=f'you edited {self.player} with {self.children[0].label}: {self.children[0].value} and {self.children[1].label}: {self.children[1].value}', ephemeral=True, delete_after=5)

	async def on_submit(self, interaction: discord.Interaction):
		VouchedPlayers[interaction.user.name] = {self.children[0].label : self.children[0].value, self.children[1].label : self.children[1].value}
		#saveVouched()
		await interaction.response.send_message(content=f'you edited {self.player} with {self.children[0].label}: {self.children[0].value} and {self.children[1].label}: {self.children[1].value}', ephemeral=True, delete_after=5)


class VouchButton(discord.ui.Button):
	def __init__(self, parent_view, player, **kwargs):
		super().__init__(**kwargs)
		self.parent_view = parent_view
		self.player = player

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_modal(VouchModal(parent_view=self.parent_view, player=self.player))

class editVouchedButton(discord.ui.Button):
	def __init__(self, parent_view, player, **kwargs):
		super().__init__(**kwargs)
		self.parent_view = parent_view
		self.player = player

	async def callback(self, interaction: discord.Interaction):
		await interaction.response.send_modal(EditVouchedModal(parent_view=self.parent_view, player=self.player))

class unVouchButton(discord.ui.Button):
	def __init__(self, parent_view, player, **kwargs):
		super().__init__(**kwargs)
		self.parent_view = parent_view
		self.player = player

	async def callback(self, interaction: discord.Interaction):
		del VouchedPlayers[self.player]
		await interaction.response.send_message(f'{self.player} has been unvouched, they will need to register again', ephemeral=True, delete_after=5)


class adminPanelRegisteredButtons(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='update registered panel', style=discord.ButtonStyle.green, custom_id='persistent_view:updatereregistered')
	async def updateRegistered(self, interaction: discord.Interaction, button: discord.ui.Button):
		print("updating adminPanel")
		view = adminPanelRegisteredButtons()
		for player in RegisteredPlayers.keys():
			button = VouchButton(parent_view=view, label=f"vouch {player}", style=discord.ButtonStyle.green, player=player)
			view.add_item(button)

		await interaction.response.edit_message(content='registered players \n', view=view)

class adminPanelVouchedButtons(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)

	@discord.ui.button(label='show vouched players', style=discord.ButtonStyle.green, custom_id='persistent_view:updatevouched')
	async def updateVouched(self, interaction: discord.Interaction, button: discord.ui.Button):
		await interaction.channel.send("vouched players:")
		await interaction.channel.send("------------------------")
		firstMessage = [message async for message in interaction.channel.history(limit=1, oldest_first=True)]
		await interaction.channel.purge(after=firstMessage[0])
		for player in VouchedPlayers.keys():
			view = discord.ui.View()
			editButton = editVouchedButton(parent_view=view, label=f"edit {player}", style=discord.ButtonStyle.green, player=player)
			unvouchbutton = unVouchButton(parent_view=view, label=f"unvouch {player}", style=discord.ButtonStyle.red, player=player)
			view.add_item(editButton)
			view.add_item(unvouchbutton)
			await interaction.channel.send(f'{player}:', view=view)



class PersistentViewBot(commands.Bot):
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True

		super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

	async def setup_hook(self) -> None:
		# Register the persistent view for listening here.
		# Note that this does not send the view to any message.
		# In order to do this you need to first send a message with the View, which is shown below.
		# If you have the message_id you can also pass it as a keyword argument, but for this example
		# we don't have one.
		self.add_view(RegisterButton())
		self.add_view(JoinAndLeaveButtons())
		self.add_view(adminPanelRegisteredButtons())
		self.add_view(adminPanelVouchedButtons())



	async def on_ready(self):
		print(f'Logged in as {self.user} (ID: {self.user.id})')
		print('------')

bot = PersistentViewBot()

@bot.command()
@commands.is_owner()
async def prepare(ctx: commands.Context):
	"""Starts a persistent view."""
	# In order for a persistent view to be listened to, it needs to be sent to an actual message.
	# Call this method once just to store it somewhere.
	# In a more complicated program you might fetch the message_id from a database for use later.
	# However this is outside of the scope of this simple example.
	await ctx.channel.purge()
	await ctx.send("Doghouse queue", view=RegisterButton())
	await ctx.send("Doghouse queue", view=JoinAndLeaveButtons())
	await ctx.send("---------------------------------------------------------------------------------------------------------- \n queue currently empty \n ----------------------------------------------------------------------------------------------------------")

@bot.command()
@commands.is_owner()
async def registeredPanel(ctx: commands.Context):
	"""Starts a persistent view."""
	# In order for a persistent view to be listened to, it needs to be sent to an actual message.
	# Call this method once just to store it somewhere.
	# In a more complicated program you might fetch the message_id from a database for use later.
	# However this is outside of the scope of this simple example.
	await ctx.channel.purge()
	await ctx.send("Registered players (need to be vouched)", view=adminPanelRegisteredButtons())

@bot.command()
@commands.is_owner()
async def vouchedPanel(ctx: commands.Context):
	"""Starts a persistent view."""
	# In order for a persistent view to be listened to, it needs to be sent to an actual message.
	# Call this method once just to store it somewhere.
	# In a more complicated program you might fetch the message_id from a database for use later.
	# However this is outside of the scope of this simple example.
	await ctx.channel.purge()
	await ctx.send("Vouched players can queue", view=adminPanelVouchedButtons())


@bot.command()
async def registered(ctx: commands.Context):
	await ctx.send(f"registered players: \n {RegisteredPlayers}")

@bot.command()
async def vouched(ctx: commands.Context):
	await ctx.send(f"registered players: \n {VouchedPlayers}")


bot.run(loadToken())