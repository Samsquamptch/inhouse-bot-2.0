import yaml

def get_steam_credentials():
    with open('../../credentials/credentials_steam.yml') as f:
        data = yaml.safe_load(f)
        return (data['USERNAME'], data['PASSWORD'])
