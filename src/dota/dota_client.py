import asyncio
import logging
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

    async def start_bot(self):
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
            Manager.join_lobby_channel()

        @dota.on('match_end')
        def update_player_stats():
            if dota.lobby.match_outcome == EMatchOutcome.RadVictory:
                dota_db_interface.update_match_records(self.radiant_team, self.dire_team, self.server)
            else:
                dota_db_interface.update_match_records(self.dire_team, self.radiant_team, self.server)
            dota.destroy_lobby()
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
                        dota.practice_lobby_kick(player.id - 76561197960265728)
                        return
                if not players:
                    print("No players in queue")
                    return
                elif len(players) < 10:
                    print("Number of players is only " + str(len(players)))
                    return
                for player in players:
                    if player.team == 0:
                        self.radiant_team.append(player.id - 76561197960265728)
                    else:
                        self.dire_team.append(player.id - 76561197960265728)
                dota.launch_practice_lobby()



        client.login(username=steam_login[0], password=steam_login[1])
        await asyncio.to_thread(client.run_forever())
