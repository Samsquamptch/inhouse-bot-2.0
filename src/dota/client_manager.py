import asyncio
import dota_db_interface
from src.dota.dota_client import DotaClient
import threading


class ClientManager:
    def __init__(self):
        self.bots = []

    async def check_for_active_lobbies(self):
        while True:
            print("looping")
            match_list = dota_db_interface.load_active_lobbies()
            if not match_list and self.bots:
                for lobby in self.bots:
                    lobby.stop()
                self.bots.clear()
                print("bots cleared")
            else:
                await self.check_lobby_exists(match_list)
            await asyncio.sleep(30)

    async def check_lobby_exists(self, match_list):
        if not self.bots:
            for match in match_list:
                await self.add_lobby(match)
            return
        for lobby in self.bots:
            with lobby.lock:
                if lobby.finished:
                    lobby.stop()
                    self.bots.remove(lobby)
        for match in match_list:
            lobby = next((x for x in self.bots if x.server == match[0]), None)
            if not lobby:
                await self.add_lobby(match)


    async def add_lobby(self, match):
        client = DotaClient(match[0], match[1])
        task = threading.Thread(target=client.start_bot)
        task.start()
        self.bots.append(client)
        print(f"{match[0]}: task started")

    def main(self):
        asyncio.run(self.check_for_active_lobbies())


manager = ClientManager()
manager.main()
