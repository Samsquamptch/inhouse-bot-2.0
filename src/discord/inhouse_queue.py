from enum import Enum
import discord.ui
from discord.ext import tasks
import client_db_interface
from _datetime import datetime, timedelta
import asyncio

from src.discord import team_balancer, validate_user
from src.discord.embed_superclass import ChannelEmbeds, QueueSettings


class Gamer:
    def __init__(self, user, server, is_champion):
        self.id = user.id
        self.name = user.display_name
        self.last_action = datetime.now(tz=None)
        gamer_stats = client_db_interface.get_user_stats(user, server)
        self.steam = gamer_stats[1]
        self.mmr = gamer_stats[2]
        role_pref = [gamer_stats[3], gamer_stats[4], gamer_stats[5], gamer_stats[6], gamer_stats[7]]
        self.role_preference = validate_user.check_role_priority(role_pref)
        self.is_champion = is_champion


class VoteKickVictim:
    def __init__(self, victim, voter):
        self.victim = victim
        self.vote_list = [voter]

    def add_vote(self, voter):
        self.vote_list.append(voter)


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


class QueueList:
    def __init__(self, player_list):
        self.queued_players = player_list
        self.team_list = []
        self.vote_kick_list = []


# Embed and buttons for the inhouse queue
class InhouseQueueEmbed(ChannelEmbeds, QueueSettings):
    def __init__(self, server, chat_channel, embed_channel, queue_embed):
        ChannelEmbeds.__init__(self, server, chat_channel, embed_channel)
        QueueSettings.__init__(self, server)
        self.queued_players = []
        self.action_status = False
        self.admin_role = client_db_interface.load_admin_role(server)
        self.champion_role = client_db_interface.load_champion_role(server)
        self.queue_embed = queue_embed
        self.action_state = InhouseActionState.NONE
        self.queue_state = InhouseQueueState.EMPTY
        self.queue_full_time = datetime.now(tz=None)
        self.team_list = []
        self.vote_kick_list = []
        self.last_ping = datetime.now(tz=None)

    @tasks.loop(minutes=1)
    async def match_end_check(self):
        print("Checking")
        # TODO: Update to check new autolobby system (when in use)
        # if client_db_interface.check_autolobby(self.server.id) == 0:
        #     await self.bot_clear_queue()
        # else:
        #     pass

    @tasks.loop(minutes=10)
    async def inhouse_role_ping(self):
        current_time = datetime.now(tz=None)
        if current_time - timedelta(minutes=10) > self.last_ping:
            await self.chat_channel.send(f"<@&{self.ping_role}> +{10 - len(self.queued_players)} users needed for an inhouse game!")
            self.last_ping = current_time

    @tasks.loop(minutes=5)
    async def afk_check(self):
        current_time = datetime.now(tz=None)
        channel_messages = self.chat_channel.history(
            after=(current_time - timedelta(minutes=self.afk_timer)))
        for gamer in reversed(self.queued_players):
            if self.team_list and self.queued_players.index(gamer) < 10:
                break
            if gamer.last_action > current_time - timedelta(minutes=self.afk_timer):
                continue
            user_messages = [message async for message in channel_messages if message.author.id == gamer.id]
            if not user_messages:
                gamer.last_action = current_time
                asyncio.create_task(self.afk_ping(gamer))

    async def afk_ping(self, gamer):
        user = discord.utils.get(self.server.members, id=gamer.id)
        afk_check_ping = AfkCheckButtons()
        afk_check_ping.check_user = user
        await afk_check_ping.send_buttons(self.chat_channel)
        await afk_check_ping.wait()
        if afk_check_ping.kick_user:
            self.queued_players.remove(gamer)
            self.action_state = InhouseActionState.KICK
            await self.update_message(user)
            await self.chat_channel.send(f"<@{user.id}> has been kicked from the queue for being afk")
        else:
            gamer.last_action = datetime.now(tz=None)

    async def bot_clear_queue(self):
        if len(self.queued_players) < 10:
            return False
        del self.queued_players[:10]
        self.team_list.clear()
        self.vote_kick_list.clear()
        if self.action_state != InhouseActionState.AUTOLOBBY:
            self.action_state = InhouseActionState.CLEAR
        return True

    async def send_embed(self):
        self.message = await self.embed_channel.send(view=self)
        await self.update_message()

    def last_action_field(self, update_user=None):
        if self.action_state == InhouseActionState.NONE:
            pass
        elif self.action_state == InhouseActionState.AUTOLOBBY or InhouseActionState.OTHER_QUEUE:
            self.queue_embed.add_field(name='', value=self.action_state.value)
        else:
            self.queue_embed.add_field(name='', value=update_user.name + self.action_state.value)

    def set_queue_state(self):
        if len(self.queued_players) >= 10:
            self.queue_state = InhouseQueueState.FULL
        elif len(self.queued_players) > 0:
            self.queue_state = InhouseQueueState.ACTIVE
        else:
            self.queue_state = InhouseQueueState.EMPTY

    async def notify_gamers(self):
        send_message = 'Queue has popped, can the following users please head to the lobby: \n'
        for player in self.queued_players[:10]:
            send_message += f'<@{player.id}> '
        await self.chat_channel.send(send_message, delete_after=600)

    async def update_message(self, update_user=None):
        self.set_queue_state()
        if self.queue_state == InhouseQueueState.FULL:
            if not self.team_list:
                self.queue_full_time = datetime.now(tz=None)
                team_ids = (x.id for x in self.queued_players[:10])
                self.team_list = team_balancer.assign_teams(team_ids)
                await self.notify_gamers()
            self.queue_embed.full_queue(self.queued_players, self.team_list)
            # client_db_interface.update_autolobby(self.server.id, [1, 1])
        elif self.queue_state == InhouseQueueState.ACTIVE:
            self.team_list.clear()
            self.vote_kick_list.clear()
            self.queue_embed.partial_queue(self.queued_players)
            await self.update_inhouse_ping()
        elif self.queue_state == InhouseQueueState.EMPTY:
            self.queue_embed.empty_embed()
        self.last_action_field(update_user)
        self.update_votekick_select()
        self.update_afk_checker()
        await self.message.edit(embed=self.queue_embed, view=self)

    async def update_inhouse_ping(self):
        if not self.ping_role:
            return
        if len(self.queued_players) < 6:
            self.inhouse_role_ping.stop()
        elif not self.inhouse_role_ping.get_task():
            self.inhouse_role_ping.start()

    def check_user_can_join(self, interaction):
        user_status = client_db_interface.get_user_status(interaction.user, interaction.guild)
        if user_status != "verified":
            return "Only verified users may join the queue"
        if user_status == "banned":
            return "You are currently banned from joining the queue"
        gamer = next((x for x in self.queued_players if x.id == interaction.user.id), None)
        if gamer:
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

    def update_afk_checker(self):
        if self.queue_state == InhouseQueueState.EMPTY:
            print("afk check stopped on " + self.server.name)
            self.afk_check.stop()
        elif not self.afk_check.get_task():
            print("afk check started on " + self.server.name)
            self.afk_check.start()

    def update_votekick_select(self):
        if self.queue_state == InhouseQueueState.FULL:
            self.select_votekick.disabled = False
            self.select_votekick.placeholder = "Select a User to Votekick"
            self.select_votekick.options.clear()
            for gamer in self.queued_players[:10]:
                self.select_votekick.add_option(label=gamer.name, value=gamer.id, description=f"Votekick {gamer.name}")
        else:
            self.select_votekick.disabled = True
            self.select_votekick.placeholder = "Votekick Disabled"

    @discord.ui.button(label="Join Queue", emoji="✅", style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        denied_message = self.check_user_can_join(interaction)
        if denied_message:
            await interaction.response.send_message(content=denied_message, ephemeral=True, delete_after=5)
            return
        if self.champion_role and self.champion_role in interaction.user.roles:
            is_champion = True
        else:
            is_champion = False
        while self.action_status:
            await asyncio.sleep(0.5)
        self.action_status = True
        self.queued_players.append(Gamer(interaction.user, interaction.guild, is_champion))
        self.action_state = InhouseActionState.JOIN
        await self.update_message(interaction.user)
        self.action_status = False
        await interaction.response.defer()

    @discord.ui.button(label="Leave Queue", emoji="❌", style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        gamer = next((x for x in self.queued_players if x.id == interaction.user.id), None)
        denied_message = self.check_user_can_leave(gamer)
        if denied_message:
            await interaction.response.send_message(content=denied_message, ephemeral=True, delete_after=5)
            return
        while self.action_status:
            await asyncio.sleep(0.5)
        self.action_status = True
        self.queued_players.remove(gamer)
        self.action_state = InhouseActionState.LEAVE
        await self.update_message(interaction.user)
        self.action_status = False
        await interaction.response.defer()

    @discord.ui.button(label="Clear Queue", emoji="🥾", style=discord.ButtonStyle.blurple)
    async def clear_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        denied_message = self.user_is_admin(interaction.user)
        if denied_message:
            await interaction.response.send_message(content=denied_message, ephemeral=True, delete_after=5)
            return
        await self.update_message(interaction.user)
        await interaction.response.send_message(content="Queue has been cleared", ephemeral=True)

    @discord.ui.select(placeholder="Votekick", min_values=0, max_values=1, options=[
        discord.SelectOption(label="Blank", value="Search",
                             description="Test")])
    async def select_votekick(self, interaction: discord.Interaction, select: discord.ui.Select):
        if not select.values:
            await interaction.response.defer()
            return
        victim_id = select.values[0]
        gamer = next((x for x in self.queued_players if x.id == int(victim_id)), None)
        if self.admin_role in interaction.user.roles:
            self.queued_players.remove(gamer)
            self.action_state = InhouseActionState.KICK
            await self.update_message(gamer)
            await interaction.response.send_message("User has been kicked", ephemeral=True)
            return
        voter = next((x for x in self.queued_players if x.id == interaction.user.id), None)
        if voter not in self.queued_players[:10]:
            await interaction.response.send_message("You have to be in the queue to vote kick!", ephemeral=True)
            return
        kick_victim = next((x for x in self.vote_kick_list if x.victim == gamer), None)
        if not kick_victim:
            self.vote_kick_list.append(VoteKickVictim(gamer, voter))
        elif voter in kick_victim.vote_list:
            pass
        elif len(kick_victim.vote_list) >= 2:
            self.vote_kick_list.remove(kick_victim)
            self.queued_players.remove(gamer)
            self.action_state = InhouseActionState.KICK
            await self.update_message(gamer)
        else:
            kick_victim.add_vote(voter)
        await interaction.response.send_message(f"You have voted to kick {gamer.name}, {3 - len(kick_victim.vote_list)} "
                                                f"more votes needed to kick them.", ephemeral=True)


class InhouseActionState(Enum):
    NONE: str = ""
    JOIN: str = " joined the queue"
    LEAVE: str = " left the queue"
    KICK: str = " was kicked from the queue"
    CLEAR: str = " cleared the queue"
    AUTOLOBBY: str = "Queue was cleared by Autolobby"
    OTHER_QUEUE: str = "Users from other full queue were removed"


class InhouseQueueState(Enum):
    EMPTY: str = "Queue is Empty"
    ACTIVE: str = "Queue is Active"
    FULL: str = "Queue is Full"
