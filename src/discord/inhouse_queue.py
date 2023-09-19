import discord
from discord.ext import tasks
import data_management
import check_user
import datetime
import asyncio
from zoneinfo import ZoneInfo
from collections import defaultdict


# The modal for admins to kick users from the queue. Full usernames or global nicknames must be used for this to work
class AdminKickPlayerModal(discord.ui.Modal, title='Kick User in Queue'):
    def __init__(self):
        super().__init__()
        self.user_acc = None
        self.user_name = ""
        self.clear_users = False

    player_name = discord.ui.TextInput(label='User\'s global name or username', min_length=3)

    async def on_submit(self, interaction: discord.Interaction):
        server = interaction.guild
        self.user_name = str(self.player_name)
        if self.user_name.lower() == "all" or self.user_name == "clear":
            self.clear_users = True
            await interaction.response.defer()
        else:
            check_if_exists = check_user.user_exists(server, self.user_name)
            if not check_if_exists[0]:
                self.user_acc = None
                await interaction.response.defer()
            else:
                self.user_acc = check_if_exists[1]
                await interaction.response.defer()
        self.stop()


# The modal for users to votekick when the queue is full. Will be left for a later date
class VoteKickPlayerModal(discord.ui.Modal, title='Votekick User in Queue'):
    def __init__(self):
        super().__init__()
        self.user_acc = None
        self.user_name = ""

    player_name = discord.ui.TextInput(label='User\'s global name or username', min_length=3)

    async def on_submit(self, interaction: discord.Interaction):
        server = interaction.guild
        self.user_name = str(self.player_name)
        check_if_exists = check_user.user_exists(server, self.user_name)
        if not check_if_exists[0]:
            self.user_acc = None
            await interaction.response.defer()
        else:
            self.user_acc = check_if_exists[1]
            await interaction.response.defer()
        self.stop()


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


