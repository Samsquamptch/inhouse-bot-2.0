from steam.client import SteamClient
from dota2.client import Dota2Client
from time import sleep
import dota2
import logging
from datetime import date


def run_dota_bot():
    # logging.basicConfig(filename=f'../../data/{date.today()}.-dota.log', format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.DEBUG)
    (user, password) = discord_service.steam_login()
    client = SteamClient()
    dota = Dota2Client(client)
    Manager = dota2.features.chat.ChannelManager(dota, 'logger')
    server = discord_service.discord_credentials('SERVER')

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
        dota_settings = discord_service.load_config_data(server, 'DOTA')
        opt = {
            'game_name': dota_settings['lobby_name'],
            'server_region': dota_settings['server_region'],
            'game_mode': dota2.enums.DOTA_GameMode.DOTA_GAMEMODE_CM,
            'leagueid': dota_settings['league_id'],
            'fill_with_bots': False,
            'allow_spectating': True,
            'allow_cheats': False,
            'allchat': dota_settings['all_chat_enabled'],
            'dota_tv_delay': dota_settings['spectator_delay'],
            'pause_setting': 0
        }
        dota.create_practice_lobby(password="woof", options=opt)
        sleep(3)
        dota.channels.join_lobby_channel()
        Manager.join_lobby_channel()

    @dota.on(dota2.features.Lobby.EVENT_LOBBY_CHANGED)
    def print_state(lobby):
        if int(dota.lobby.state) == 3:
            discord_service.update_autolobby(server, [0, 1])
            print("Queue will be cleared")
            dota.destroy_lobby()
            sleep(10)
            dota.emit('make_lobby')
        elif int(dota.lobby.state) == 0:
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
            elif len(players) == 1:
                print('test')
                dota.destroy_lobby()
                sleep(10)
                client.disconnect()
            else:
                print("Number of players is only " + str(len(players)))

    client.login(username=user, password=password)
    client.run_forever()

run_dota_bot()
