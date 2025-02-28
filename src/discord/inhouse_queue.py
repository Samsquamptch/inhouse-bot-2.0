import discord
from discord.ext import tasks
import client_db_interface
import check_user
import datetime
import asyncio
from zoneinfo import ZoneInfo
from collections import defaultdict
from src.discord import team_balancer, embed_superclass
from src.discord.menu_user_options import SelectUserView, SelectUserEmbed


class VotekickSelect(discord.ui.UserSelect):
    def __init__(self, user_list):
        super().__init__(placeholder="Who do you want to kick?", max_values=1, min_values=0)
        self.player_list = user_list


    async def callback(self, interaction: discord.Interaction):
        user = self.values[0]
        if user not in self.player_list:
            interaction.response.send_message("User is not in the queue", ephemeral=True)


# The modal for users to votekick when the queue is full. Will be left for a later date
# class VoteKickPlayerModal(discord.ui.Modal, title='Votekick User in Queue'):
#     def __init__(self):
#         super().__init__()
#         self.user_acc = None
#         self.user_name = ""
#
#     player_name = discord.ui.TextInput(label='User\'s global name or username', min_length=3)
#
#     async def on_submit(self, interaction: discord.Interaction):
#         server = interaction.guild
#         self.user_name = str(self.player_name)
#         check_if_exists = check_user.user_exists(server, self.user_name)
#         if not check_if_exists[0]:
#             self.user_acc = None
#             await interaction.response.defer()
#         else:
#             self.user_acc = check_if_exists[1]
#             await interaction.response.defer()
#         self.stop()
#
#
# # The modal for admins to kick users from the queue. Full usernames or global nicknames must be used for this to work
# class AdminKickPlayerModal(VoteKickPlayerModal, title='Kick User in Queue'):
#     def __init__(self):
#         super().__init__()
#         self.clear_users = False
#
#     async def on_submit(self, interaction: discord.Interaction):
#         server = interaction.guild
#         self.user_name = str(self.player_name)
#         if self.user_name.lower() == "all" or self.user_name.lower() == "clear":
#             self.clear_users = True
#             await interaction.response.defer()
#         else:
#             check_if_exists = check_user.user_exists(server, self.user_name)
#             if not check_if_exists[0]:
#                 self.user_acc = None
#                 await interaction.response.defer()
#             else:
#                 self.user_acc = check_if_exists[1]
#                 await interaction.response.defer()
#         self.stop()


class AfkCheckButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
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

    @discord.ui.button(label="I'm here!", emoji="👋",
                       style=discord.ButtonStyle.green)
    async def press_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.check_user:
            self.press_button.disabled = True
            self.kick_user = False
            await self.message.edit(content=f"Thank you for responding, {interaction.user.display_name}.", view=self)
            await interaction.response.defer()
            self.stop()
        else:
            await interaction.response.defer()


# class WaitingRoom(discord.ui.View):
#     def __init__(self, server, embed_channel):
#         super().__init__(timeout=None)
#         self.waiting_list = []
#         self.embed_channel = embed_channel
#         self.message = None
#         self.server = server
#
#     async def send_embed(self):
#         self.message = await self.embed_channel.send("Users in the waiting room are below", view=self)
#         await self.update_message()
#
#     def create_embed(self, queue_list):
#         if queue_list:
#             embed_desc = f"{len(queue_list)} People currently in waiting list"
#             embed_clr = 0x00ff00
#         else:
#             embed_desc = "Waiting list is currently empty"
#             embed_clr = 0xFF0000
#         queue_embed = discord.Embed(title="Inhouse Waiting List", description=f'{embed_desc}',
#                                     color=embed_clr)
#         for user in queue_list:
#             user_data = client_db_interface.view_user_data(user.id)
#             queue_embed.add_field(name=user.display_name, value=f'MMR: {user_data[2]}', inline=True)
#         update_time = datetime.datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
#         queue_embed.set_footer(text=f'Waiting list updated at: {update_time}')
#         return queue_embed
#
#     async def delete_message(self):
#         try:
#             await self.message.delete()
#         except discord.errors.NotFound:
#             pass
#         except AttributeError:
#             pass
#
#     async def update_message(self):
#         await self.message.edit(embed=self.create_embed(self.waiting_list), view=self)


