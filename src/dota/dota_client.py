import asyncio
import logging
import threading

from steam.client import SteamClient
from dota2.client import Dota2Client
import dota2
import dota_db_interface
from dota2.enums import DOTA_GC_TEAM, EMatchOutcome
from time import sleep


class DotaClient:
    def __init__(self, server, match_id):
        self.server = server
        self.finished = False
        self.match_id = match_id
        self.player_list = []
        self.radiant_team = []
        self.dire_team = []
        self.lock = threading.Lock()
        self._stop_event = threading.Event()

    def start_bot(self):
        steam_login = dota_db_interface.load_server_steam(self.server)
        logging.basicConfig(filename=f'../../data/dota.log', format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.ERROR)
        client = SteamClient()
        dota = Dota2Client(client)
        manager = dota2.features.chat.ChannelManager(dota, 'logger')

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
            lobby_settings = dota_db_interface.load_dota_settings(self.server)
            opt = {
                'game_name': lobby_settings[0],
                'server_region': lobby_settings[2],
                'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
                'leagueid': lobby_settings[3],
                'fill_with_bots': False,
                'allow_spectating': True,
                'allow_cheats': False,
                'allchat': False,
                'dota_tv_delay': lobby_settings[4],
                'pause_setting': 0
            }
            dota.create_practice_lobby(password=lobby_settings[1], options=opt)
            sleep(2)
            self.player_list = dota_db_interface.return_queue_ids(self.match_id)


        @dota.on(dota2.features.Lobby.EVENT_LOBBY_NEW)
        def lobby_new(lobby):
            print('%s joined lobby %s' % (dota.steam.username, lobby.lobby_id))
            manager.join_lobby_channel()
            for player in self.player_list:
                dota.invite_to_lobby(player)

        @dota.on(dota2.features.Lobby.EVENT_LOBBY_CHANGED)
        def update_player_stats():
            if int(dota.lobby.state) == 3:
                if dota.lobby.match_outcome == EMatchOutcome.RadVictory:
                    dota_db_interface.update_match_records(self.radiant_team, self.dire_team, self.server)
                else:
                    dota_db_interface.update_match_records(self.dire_team, self.radiant_team, self.server)
                dota_db_interface.update_autolobby_status("MatchStatus", self.match_id)
                dota.destroy_lobby()
                with self.lock:
                    self.finished = True

        @manager.on('message')
        def message_check(c, message):
            if message.text == "start":
                players = []
                users = dota.lobby.all_members
                for user in users:
                    if user.team == 1 or user.team == 0:
                        players.append(user)
                for player in players:
                    if player.id not in self.player_list:
                        dota.channels.lobby.send("Kicking players who aren't in the queue")
                        dota.practice_lobby_kick(self.bit_converter(player.id))
                        return
                if len(players) < 10:
                    dota.channels.lobby.send("Not enough players to start, please fill all slots.")
                    return
                for player in players:
                    if player.team == 0:
                        self.radiant_team.append(self.bit_converter(player.id))
                    else:
                        self.dire_team.append(self.bit_converter(player.id))
                dota.channels.lobby.send("Starting match, good luck!")
                sleep(2)
                dota_db_interface.update_autolobby_status("LobbyStatus", self.match_id)
                dota.launch_practice_lobby()



        client.login(username=steam_login[0], password=steam_login[1])
        asyncio.to_thread(client.run_forever())

    def stop(self):
        self._stop_event.set()

    # In cases where the Dota ID and not the Steam ID are required, this converts them
    def bit_converter(self, player_id):
        return player_id - 76561197960265728
