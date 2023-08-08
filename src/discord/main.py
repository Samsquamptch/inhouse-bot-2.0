import discord

async def sendMessage(message, user_message, is_private):
	await message.channel.send("hi")

def runDiscordBot():
	token = 'MTEzODYwMjQ0NzQ2MDM3NjY2OA.G58NkE.7n3ioyav-KnOe5vb8QVGr2rZmtDIikgIlBm27s'
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
		
		await message.channel.send("hi")

	client.run(token)

if __name__ == '__main__':
	runDiscordBot()
	pass