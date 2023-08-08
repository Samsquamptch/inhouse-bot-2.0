import discord
import yaml
from yaml.loader import SafeLoader

def loadToken():
	with open('../../credentials/discord_credentials.yml') as f:
		data = yaml.load(f, Loader=SafeLoader)
	return data['TOKEN']

async def sendMessage(message, user_message, is_private):
	await message.channel.send("hi")

def runDiscordBot():
	token = loadToken()
	client = discord.Client(intents=discord.Intents.default())

	@client.event
	async def on_ready():
		print(f'{client.user} is now running')

	@client.event
	async def on_message(message):
		if message.author == client.user:
			return
		user_name = str(message.author)
		user_message = str(message.content)
		channel = str(message.channel)
		print(f"user: {user_name} said {user_message} in channel: {channel}")
		
		if user_message == 'test':
			await message.channel.send("hi")

	client.run(token)

if __name__ == '__main__':
	runDiscordBot()
	pass