# Embed and buttons for the inhouse queue
class InhouseQueue(embed_superclass.ChannelEmbeds, embed_superclass.QueueSettings):
    def __init__(self, server, chat_channel, embed_channel, afk_timer, mmr_floor, mmr_ceiling, queue_name):
        embed_superclass.ChannelEmbeds.__init__(self, chat_channel, embed_channel, server)
        embed_superclass.QueueSettings(server)
        self.queued_players = []
        self.votekick_dict = defaultdict(list)
        self.afk_dict = {}
        self.afk_timer = afk_timer
        self.mmr_floor = mmr_floor
        self.mmr_ceiling = mmr_ceiling
        self.queue_name = queue_name
        self.status = False
        self.admin_role = client_db_interface.load_admin_role(server)
        self.champion_role = client_db_interface.load_champion_role(server)

    async def vote_kick(self, kick_victim, vote_user, interaction=None):
        if kick_victim.id not in self.votekick_dict:
            self.votekick_dict[kick_victim.id].append(vote_user.id)
        elif kick_victim.id in self.votekick_dict and vote_user.id not in self.votekick_dict[kick_victim.id]:
            self.votekick_dict[kick_victim.id].append(vote_user.id)
        elif interaction:
            await interaction.response.send_message("You've already voted to kick that person!", ephemeral=True)
            return
        else:
            await self.embed_channel.send("You've already voted to kick that person!")
            return
        kick_votes = len(self.votekick_dict[kick_victim.id])
        if kick_votes == 3:
            if kick_victim.id in self.afk_dict:
                del self.afk_dict[kick_victim.id]
            self.queued_players.remove(kick_victim)
            del self.votekick_dict[kick_victim.id]
            await self.update_message(self.queued_players, self.server, 'Kick', kick_victim)
            await self.waiting_room_transfer(self.server)
            await self.embed_channel.send(f'{kick_victim} has been kicked from the queue',
                               delete_after=60)
        elif kick_votes < 3:
            num = 3 - kick_votes
            await self.embed_channel.send(f'{vote_user.display_name} wants to kick {kick_victim.display_name} from the queue! '
                               f'Votes required to kick: {num}', delete_after=60)

    @tasks.loop(minutes=5)
    async def afk_check(self):
        channel_messages = self.chat_channel.history(
            after=(datetime.datetime.now() - datetime.timedelta(minutes=self.afk_timer)))
        if self.queued_players and len(self.queued_players) < 10:
            for user in self.queued_players:
                user_messages = [message async for message in channel_messages if message.author.id == user.id]
                if self.afk_dict[user.id] > datetime.datetime.now(tz=None) - datetime.timedelta(
                        minutes=self.afk_timer):
                    continue
                if user_messages:
                    continue
                else:
                    self.afk_dict[user.id] = datetime.datetime.now(tz=None)
                    asyncio.create_task(self.afk_ping(user))

    @tasks.loop(minutes=1)
    async def match_end_check(self):
        print("Checking")
        # TODO: Update to check new autolobby system (when in use)
        # if client_db_interface.check_autolobby(self.server.id) == 0:
        #     await self.bot_clear_queue()
        # else:
        #     pass

    async def afk_ping(self, user):
        afk_check_ping = AfkCheckButtons()
        afk_check_ping.check_user = user
        await afk_check_ping.send_buttons(self.chat_channel)
        await afk_check_ping.wait()
        if afk_check_ping.kick_user and len(self.queued_players) < 10:
            del self.afk_dict[user.id]
            self.queued_players.remove(user)
            await self.update_message(self.queued_players, self.server, 'Kick', user)
            await self.chat_channel.send(f"<@{user.id}> has been kicked from the queue for being afk")
        else:
            self.afk_dict[user.id] = datetime.datetime.now(tz=None)

    async def bot_clear_queue(self, interaction=None):
        self.afk_dict.clear()
        self.votekick_dict.clear()
        self.queued_players.clear()
        if (interaction == None):
            await self.update_message(self.queued_players, 'Autolobby')
        else:
            await self.update_message(self.queued_players, 'Clear', interaction.user)
            await interaction.followup.send(content=f'queue has been cleared', ephemeral=True)
        self.match_end_check.stop()
        await self.waiting_room_transfer()

    async def send_embed(self):
        self.afk_check.start()
        self.message = await self.embed_channel.send(view=self)
        await self.update_message(self.queued_players, self.server)

    def full_queue_embed(self, queue_list):
        queue_ids = [user.id for user in queue_list]
        queue_roles = ["Carry", "Midlane", "Offlane", "Soft Supp", "Hard Supp"]
        queue_teams = team_balancer.assign_teams(queue_ids)
        queue_embed = discord.Embed(title=f"{self.queue_name} QUEUE", description=f'Queue is full, please join the lobby!',
                                    color=0x00ff00)
        icon_url = self.server.icon.url
        queue_embed.set_thumbnail(url=f'{icon_url}')
        queue_embed.add_field(name='Roles', value='', inline=True)
        queue_embed.add_field(name='Radiant', value='', inline=True)
        queue_embed.add_field(name='Dire', value='', inline=True)
        radiant_team = queue_teams[0]
        dire_team = queue_teams[1]
        x = 0
        mmr_total_radiant = 0
        mmr_total_dire = 0
        while x < 5:
            user_acc_radiant = discord.utils.get(self.server.members, id=radiant_team[x])
            user_acc_dire = discord.utils.get(self.server.members, id=dire_team[x])
            user_radiant = client_db_interface.view_user_data(radiant_team[x])
            user_dire = client_db_interface.view_user_data(dire_team[x])
            mmr_total_radiant = mmr_total_radiant + user_radiant[2]
            mmr_total_dire = mmr_total_dire + user_dire[2]
            queue_embed.add_field(name=f'{queue_roles[x]}',
                                  value='\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC\u1CBC',
                                  inline=True)
            queue_embed.add_field(name=user_acc_radiant.display_name,
                                  value=f'MMR: {user_radiant[2]} \u1CBC\u1CBC\u1CBC\u1CBC\u1CBC \n'
                                        f'[Dotabuff](https://www.dotabuff.com/players/{user_radiant[1]})',
                                  inline=True)
            queue_embed.add_field(name=user_acc_dire.display_name,
                                  value=f'MMR: {user_dire[2]} \n'
                                        f'[Dotabuff](https://www.dotabuff.com/players/{user_dire[1]})',
                                  inline=True)
            x += 1
        mmr_avg_radiant = mmr_total_radiant / 5
        mmr_avg_dire = mmr_total_dire / 5
        queue_embed.add_field(name=f'Average MMR', value='', inline=True)
        queue_embed.add_field(name=f'{mmr_avg_radiant}', value='', inline=True)
        queue_embed.add_field(name=f'{mmr_avg_dire}', value='', inline=True)
        update_time = datetime.datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
        queue_embed.add_field(name='Players',
                              value=f'<@{radiant_team[0]}> <@{radiant_team[1]}> <@{radiant_team[2]}> <@{radiant_team[3]}>'
                                    f'<@{radiant_team[4]}> <@{dire_team[0]}> <@{dire_team[1]}> <@{dire_team[2]}> <@{dire_team[3]}>'
                                    f'<@{dire_team[4]}>')
        queue_embed.set_footer(text=f'Teams created at: {update_time}')
        return queue_embed

    # Creates the embed used for displaying the inhouse queue
    def create_embed(self, action=None, action_user=None):
        if self.queued_players:
            #TODO: Tidy this up
            if self.champion_role:
                champion_check = any(check in self.queued_players for check in self.champion_role.members)
                if champion_check:
                    embed_desc = f"A champion is in the queue!"
                    embed_clr = 0xFFD70
                else:
                    embed_desc = f"Queue is live, come join!"
                    embed_clr = 0x00ff00
            else:
                embed_desc = f"Queue is live, come join!"
                embed_clr = 0x00ff00
        else:
            embed_desc = "The queue is currently empty. You can change this!"
            embed_clr = 0xFF0000
        queue_embed = discord.Embed(title=f"{self.queue_name} QUEUE", description=f'{embed_desc}',
                                    color=embed_clr)
        queue_length = len(self.queued_players)
        match queue_length:
            case 0:
                queue_embed.add_field(name=f'No one is in the queue', value='', inline=False)
            case 1:
                queue_embed.add_field(name=f'1 player in queue', value='', inline=False)
            case _:
                queue_embed.add_field(name=f'{queue_length} players in queue', value='', inline=False)
        icon_url = self.server.icon.url
        queue_embed.set_thumbnail(url=f'{icon_url}')
        mmr_total = 0
        for user in self.queued_players:
            user_data = client_db_interface.view_user_data(user.id)
            mmr_total = mmr_total + user_data[2]
            role_preference = check_user.check_role_priority(user_data)
            queue_embed.add_field(name=user.display_name,
                                  value=f'MMR: {user_data[2]} | [Dotabuff](https://www.dotabuff.com/players/{user_data[1]}) | Preference: {role_preference}',
                                  inline=False)
        update_time = datetime.datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
        match action:
            case 'Join':
                queue_embed.add_field(name='', value=f'{action_user.display_name} joined the queue')
            case 'Leave':
                queue_embed.add_field(name='', value=f'{action_user.display_name} left the queue')
            case 'Kick':
                queue_embed.add_field(name='', value=f'{action_user.display_name} was kicked from queue')
            case 'Clear':
                queue_embed.add_field(name='', value=f'Queue was cleared by {action_user.display_name}')
            case 'Autlobby':
                queue_embed.add_field(name='', value=f'Queue was cleared by Autolobby')
            case _:
                pass
        if self.queued_players:
            average_mmr = int(mmr_total / len(self.queued_players))
            queue_embed.set_footer(text=f'Queue updated at: {update_time} | Average MMR: {average_mmr}')
        else:
            queue_embed.set_footer(text=f'Queue updated at: {update_time}')
        return queue_embed

    async def update_message(self, action=None, update_user=None):
        if len(self.queued_players) >= 10:
            await self.message.edit(embed=self.full_queue_embed(self.queued_players), view=self)
            # client_db_interface.update_autolobby(self.server.id, [1, 1])
            print("Loaded")
            await self.chat_channel.send(f'Queue has popped, can the following users please head to the lobby: \n'
                               f'<@{self.queued_players[0].id}> <@{self.queued_players[1].id}> <@{self.queued_players[2].id}>'
                               f'<@{self.queued_players[3].id}> <@{self.queued_players[4].id}> <@{self.queued_players[5].id}>'
                               f'<@{self.queued_players[6].id}> <@{self.queued_players[7].id}> <@{self.queued_players[8].id}>'
                               f'<@{self.queued_players[9].id}>', delete_after=600)
            # self.match_end_check.start()
        else:
            # self.match_end_check.stop()
            await self.message.edit(embed=self.create_embed(action, update_user), view=self)


    # Button to join the inhouse queue
    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_verified, user_banned = client_db_interface.get_user_status(interaction.user, interaction.guild)
        if user_banned:
            await interaction.response.send_message(content="You are currently banned from joining the queue",
                                                    ephemeral=True, delete_after=5)
        elif user_verified:
            self.afk_dict[interaction.user.id] = datetime.datetime.now(tz=None)
            while self.status:
                await asyncio.sleep(1)
            if interaction.user in self.queued_players:
                await interaction.response.send_message(content="You are already queued", ephemeral=True,
                                                        delete_after=5)
            self.status = True
            self.queued_players.append(interaction.user)
            await self.update_message(self.queued_players, 'Join', interaction.user)
            self.status = False
            await interaction.response.defer()
        else:
            await interaction.response.send_message(
                content="Please register and wait to be verified to join the queue", ephemeral=True,
                delete_after=5)

    # Button to leave the inhouse queue
    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.queued_players:
            while self.status:
                await asyncio.sleep(1)
            if len(self.queued_players) == 10:
                await interaction.response.send_message(content="You cannot leave a full queue!", ephemeral=True,
                                                        delete_after=5)
            else:
                self.status = True
                if interaction.user.id in self.afk_dict:
                    del self.afk_dict[interaction.user.id]
                self.queued_players.remove(interaction.user)
                await self.update_message(self.queued_players, 'Leave', interaction.user)
                self.status = False
                await interaction.response.defer()
            if interaction.user.id in self.afk_dict:
                del self.afk_dict[interaction.user.id]
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content="You aren't in the queue", ephemeral=True,
                                                    delete_after=5)

    # Button to kick players from the inhouse queue
    @discord.ui.button(label="Clear Queue", emoji="🥾",
                       style=discord.ButtonStyle.blurple)
    async def clear_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        a_view = SelectUserView()
        await interaction.response.send_message(view=a_view, ephemeral=True)
        # if self.admin_role not in interaction.user.roles:
        #     interaction.response.send_message(content="Queue can only be cleared by a server admin", ephemeral=True)
        #     return
        # if len(self.queued_players) >= 10:
        #     del self.queued_players[:10]
        # else:
        #     self.queued_players.clear()
        # await self.update_message("clear", interaction.user)
        # interaction.response.send_message(content="Queue has been cleared", ephemeral=True)
