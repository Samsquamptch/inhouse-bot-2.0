from enum import Enum

import discord.ui
from discord.ext import tasks
import client_db_interface
import datetime
import asyncio
from collections import defaultdict
from src.discord.embed_superclass import ChannelEmbeds, QueueSettings


class Gamer:
    def __init__(self, user, server, is_champion):
        self.id = user.id
        self.name = user.display_name
        self.last_action = datetime.datetime.now(tz=None)
        gamer_stats = client_db_interface.get_user_stats(user, server)
        self.steam = gamer_stats[1]
        self.mmr = gamer_stats[2]
        self.pos1 = gamer_stats[3]
        self.pos2 = gamer_stats[4]
        self.pos3 = gamer_stats[5]
        self.pos4 = gamer_stats[6]
        self.pos5 = gamer_stats[7]
        self.is_champion = is_champion


class VotekickSelect(discord.ui.UserSelect):
    def __init__(self, user_list):
        super().__init__(placeholder="Who do you want to kick?", max_values=1, min_values=0)
        self.player_list = user_list

    async def callback(self, interaction: discord.Interaction):
        selected_user = self.values[0]
        # gamer = next((x for x in self.player_list if x.id == selected_user.id), None)
        # if not gamer:
        #     interaction.response.send_message("User is not in the queue", ephemeral=True)
        #     return
        # if interaction.user.id not in gamer.vote_kick_list:
        #     gamer.vote_kick_list.append(interaction.user.id)
        interaction.response.defer()


class AfkCheckButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=290)
        self.check_user = None
        self.kick_user = True
        self.message = None

    async def send_buttons(self, channel):
        self.message = await channel.send(
            f"<@{self.check_user.id}>, please confirm you are here. You have five minutes to respond.", view=self,
            delete_after=600)

    async def on_timeout(self):
        self.press_button.disabled = True
        await self.message.edit(content=f"You took too long to respond, {self.check_user.display_name}!", view=self)
        self.stop()

    @discord.ui.button(label="I'm here!", emoji="👋", style=discord.ButtonStyle.green)
    async def press_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.check_user:
            await interaction.response.defer()
            return
        self.press_button.disabled = True
        self.kick_user = False
        await self.message.edit(content=f"Thank you for responding, {interaction.user.display_name}.", view=self)
        await interaction.response.defer()
        self.stop()