class WaitingRoom(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.waiting_list = []
        self.channel_id = None
        self.message = None

    async def send_embed(self, server):
        channel = discord.utils.get(server.channels, id=self.channel_id['queue_channel'])
        self.message = await channel.send(content="Users in the waiting room are below", view=self)
        await self.update_message()

    def create_embed(self, queue_list):
        if queue_list:
            embed_desc = f"{len(queue_list)} People currently in waiting list"
            embed_clr = 0x00ff00
        else:
            embed_desc = "Waiting list is currently empty"
            embed_clr = 0xFF0000
        queue_embed = discord.Embed(title="Inhouse Waiting List", description=f'{embed_desc}',
                                    color=embed_clr)
        for user in queue_list:
            user_data = data_management.view_user_data(user.id)
            queue_embed.add_field(name=user.display_name, value=f'MMR: {user_data[2]}', inline=True)
        update_time = datetime.datetime.now(ZoneInfo("Europe/Paris")).strftime("%H:%M:%S")
        queue_embed.set_footer(text=f'Waiting list updated at: {update_time}')
        return queue_embed

    async def delete_message(self):
        try:
            await self.message.delete()
        except discord.errors.NotFound:
            pass
        except AttributeError:
            pass

    async def update_message(self):
        await self.message.edit(embed=self.create_embed(self.waiting_list), view=self)


# Embed and buttons for the inhouse queue
class InhouseQueue(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.queued_players = []
        self.preload_modal = WaitingRoom()
        self.votekick_dict = defaultdict(list)
        self.afk_dict = {}
        self.roles_id = None
        self.channel_id = None
        self.config_data = None
        self.message = None
        self.server = None
        self.status = False

    @tasks.loop(minutes=5)
    async def afk_check(self):
        chat_channel = discord.utils.get(self.server.channels, id=self.channel_id['chat_channel'])
        notif_channel = discord.utils.get(self.server.channels, id=self.channel_id['notification_channel'])
        channel_messages = chat_channel.history(
            after=(datetime.datetime.now() - datetime.timedelta(minutes=self.config_data['afk_time'])))
        if self.queued_players and len(self.queued_players) < 10:
            for user in self.queued_players:
                user_messages = [message async for message in channel_messages if message.author.id == user.id]
                if self.afk_dict[user.id] > datetime.datetime.now(tz=None) - datetime.timedelta(
                        minutes=self.config_data['afk_time']):
                    print(f'{user} user is active')
                    continue
                if user_messages:
                    print(f'{user} user is active')
                    continue
                else:
                    self.afk_dict[user.id] = datetime.datetime.now(tz=None)
                    asyncio.create_task(self.afk_ping(user, notif_channel))
                    print(f'{user} is afk')

    async def afk_ping(self, user, channel):
        afk_check_ping = AfkCheckButtons()
        afk_check_ping.check_user = user
        await afk_check_ping.send_buttons(channel)
        await afk_check_ping.wait()
        if afk_check_ping.kick_user and len(self.queued_players) < 10:
            del self.afk_dict[user.id]
            self.queued_players.remove(user)
            await self.update_message(self.queued_players, self.server, 'Kick', user)
            await channel.send(f"<@{user.id}> has been kicked from the queue for being afk")
        else:
            print(f"{user} responded")
            self.afk_dict[user.id] = datetime.datetime.now(tz=None)

    # async def test_add_user(self, interaction: discord.Interaction):
    #     server = interaction.guild
    #     test_list = ["Hamma", "PharmarMarosh", "Lekandor", "Boo... Who?", "Abfr0", "greenman", "Glimmy", "Rock Bottom",
    #                  "Teky"]
    #     for user in test_list:
    #         check_if_exists = check_user.user_exists(server, user)
    #         if user not in self.queued_players:
    #             self.queued_players.append(check_if_exists[1])
    #     print(self.queued_players)

    async def send_embed(self, channel):
        self.preload_modal.channel_id = self.channel_id
        self.afk_check.start()
        self.message = await channel.send(view=self)
        await self.update_message(self.queued_players, self.server)

    def full_queue_embed(self, queue_list, server):
        queue_ids = [user.id for user in queue_list]
        queue_roles = ["Carry", "Midlane", "Offlane", "Soft Supp", "Hard Supp"]
        queue_teams = data_management.assign_teams(queue_ids)
        queue_embed = discord.Embed(title="Inhouse queue", description=f'Queue is full, please join the lobby!',
                                    color=0x00ff00)
        icon_url = server.icon.url
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
            user_acc_radiant = discord.utils.get(server.members, id=radiant_team[x])
            user_acc_dire = discord.utils.get(server.members, id=dire_team[x])
            user_radiant = data_management.view_user_data(radiant_team[x])
            user_dire = data_management.view_user_data(dire_team[x])
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
    def create_embed(self, queue_list, server, action=None, action_user=None):
        if queue_list:
            role_champions = discord.utils.get(server.roles, id=self.roles_id['champions_role'])
            champion_check = any(check in queue_list for check in role_champions.members)
            if champion_check:
                embed_desc = f"A champion is in the queue!"
                embed_clr = 0xFFD700
            else:
                embed_desc = f"Queue is live, come join!"
                embed_clr = 0x00ff00
        else:
            embed_desc = "The queue is currently empty. You can change this!"
            embed_clr = 0xFF0000
        queue_embed = discord.Embed(title="INHOUSE QUEUE", description=f'{embed_desc}',
                                    color=embed_clr)
        queue_length = len(queue_list)
        match queue_length:
            case 0:
                queue_embed.add_field(name=f'No one is in the queue', value='', inline=False)
            case 1:
                queue_embed.add_field(name=f'1 player in queue', value='', inline=False)
            case _:
                queue_embed.add_field(name=f'{queue_length} players in queue', value='', inline=False)
        icon_url = server.icon.url
        queue_embed.set_thumbnail(url=f'{icon_url}')
        mmr_total = 0
        for user in queue_list:
            print(user)
            user_data = data_management.view_user_data(user.id)
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
            case _:
                pass
        if queue_list:
            average_mmr = int(mmr_total / len(queue_list))
            queue_embed.set_footer(text=f'Queue updated at: {update_time} | Average MMR: {average_mmr}')
        else:
            queue_embed.set_footer(text=f'Queue updated at: {update_time}')
        return queue_embed

    async def update_message(self, queue_list, server, action=None, update_user=None):
        if len(queue_list) >= 10:
            await self.message.edit(embed=self.full_queue_embed(queue_list, server), view=self)
            await self.preload_modal.send_embed(server)
            channel = discord.utils.get(server.channels, id=self.channel_id['queue_channel'])
            await channel.send(f'Queue has popped, can the following users please head to the lobby: \n'
                               f'<@{queue_list[0].id}> <@{queue_list[1].id}> <@{queue_list[2].id}>'
                               f'<@{queue_list[3].id}> <@{queue_list[4].id}> <@{queue_list[5].id}>'
                               f'<@{queue_list[6].id}> <@{queue_list[7].id}> <@{queue_list[8].id}>'
                               f'<@{queue_list[9].id}>', delete_after=600)
        else:
            await self.message.edit(embed=self.create_embed(queue_list, server, action, update_user), view=self)

    async def waiting_room_transfer(self, server):
        if not self.queued_players and self.preload_modal.waiting_list:
            for user in self.preload_modal.waiting_list:
                self.afk_dict[user.id] = datetime.datetime.now(tz=None)
                self.queued_players.append(user)
                if len(self.queued_players) == 10:
                    break
            self.preload_modal.waiting_list = [i for i in self.preload_modal.waiting_list if
                                               i not in self.queued_players]
            await self.preload_modal.delete_message()
            await self.update_message(self.queued_players, server)
        elif self.preload_modal.waiting_list:
            for user in self.preload_modal.waiting_list:
                self.queued_players.append(user)
                await self.preload_modal.update_message()
                if len(self.queued_players) == 10:
                    break
            self.preload_modal.waiting_list = [i for i in self.preload_modal.waiting_list if
                                               i not in self.queued_players]
            await self.preload_modal.delete_message()
            await self.update_message(self.queued_players, server)
        else:
            await self.preload_modal.delete_message()

    async def vote_kick(self, server, votekick_modal, interaction):
        channel = discord.utils.get(server.channels, id=self.channel_id['queue_channel'])
        if votekick_modal.user_acc.id not in self.votekick_dict:
            self.votekick_dict[votekick_modal.user_acc.id].append(interaction.user.id)
        elif votekick_modal.user_acc.id in self.votekick_dict and interaction.user.id not in self.votekick_dict[votekick_modal.user_acc.id]:
            self.votekick_dict[votekick_modal.user_acc.id].append(interaction.user.id)
        else:
            await interaction.followup.send(
                content=f'You\'ve already voted to kick this user before!', ephemeral=True)
            return
        kick_votes = len(self.votekick_dict[votekick_modal.user_acc.id])
        if kick_votes == 3:
            if votekick_modal.user_acc.id in self.afk_dict:
                del self.afk_dict[votekick_modal.user_acc.id]
            self.queued_players.remove(votekick_modal.user_acc)
            del self.votekick_dict[votekick_modal.user_acc.id]
            await self.update_message(self.queued_players, server, 'Kick', votekick_modal.user_acc)
            await self.waiting_room_transfer(server)
            await channel.send(content=f'{votekick_modal.user_name} has been kicked from the queue', delete_after=60)
        elif kick_votes < 3:
            num = 3 - kick_votes
            await channel.send(
                content=f'{interaction.user.display_name} wants to kick {votekick_modal.user_name} from the queue! Votes required to kick: {num}',
                delete_after=60)

    # Button to join the inhouse queue
    @discord.ui.button(label="Join Queue", emoji="✅",
                       style=discord.ButtonStyle.green)
    async def join_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role_verify = discord.utils.get(server.roles, id=self.roles_id['verified_role'])
        role_banned = discord.utils.get(server.roles, id=self.roles_id['banned_role'])
        if role_banned in interaction.user.roles:
            await interaction.response.send_message(content="You are currently banned from joining the queue",
                                                    ephemeral=True, delete_after=5)
        elif role_verify in interaction.user.roles:
            self.afk_dict[interaction.user.id] = datetime.datetime.now(tz=None)
            while self.status:
                await asyncio.sleep(1)
            if interaction.user in self.queued_players:
                await interaction.response.send_message(content="You are already queued", ephemeral=True,
                                                        delete_after=5)
            elif len(self.queued_players) < 10:
                self.status = True
                self.queued_players.append(interaction.user)
                await self.update_message(self.queued_players, server, 'Join', interaction.user)
                self.status = False
                await interaction.response.defer()
            elif interaction.user in self.preload_modal.waiting_list:
                await interaction.response.send_message(content="You are already in the waiting list", ephemeral=True,
                                                        delete_after=5)
            else:

                self.preload_modal.waiting_list.append(interaction.user)
                await self.preload_modal.update_message()
                await interaction.response.defer()
        else:
            await interaction.response.send_message(
                content="Please register and wait to be verified to join the queue", ephemeral=True,
                delete_after=5)

    # Button to leave the inhouse queue
    @discord.ui.button(label="Leave Queue", emoji="❌",
                       style=discord.ButtonStyle.red)
    async def leave_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
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
                await self.update_message(self.queued_players, server, 'Leave', interaction.user)
                self.status = False
                await interaction.response.defer()
        elif interaction.user in self.preload_modal.waiting_list:
            if interaction.user.id in self.afk_dict:
                del self.afk_dict[interaction.user.id]
            self.preload_modal.waiting_list.remove(interaction.user)
            await self.preload_modal.update_message()
            await interaction.response.defer()
        else:
            await interaction.response.send_message(content="You aren't in the queue", ephemeral=True,
                                                    delete_after=5)

    # Button to kick players from the inhouse queue
    @discord.ui.button(label="Kick User", emoji="🥾",
                       style=discord.ButtonStyle.blurple)
    async def kick_from_queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = interaction.user.guild
        role_admin = discord.utils.get(server.roles, id=self.roles_id['admin_role'])
        if role_admin in interaction.user.roles:
            admin_modal = AdminKickPlayerModal()
            await interaction.response.send_modal(admin_modal)
            await admin_modal.wait()
            if admin_modal.clear_users:
                self.afk_dict.clear()
                self.votekick_dict.clear()
                self.queued_players.clear()
                await self.update_message(self.queued_players, server, 'Clear', interaction.user)
                await self.waiting_room_transfer(server)
                await interaction.followup.send(content=f'queue has been cleared', ephemeral=True)
            elif not admin_modal.user_acc or admin_modal.user_acc not in self.queued_players:
                await interaction.followup.send(content=f'{admin_modal.user_name} isn\'t in the queue', ephemeral=True)
            else:
                if admin_modal.user_acc.id in self.afk_dict:
                    del self.afk_dict[admin_modal.user_acc.id]
                self.queued_players.remove(admin_modal.user_acc)
                await self.update_message(self.queued_players, server, 'Kick', admin_modal.user_acc)
                await self.waiting_room_transfer(server)
                await interaction.followup.send(content=f'{admin_modal.user_name} has been kicked from the queue',
                                                ephemeral=True)
        elif len(self.queued_players) == 10 and interaction.user in self.queued_players:
            votekick_modal = VoteKickPlayerModal()
            await interaction.response.send_modal(votekick_modal)
            await votekick_modal.wait()
            if not votekick_modal.user_acc or votekick_modal.user_acc not in self.queued_players:
                await interaction.followup.send(content=f'{votekick_modal.user_name} isn\'t in the queue',
                                                ephemeral=True)
            else:
                await self.vote_kick(server, votekick_modal, interaction)

        elif len(self.queued_players) < 10 and interaction.user in self.queued_players:
            await interaction.response.send_message(content="Votekick can only be held once queue is full",
                                                    ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message(content="You can't initiate a votekick if you're not in the queue!",
                                                    ephemeral=True, delete_after=5)

    # @discord.ui.button(label="Add User (test)", emoji="🖥️",
    #                    style=discord.ButtonStyle.blurple)
    # async def add_user_test(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     server = interaction.user.guild
    #     role_admin = discord.utils.get(server.roles, id=self.roles_id['admin_role'])
    #     if role_admin in interaction.user.roles:
    #         await self.test_add_user(interaction)
    #         await self.update_message(self.queued_players, server)
    #         await interaction.response.defer()
