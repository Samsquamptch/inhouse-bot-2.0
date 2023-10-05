from steam.client import SteamClient, SteamID
from dota2.client import Dota2Client
import multiprocessing
import dota2
import os
import sys
import connections
from connections import getCredentialsSteam
import logging
from eventemitter import EventEmitter
from multiprocessing.connection import Client
import time
import pandas as pd


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
(user, password) = getCredentialsSteam()
client = SteamClient()
dota = Dota2Client(client)
Manager = dota2.features.chat.ChannelManager(dota, 'logger')


@client.on('logged_on')
def start_dota():
    dota.launch()
    print("Running...")


# @dota.on('ready')
# def fetch_profile_card():
# dota.request_profile_card(70388657)

@client.on('disconnected')
def kill_lobby():
    dota.destroy_lobby()


@dota.on('dota_welcome')
def create_base_lobby(filler):
    dota.destroy_lobby()
    opt = {
        'game_name': 'Nest Test Lobby2',
        'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
        'fill_with_bots': False,
        'allow_spectating': True,
        'allow_cheats': False,
        'allchat': False,
        'dota_tv_delay': 0,  # TODO: this is LobbyDotaTV_10
        'pause_setting': 0,  # TODO: LobbyDotaPauseSetting_Unlimited
    }
    dota.create_practice_lobby(password="1", options=opt)
    dota.channels.join_lobby_channel()
    Manager.join_lobby_channel()
    dota.join_practice_lobby_team()  # jump to unassigned players
    event.emit('check_queue')


@dota.on(dota2.features.Lobby.EVENT_LOBBY_NEW)
def do_dota_wait(lobby):
    dota.emit('start_queue', lobby)


@dota.on('starting_queue')
def do_queue(lobby, id_list):
    dota.emit('queue_full', id_list)
    print('Queue Full...')


@dota.on('queue_full')
def dota_invite(ids):
    print('Inviting...')
    for i in ids:
        print(SteamID(i))
        print(f'inviting {i}')
        print(i + 76561197960265728)
        dota.invite_to_lobby(i + 76561197960265728)


@dota.on('lobby_changed')
def change_lobby(lobby):
    pass


@event.on('check_queue')
def check_queue():
    if os.path.isfile('data/activate.txt'):
        dota.join_practice_lobby_team()
        df = pd.DataFrame(pd.read_csv('data/match.csv'))
        ids = list(df['steam'])
        stat.set_game(ids)
        os.remove('data/activate.txt')
        dota.emit('queue_full', ids)
    time.sleep(0.1)
    event.emit('check_queue')


@Manager.on('message')
def message_check(c, message):
    if message.text.startswith('!'):
        if message.text == '!start':
            player_list = dota.lobby.all_members
            players = [x for x in player_list if x.team == 1 or x.team == 0]
            # for user in player_list:
            #     if user.team == 1 or user.team == 0:
            #         players.append(user)
            if not players:
                print('No Players')
                return False
            for player in players:
                print(SteamID(player.id).as_32)
                print(stat.get_game())
                if SteamID(player.id).as_32 not in stat.get_game():
                    return False
            if len(players) == 10:
                dota.launch_practice_lobby()


def check_users():
    pass


client.cli_login(username=user, password=password)
client.run_forever()
