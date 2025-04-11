import yaml
import src.data.db_access

def check_autolobby(server_id):
    pass


def get_steam_credentials():
    with open('../../credentials/credentials_steam.yml') as f:
        data = yaml.safe_load(f)
        return (data['USERNAME'], data['PASSWORD'])


def get_league_id():
    with open('../../credentials/credentials_steam.yml') as f:
        data = yaml.safe_load(f)
        return (data['LEAGUE'])