# Embed and buttons for the inhouse queue
class InhouseQueue(ChannelEmbeds, QueueSettings):
    def __init__(self, server, chat_channel, embed_channel, queue_embed):
        ChannelEmbeds.__init__(self, server, chat_channel, embed_channel)
        QueueSettings.__init__(self, server)
        self.queued_players = []
        self.votekick_dict = defaultdict(list)
        self.afk_dict = {}
        self.status = False
        self.admin_role = client_db_interface.load_admin_role(server)
        self.champion_role = client_db_interface.load_champion_role(server)
        self.queue_embed = queue_embed
        self.action_state = InhouseActionState.NONE
        self.queue_state = InhouseQueueState.EMPTY
        self.queue_popped = False

    @tasks.loop(minutes=1)
    async def match_end_check(self):
        print("Checking")
        # TODO: Update to check new autolobby system (when in use)
        # if client_db_interface.check_autolobby(self.server.id) == 0:
        #     await self.bot_clear_queue()
        # else:
        #     pass

    @tasks.loop(minutes=5)
    async def afk_check(self):
        if not self.queued_players:
            return
        print("loop has occurred")
        channel_messages = self.chat_channel.history(after=(datetime.datetime.now() - datetime.timedelta(minutes=self.afk_timer)))
        for gamer in self.queued_players:
            if self.queue_popped and self.queued_players.index(gamer) < 10:
                continue
            if gamer.last_action > datetime.datetime.now(tz=None) - datetime.timedelta(minutes=self.afk_timer):
                continue
            user_messages = [message async for message in channel_messages if message.author.id == gamer.id]
            if user_messages:
                continue
            else:
                gamer.last_action = datetime.datetime.now(tz=None)
                asyncio.create_task(self.afk_ping(gamer))

    async def afk_ping(self, gamer):
        user = discord.utils.get(self.server.members, id=gamer.id)
        afk_check_ping = AfkCheckButtons()
        afk_check_ping.check_user = user
        await afk_check_ping.send_buttons(self.chat_channel)
        await afk_check_ping.wait()
        if afk_check_ping.kick_user and len(self.queued_players) < 10:
            self.queued_players.remove(gamer)
            self.action_state = InhouseActionState.KICK
            await self.update_message(user)
            await self.chat_channel.send(f"<@{user.id}> has been kicked from the queue for being afk")
        else:
            gamer.last_action = datetime.datetime.now(tz=None)

    async def bot_clear_queue(self):
        if len(self.queued_players) < 10:
            return False
        del self.queued_players[:10]
        self.queue_popped = False
        self.votekick_dict.clear()
        if self.action_state != InhouseActionState.AUTOLOBBY:
            self.action_state = InhouseActionState.CLEAR
        return True

    async def send_embed(self):
        self.afk_check.start()
        self.queue_embed.set_title(self.queue_name)
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    def last_action_field(self, update_user=None):
        if self.action_state == InhouseActionState.NONE:
            pass
        elif self.action_state == InhouseActionState.AUTOLOBBY:
            self.queue_embed.add_field(name='', value=f'Queue was cleared by Autolobby')
        else:
            self.queue_embed.add_field(name='', value=update_user.display_name + self.action_state.value)

    def set_queue_state(self):
        if len(self.queued_players) >= 10:
            self.queue_state = InhouseQueueState.FULL
        elif len(self.queued_players) > 0:
            self.queue_state = InhouseQueueState.ACTIVE
        else:
            self.queue_state = InhouseQueueState.EMPTY

    async def queue_popped_notification(self):
        if not self.queue_popped:
            await self.chat_channel.send(f'Queue has popped, can the following users please head to the lobby: \n'
                                         f'<@{self.queued_players[0].id}> <@{self.queued_players[1].id}> <@{self.queued_players[2].id}>'
                                         f'<@{self.queued_players[3].id}> <@{self.queued_players[4].id}> <@{self.queued_players[5].id}>'
                                         f'<@{self.queued_players[6].id}> <@{self.queued_players[7].id}> <@{self.queued_players[8].id}>'
                                         f'<@{self.queued_players[9].id}>', delete_after=600)
            self.queue_popped = True

    async def update_message(self, update_user=None):
        self.set_queue_state()
        if self.queue_state == InhouseQueueState.FULL:
            self.queue_embed.full_queue(self.queued_players)
            # client_db_interface.update_autolobby(self.server.id, [1, 1])
            await self.queue_popped_notification()
        elif self.queue_state == InhouseQueueState.ACTIVE:
            self.queue_popped = False
            self.queue_embed.partial_queue(self.queued_players)
        elif self.queue_state == InhouseQueueState.EMPTY:
            self.queue_embed.empty_embed()
        self.last_action_field(update_user)
        await self.message.edit(embed=self.queue_embed, view=self)

    def check_user_can_join(self, interaction):
        user_verified, user_banned = client_db_interface.get_user_status(interaction.user, interaction.guild)
        if user_banned:
            return "You are currently banned from joining the queue"
        if not user_verified:
            return "Only verified users may join the queue"
        if interaction.user in self.queued_players:
            return "You are already queued"
        if not client_db_interface.user_within_mmr_range(interaction.user, self.mmr_floor, self.mmr_ceiling):
            return f"Your MMR is not within the range of {self.mmr_floor} and {self.mmr_ceiling}"
        return None

    def check_user_can_leave(self, gamer):
        if not gamer:
            return "You aren't in the queue"
        if len(self.queued_players) >= 10 > self.queued_players.index(gamer):
            return "You cannot leave when you need to play a game!"
        return None

    def user_is_admin(self, user):
        if self.admin_role not in user.roles:
            return "Queue can only be cleared by a server admin"
        if not self.bot_clear_queue():
            return "Queue clear function only works if queue is full"
        return None

    # Button to join the inhouse queue
    @discord.ui.button(label="Join Queue", emoji="✅", style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        denied_message = self.check_user_can_join(interaction)
        if denied_message:
            await interaction.response.send_message(content=denied_message, ephemeral=True, delete_after=5)
            return
        if self.champion_role in interaction.user.roles:
            is_champion = True
        else:
            is_champion = False
        while self.status:
            await asyncio.sleep(0.5)
        self.status = True
        self.queued_players.append(Gamer(interaction.user, interaction.guild, is_champion))
        self.action_state = InhouseActionState.JOIN
        await self.update_message(interaction.user)
        self.status = False
        await interaction.response.defer()

    # Button to leave the inhouse queue
    @discord.ui.button(label="Leave Queue", emoji="❌", style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        gamer = next((x for x in self.queued_players if x.id == interaction.user.id), None)
        denied_message = self.check_user_can_leave(gamer)
        if denied_message:
            await interaction.response.send_message(content=denied_message, ephemeral=True, delete_after=5)
            return
        while self.status:
            await asyncio.sleep(0.5)
        self.status = True
        self.queued_players.remove(gamer)
        self.action_state = InhouseActionState.LEAVE
        await self.update_message(interaction.user)
        self.status = False
        await interaction.response.defer()

    # Button to kick players from the inhouse queue
    @discord.ui.button(label="Clear Queue", emoji="🥾", style=discord.ButtonStyle.blurple)
    async def clear_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        denied_message = self.user_is_admin(interaction.user)
        if denied_message:
            await interaction.response.send_message(content=denied_message, ephemeral=True, delete_after=5)
            return
        await self.update_message(interaction.user)
        await interaction.response.send_message(content="Queue has been cleared", ephemeral=True)


class InhouseActionState(Enum):
    NONE: str = ""
    JOIN: str = " joined the queue"
    LEAVE: str = " left the queue"
    KICK: str = " was kicked from the queue"
    CLEAR: str = " cleared the queue"
    AUTOLOBBY: str = "Queue was cleared by Autolobby"


class InhouseQueueState(Enum):
    EMPTY: str = "Queue is Empty"
    ACTIVE: str = "Queue is Active"
    FULL: str = "Queue is Full"

    # async def vote_kick(self, kick_victim, vote_user, interaction=None):
    #     if kick_victim.id not in self.votekick_dict:
    #         self.votekick_dict[kick_victim.id].append(vote_user.id)
    #     elif kick_victim.id in self.votekick_dict and vote_user.id not in self.votekick_dict[kick_victim.id]:
    #         self.votekick_dict[kick_victim.id].append(vote_user.id)
    #     elif interaction:
    #         await interaction.response.send_message("You've already voted to kick that person!", ephemeral=True)
    #         return
    #     else:
    #         await self.embed_channel.send("You've already voted to kick that person!")
    #         return
    #     kick_votes = len(self.votekick_dict[kick_victim.id])
    #     if kick_votes == 3:
    #         if kick_victim.id in self.afk_dict:
    #             del self.afk_dict[kick_victim.id]
    #         self.queued_players.remove(kick_victim)
    #         del self.votekick_dict[kick_victim.id]
    #         await self.update_message(self.queued_players, self.server, 'Kick', kick_victim)
    #         await self.waiting_room_transfer(self.server)
    #         await self.embed_channel.send(f'{kick_victim} has been kicked from the queue',
    #                            delete_after=60)
    #     elif kick_votes < 3:
    #         num = 3 - kick_votes
    #         await self.embed_channel.send(f'{vote_user.display_name} wants to kick {kick_victim.display_name} from the queue! '
    #                            f'Votes required to kick: {num}', delete_after=60)
