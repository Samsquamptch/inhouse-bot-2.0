from discord.ext import tasks

from src.discord.inhouse_queue import InhouseActionState


class QueueManager:
    def __init__(self):
        self.embed_list = []
        self.full_embed_list = []
        self.full_queue = None

    def add_to_queue_list(self, embed):
        self.embed_list.append(embed)

    def remove_from_queue_list(self, embed):
        self.embed_list.remove(embed)

    @tasks.loop(seconds=30)
    async def check_full_queues(self):
        for embed in self.embed_list:
            if embed.team_list and embed not in self.full_embed_list:
                self.full_queue = embed
                await self.kick_user()
                self.full_embed_list.append(embed)
            elif not embed.team_list and embed in self.full_embed_list:
                self.full_embed_list.remove(embed)

    async def kick_user(self):
        for embed in self.embed_list:
            print(embed.server.name)
            if embed == self.full_queue:
                continue
            if embed.queue_full_time > self.full_queue.queue_full_time:
                continue
            full_queue_list = self.full_queue.queue_container.get_full_queue_players()
            for player in full_queue_list:
                gamer = embed.queue_container.user_in_queue(player)
                if not gamer:
                    continue
                embed.queue_container.remove_from_inhouse_queue(gamer)
                embed.action_state = InhouseActionState.OTHER_QUEUE
            await embed.update_message()

    @tasks.loop(minutes=1)
    async def autolobby_clear(self):
        pass
