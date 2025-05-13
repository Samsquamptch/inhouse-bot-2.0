import asyncio
import logging
from steam.client import SteamClient
from dota2.client import Dota2Client
import dota2
import dota_db_interface
from dota2.enums import DOTA_GC_TEAM, EMatchOutcome
from time import sleep


class DotaClient:
    def __init__(self, server):
        self.server = server
        self.finished = False
        self.player_list = [76561197988972789]

    async def start_bot(self):
        steam_login = dota_db_interface.load_server_steam(self.server)
        logging.basicConfig(filename=f'../../data/dota.log', format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.ERROR)
        client = SteamClient()
        dota = Dota2Client(client)
        Manager = dota2.features.chat.ChannelManager(dota, 'logger')

        @client.on('logged_on')
        def start_dota():
            dota.launch()
            print("Running...")

        @dota.on('dota_welcome')
        def startup_lobby(filler):
            dota.destroy_lobby()
            sleep(3)
            dota.emit('make_lobby')

        @dota.on('make_lobby')
        def create_new_lobby():
            opt = {
                'game_name': 'test lobby',
                'server_region': 8,
                'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
                'leagueid': 17134,
                'fill_with_bots': False,
                'allow_spectating': True,
                'allow_cheats': False,
                'allchat': False,
                'dota_tv_delay': 2,
                'pause_setting': 0
            }
            dota.create_practice_lobby(password="woof", options=opt)
            sleep(5)


        @dota.on(dota2.features.Lobby.EVENT_LOBBY_NEW)
        def lobby_new(lobby):
            print('%s joined lobby %s' % (dota.steam.username, lobby.lobby_id))
            Manager.join_lobby_channel()

        @dota.on(dota2.features.Lobby.EVENT_LOBBY_CHANGED)
        def print_state(lobby):
            if int(dota.lobby.state) == 3:
                print("Queue will be cleared")
                if dota.lobby.match_outcome == EMatchOutcome.RadVictory:
                    pass
                else:
                    pass
                dota.destroy_lobby()
                sleep(3)
                dota.emit('make_lobby')

        @Manager.on('message')
        def message_check(c, message):
            print(message)
            if message.text == "start":
                players = []
                users = dota.lobby.all_members
                for user in users:
                    if user.team == 1 or user.team == 0:
                        players.append(user)
                for player in players:
                    if player.id not in self.player_list:
                        dota.practice_lobby_kick(player.id - 76561197960265728)
                        return
                if not players:
                    print("No players in queue")
                elif len(players) == 10:
                    dota.launch_practice_lobby()
                else:
                    print("Number of players is only " + str(len(players)))


        client.login(username=steam_login[0], password=steam_login[1])
        await asyncio.to_thread(client.run_forever())
