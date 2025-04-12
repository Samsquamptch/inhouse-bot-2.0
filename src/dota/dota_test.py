from steam.client import SteamClient, SteamID
from dota2.client import Dota2Client
import multiprocessing
from time import sleep
import dota2
import os
import sys
import dota_db_interface
import logging
from eventemitter import EventEmitter
from multiprocessing.connection import Client
import time
import pandas as pd
from sys import exit

class Status:
    def __init__(self):
        self.gameIDs = []
    def set_game(self, ids):
        self.gameIDs = ids
    def get_game(self):
        return self.gameIDs


stat = Status()
event = EventEmitter()

logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
(user, password) = connections.get_steam_credentials()
client = SteamClient()
dota = Dota2Client(client)
Manager = dota2.features.chat.ChannelManager(dota, 'logger')
    
@client.on('logged_on')
def start_dota():
    dota.launch()
    print("Running...")

@client.on('disconnected')
def kill_lobby():
    dota.destroy_lobby()

@dota.on('dota_welcome')
def startup_lobby(filler):
    dota.destroy_lobby()
    sleep(5)
    dota.emit('make_lobby')

# @dota.on('match_end')
# def renew_lobby(filler):
#     dota.destroy_lobby()
#     sleep(5)
#     dota.emit('make_lobby')

@dota.on('make_lobby')
def create_new_lobby():
    league_id = connections.get_league_id()
    opt = {
        'game_name': 'Doghouse Inhouse',
        'server_region': dota2.enums.EServerRegion.Europe,
        'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
        'leagueid': league_id,
        'fill_with_bots': False,
        'allow_spectating': True,
        'allow_cheats': False,
        'allchat': False,
        'dota_tv_delay': 0,
        'pause_setting': 0
    }
    dota.create_practice_lobby(password="woof", options=opt)
    dota.channels.join_lobby_channel()
    Manager.join_lobby_channel()
    # dota.join_practice_lobby_broadcast_channel(channel=1)


# @dota.on(dota2.features.Lobby.EVENT_LOBBY_NEW)
# def do_dota_wait(lobby):
#     dota.emit('start_queue', lobby)

@dota.on(dota2.features.Lobby.EVENT_LOBBY_CHANGED)
def print_state(lobby):
    if int(dota.lobby.state) == 0:
        print(str("UI"))
        players = []
        users = dota.lobby.all_members
        for user in users:
            if user.team == 1 or user.team == 0:
                players.append(user)
        if not players:
            print('No Players')
            return False
        elif len(players) == 10:
            dota.launch_practice_lobby()
        else:
            print("Number of players is only " + str(len(players)))
    elif int(dota.lobby.state) == 1:
        print(str("Setup"))
    elif int(dota.lobby.state) == 2:
        print(str("Run"))
    elif int(dota.lobby.state) == 3:
        print(str("End"))
        dota.emit('dota_welcome')

@Manager.on('message')
def message_check(c, message):
    print("message!")
    if message.text.startswith('!'):
        if message.text == '!start':
            print("test2")
            players = []
            users = dota.lobby.all_members
            for user in users:
                if user.team == 1 or user.team == 0:
                    players.append(user)
            if not players:
                print('No Players')
                return False
            elif len(players) == 10:
                dota.launch_practice_lobby()
            else:
                print("Number of players is only " + str(len(players)))

# @dota.on('starting_queue')
# def do_queue(lobby, idList):
#     dota.emit('queue_full', idList)
#     print('Queue Full...')

# @dota.on('queue_full')
# def dota_invite(ids):
#     print('Inviting...')
#     for i in ids:
#         print(SteamID(i))
#         print(f'inviting {i}')
#         print(i+76561197960265728)
#         dota.invite_to_lobby(i+76561197960265728)

# @dota.on('lobby_changed')
# def change_lobby(lobby):
#     pass
#
# @event.on('check_queue')
# def check_queue():
#     if os.path.isfile('data/activate.txt'):
#         dota.join_practice_lobby_team()
#         df = pd.DataFrame(pd.read_csv('data/match.csv'))
#         ids = list(df['steam'])
#         stat.set_game(ids)
#         os.remove('data/activate.txt')
#         dota.emit('queue_full', ids)
#     time.sleep(0.1)
#     event.emit('check_queue')
#

# def check_users():
#     pass

client.cli_login(username=user, password=password)
client.run_forever()
