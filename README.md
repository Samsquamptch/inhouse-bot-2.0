# Birdhouse Bot 2.0
A lightweight Dota 2 Inhouse Bot capable of supporting multiple servers simultaneously. <br> 
This project is a continuation of the [Birdhouse Inhouse bot](https://github.com/Samsquamptch/BirdHouse-Inhouse-Bot), 
which itself was intended to be a successor to the [Dota2 EU Ladder Bot](https://github.com/UncleVasya/Dota2-EU-Ladder).

## Key Features
- Improved UI and UX for ease of use
- Simplified setup for less technical server owners
- Manage multiple Discord communities at once
- New global queue to encourage more cross-community interaction
- Reduced server permissions required: no more admin access for the bot!

## Setup

This guide is primarily focused on creating a new instance of the bot for a single server, however step 4 and onwards are 
also required for any additional Discord Servers added to the bot.

### Preparation

Before beginning setup, please enable Developer Mode (this can be found in Discord Settings > Advanced) and follow the steps 
outlined in the "Creating a Bot Account" section [of this guide](https://discordpy.readthedocs.io/en/stable/discord.html). 
The instructions below assume you will be using a cloud-based virtualization running some version of Linux for setup (such 
as Ubuntu or Oracle Linux), although it's entirely possible for you to run this bot on your personal computer if you wanted 
to. Oracle Cloud offer a free tier which is capable of running this bot without issue and a guide on how to use Oracle Cloud 
[can be found here](https://docs.oracle.com/en/learn/oci-basics-tutorial/#introduction). 

### Step One

Change to the directory you wish to save the Inhouse Bot repo and clone it with the following command:
```
git clone https://github.com/Samsquamptch/inhouse-bot-2.0.git
```
Install dependencies for the project
```
pip install -r requirements.txt
```
Move to the /credentials directory. Create an .env file simply called ".env". This will store your bot token and steam login 
credentials later on.

### Step Two

Move to the /src/data directory and run the ```data_manager.py``` file. This will detect you have no database and create 
a new one. Choose the "Update Bot Token" option when prompted and paste the Bot Token you created previously here. Once you 
have pressed enter and updated the Token, close this application by choosing the "exit" option.

### Step Three

Create an invitation link via the Developer Portal as outlined in [this guide](https://discordpy.readthedocs.io/en/stable/discord.html#inviting-your-bot). 
See the below image for the permissions the bot needs to run: <br>
[IMAGE NOT READY YET] <br>
Use the invite link to add the bot to the server you wish to run the inhouse from. Create the following four channels on 
the server in question:
- Admin Channel
- Queue Channel
- Global Queue Channel
- Chat Channel

These can be named whatever you wish (for example: ```admin-settings```, ```inhouse-queue```, ```global-queue```, and 
```inhouse-chat```). You will  also want to create some voice channels to go with these, such as ``Dire``, ```Radiant```, 
and ```Waiting Room```. You are now ready to run the bot and get started!

### Step Four

Copy the channel IDs of the four previously made channels and paste them somewhere for later use (such as a notepad file). 
Run the discord bot by moving to the /src/discord directory and running ```discord_client.py```. The bot should now be online 
on the server and is ready to be interacted with.

### Step Five

Run the ```!setup``` command in any channel of you choosing and follow the instructions. Input the required information 
and then press the confirm button to complete setup. The bot will now create the admin panel and inhouse queue, however 
it will be using default settings which may not be to your liking.

### Step Six

Open the Admin Channel and choose the ```Server Settings``` option from the select menu. Make any changes you wish and 
then close the window. You now have the base version of the inhouse bot set up and are ready to enable automated lobbies 
if you want.
