from dotenv import get_key

def get_discord_token():
    return get_key("../../credentials/.env", "TOKEN")

def load_initialisation_instructions():
    with open("../../data/setup.txt", "r") as setup:
        return setup.read().split("\n\n")

def load_setup_image():
    return "../../icons/slug_setup.png"

def load_admin_image():
    return "../../icons/slug_admin.png"

def load_queue_image():
    return "../../icons/slug_queue.png"
