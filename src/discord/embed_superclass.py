import discord

from src.discord import client_db_interface


class ChannelEmbeds(discord.ui.View):
    def __init__(self, server, chat_channel, embed_channel):
        super().__init__(timeout=None)
        self.server = server
        self.chat_channel = chat_channel
        self.embed_channel = embed_channel
        self.message = None


class DotaSettings:
    def __init__(self, server):
        server_settings = client_db_interface.load_dota_settings(server)
        self.lobby_name = server_settings[0]
        self.region = server_settings[1]
        self.league_id = server_settings[2]
        self.viewer_delay = server_settings[3]

class QueueSettings:
    def __init__(self, server):
        queue_settings = client_db_interface.load_discord_settings(server)
        self.afk_timer = queue_settings[0]
        self.mmr_floor = queue_settings[1]
        self.mmr_ceiling = queue_settings[2]
        self.ping_role = queue_settings[3]


class AdminPanelUserList:
    def __init__(self, server):
        self.server = server
        self.__user_list = []

    def start_list(self):
        unverified_list = client_db_interface.get_unverified_users(self.server)
        for user in unverified_list:
            discord_account = discord.utils.get(self.server.members, id=user[0])
            self.__user_list.append(ApprovalUser(discord_account, user[1], True))

    def add_user_to_list(self, user, mmr, is_registering):
        self.__user_list.append(ApprovalUser(user, mmr, is_registering))

    def remove_first_user(self):
        del self.__user_list[0]

    def list_contains_users(self):
        if self.__user_list:
            return True
        return False

    def get_first_user(self):
        return self.__user_list[0]


class ApprovalUser:
    def __init__(self, user, mmr, is_registering):
        self.id = user.id
        self.display_name = user.display_name
        self.avatar = user.avatar
        self.mmr = mmr
        self.is_registering = is_registering
