import asyncio


class ClientManager:
    def __init__(self):
        self.global_lobby = None
        self.bots = []

    async def check_for_lobbies(self):
        while True:

            await asyncio.sleep(60)

    def main(self):
        asyncio.run(self.check_for_lobbies())


manager = ClientManager()
manager.main()
