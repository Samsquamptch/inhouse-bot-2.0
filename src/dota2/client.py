from steam.client import SteamClient
from dota2.client import Dota2Client

client = SteamClient()
dota = Dota2Client(client)

@client.on('logged_on')
def start_dota():
    dota.launch()
    print("Running...")
@dota.on('ready')
def fetch_profile_card():
    dota.request_profile_card(70388657)
@dota.on('profile_card')
def print_profile_card(account_id, profile_card):
    if account_id == 70388657:
        print(str(profile_card))
@dota.on('ready')
def do_dota_stuff():
    pass
    # talk to GC


client.cli_login()
client.run_forever()