import discord

from src.discord import client_db_interface


class ChannelEmbeds(discord.ui.View):
    def __init__(self, chat_channel, embed_channel, server):
        super().__init__(timeout=None)
        self.chat_channel = chat_channel
        self.embed_channel = embed_channel
        self.server = server
        self.message = None


class QueueSettings:
    def __init__(self, server):
        queue_settings = client_db_interface.load_server_settings(server)
        self.afk_timer = queue_settings[0]
        self.mmr_floor = queue_settings[1]
        self.mmr_ceiling = queue_settings[2]
        self.queue_name = queue_settings[3]
