import discord
import data_management


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
