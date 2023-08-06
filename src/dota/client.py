from steam.client import SteamClient
from dota2.client import Dota2Client
import dota2
import os
import sys
sys.path.append(f'{os.getcwd()}/src/utils')
from connections import getCredentialsSteam
import logging

logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)

(user, password) = getCredentialsSteam()
client = SteamClient()
dota = Dota2Client(client)

@client.on('logged_on')
def start_dota():
    dota.launch()
    print("Running...")
#@dota.on('ready')
#def fetch_profile_card():
    #dota.request_profile_card(70388657)

@dota.on('dota_welcome')
def do_dota_stuff(filler):
    print(filler)
    opt = {
            'game_name': 'Doghouse Testing Lobby',
            'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
            'fill_with_bots': False,
            'allow_spectating': True,
            'allow_cheats': False,
            'allchat': False,
            'dota_tv_delay': 0,  # TODO: this is LobbyDotaTV_10
            'pause_setting': 0,  # TODO: LobbyDotaPauseSetting_Unlimited
        }
    dota.create_practice_lobby(password="sttsq1", options=opt)

@dota.on(dota2.features.Lobby.EVENT_LOBBY_NEW) 
def do_dota_invite(lobby):
    print("Inviting Teky...")
    dota.invite_to_lobby(76561198096488596)


client.cli_login(username=user, password=password)
client.run_forever()