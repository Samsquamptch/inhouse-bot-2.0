import discord


class EmbedSuperclass(discord.ui.View):
    def __init__(self, chat_channel, embed_channel, server):
        super().__init__(timeout=None)
        self.chat_channel = chat_channel
        self.embed_channel = embed_channel
        self.server = server
        self.message = None


