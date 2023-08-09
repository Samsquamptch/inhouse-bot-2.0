import discord
from discord import ui, app_commands
from datetime import datetime
import yaml
from yaml.loader import SafeLoader

list = []
modalList = []

class testModal(ui.Modal, title='test modal'):
	def __init__(self, *args, **kwargs) -> None:
		super().__init__(*args, **kwargs)
		name = 'Register'
		answer1 = ui.TextInput(label='dota id', style=discord.TextStyle.short, required=True)
		answer2 = ui.TextInput(label='mmr', style=discord.TextStyle.short, required=True)
		self.add_item(answer1)
		self.add_item(answer2)

	async def on_submit(self, interaction: discord.Interaction):
		modalList.append({interaction.user.name : {self.children[0].label : self.children[0].value, self.children[1].label : self.children[1].value}})
		await interaction.response.send_message(f'modal submit test {modalList}')

async def modal_popup(interaction: discord.Interaction):
	print(f"{interaction.user}")
	list.append(interaction.user.name)
	await interaction.response.send_modal(testModal())

async def queue(interaction: discord.Interaction):
	print(f"{interaction.user}")
	list.append(interaction.user.name)
	await interaction.response.send_message(f'button test {list}')

class Button(discord.ui.View):
	def __init__(self, buttontext, on_press):
		super().__init__()
		button = discord.ui.Button(label=buttontext, style=discord.ButtonStyle.blurple)

		button.callback = on_press
		self.add_item(button)

def loadToken():
	with open('../../credentials/discord_credentials.yml') as f:
		data = yaml.load(f, Loader=SafeLoader)
	return data['TOKEN']

async def sendMessage(message, user_message, is_private):
	await message.channel.send("hi")

def runDiscordBot():
	token = loadToken()
	client = discord.Client(intents=discord.Intents.all())

	@client.event
	async def on_ready():
		print(f'{client.user} is now running')
		#send the message with the button to the channel
		channel = client.get_channel(1138763829602435162)
		await channel.send("this is another test message", view=Button('test', queue))
		await channel.send("this is another test message", view=Button('modalButton', modal_popup))

	#for commands
	@client.event
	async def on_message(message):
		if message.author == client.user:
			return
		print(message)
		user_name = str(message.author)
		user_message = str(message.content)
		channel = str(message.channel)
		print(f"user: {user_name} said {user_message} in channel: {channel}")
		
		if user_message == 'test':
			await message.channel.send("hi")

	client.run(token)

runDiscordBot()
