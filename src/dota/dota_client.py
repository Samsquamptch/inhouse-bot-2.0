import asyncio
import logging
from steam.client import SteamClient
from dota2.client import Dota2Client
import dota2
import dota_db_interface
from dota2.enums import DOTA_GC_TEAM, EMatchOutcome, DOTAChatChannelType_t


class DotaClient:
    def __init__(self, server):
        self.server = server
        self.finished = False

    async def start_bot(self):
        steam_login = dota_db_interface.load_server_steam(self.server)
        logging.basicConfig(filename=f'../../data/dota.log', format='[%(asctime)s] %(levelname)s %(name)s: %(message)s', level=logging.ERROR)
        client = SteamClient()
        dota = Dota2Client(client)

        @client.on('logged_on')
        def start_dota():
            dota.launch()
            print("Running...")

        @dota.on('dota_welcome')
        async def startup_lobby(filler):
            dota.destroy_lobby()
            await asyncio.sleep(3)
            dota.emit('make_lobby')

        @dota.on('make_lobby')
        async def create_new_lobby():
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
            await asyncio.sleep(3)
            dota.channels.join_lobby_channel()

        @dota.on(dota2.features.Lobby.EVENT_LOBBY_CHANGED)
        async def print_state(lobby):
            if int(dota.lobby.state) == 3:
                print("Queue will be cleared")
                dota.destroy_lobby()
                await asyncio.sleep(3)
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
                    asyncio.sleep(3)
                    client.disconnect()
                else:
                    print("Number of players is only " + str(len(players)))

        @dota.channels.on(dota2.features.chat.ChannelManager.EVENT_MESSAGE)
        def chat_message(channel, msg_obj):
            if channel.type != DOTAChatChannelType_t.DOTAChannelType_Lobby:
                return

        client.login(username=steam_login[0], password=steam_login[1])
        await asyncio.to_thread(client.run_forever)
