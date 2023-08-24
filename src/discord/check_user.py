import discord
import data_management

registered_list = []

def user_embed(data_list, player_data, server):
    role = discord.utils.get(server.roles, name="verified")
    if role in player_data.roles:
        verified_status = "User is verified"
        user_clr = 0x00ff00
    else:
        verified_status = "User is not verified"
        user_clr = 0xFF0000
    user_embed = discord.Embed(title=f'{player_data.global_name}', description=f'{verified_status}',
                               color=user_clr)
    user_embed.set_thumbnail(url=f'{player_data.avatar}')
    user_embed.add_field(name='Dotabuff', value=f'https://www.dotabuff.com/players/{data_list[1]}', inline=True)
    user_embed.add_field(name='MMR', value=f'{data_list[2]}', inline=True)
    user_embed.add_field(name='Role Preferences', value='', inline=False)
    user_embed.add_field(name='Carry', value=f'{data_list[3]}', inline=False)
    user_embed.add_field(name='Midlane', value=f'{data_list[4]}', inline=False)
    user_embed.add_field(name='Offlane', value=f'{data_list[5]}', inline=False)
    user_embed.add_field(name='Soft Support', value=f'{data_list[6]}', inline=False)
    user_embed.add_field(name='Hard Support', value=f'{data_list[7]}', inline=False)
    return user_embed

def user_list(list_condition, user=None):
    global registered_list
    match list_condition:
        case "Add":
            registered_list.append(user)
            print(registered_list)
        case "Remove":
            registered_list.remove(user)
            print(registered_list)
        case _:
            pass
    return registered_list

def user_exists(server, user_name):
    try:
        user_account = discord.utils.get(server.members, global_name=user_name)
        if user_account is None:
            user_account = discord.utils.get(server.members, name=user_name)
        user_in_database = data_management.check_for_value(user_account.id)
    except:
        user_in_database = False
        user_account = None
    return user_in_database, user_account
