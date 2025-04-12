import asyncio
import dota_db_interface
from src.dota.dota_client import DotaClient


class ClientManager:
    def __init__(self):
        self.bots = []

    async def check_for_active_lobbies(self):
        while True:
            print("looping")
            match_list = dota_db_interface.load_active_lobbies()
            if not match_list and self.bots:
                self.bots.clear()
                print("bots cleared")
            else:
                self.check_lobby_exists(match_list)
            await asyncio.sleep(30)

    def check_lobby_exists(self, match_list):
        if not self.bots:
            for match in match_list:
                self.add_lobby(match)
            return
        for lobby in self.bots:
            if lobby.finished:
                self.bots.remove(lobby)
        for match in match_list:
            lobby = next((x for x in self.bots if x.server == match[0]), None)
            if not lobby:
                self.add_lobby(match)
        print(self.bots)

    def add_lobby(self, match):
        self.bots.append(DotaClient(match[0]))

    def main(self):
        asyncio.run(self.check_for_active_lobbies())


manager = ClientManager()
manager.main()
