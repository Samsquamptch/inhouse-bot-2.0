import data_interface


def view_steam_credentials():
    exit_loop = False
    while not exit_loop:
        print("Saved steam login credentials\n")
        login_list = data_interface.get_reference_list()
        if not login_list:
            print("[NONE]")
        else:
            for credentials in login_list:
                if not credentials[1]:
                    server_id = "NULL"
                else:
                    server_id = str(credentials[1])
                print(credentials[0] + " | " + server_id)
        option = input("\n1. Add new login\n2. Edit login\n3. Delete login\n4. Return\n")
        match option:
            case "1":
                add_steam_credentials()
            case "2":
                edit_steam_credentials()
            case "3":
                delete_steam_credentials()
            case "4":
                return
            case _:
                print("Please input a number corresponding to an option")


def add_steam_credentials():
    title = input("Please set a title (for ease of reference, such as the associated server name):\n")
    server = input("Please paste the Server ID (refer to the setup guide for more details):\n")
    username = input("Please input the username of the steam account:\n")
    password = input("Please input the password of the steam account:\n")
    data_interface.add_credentials(title, server, username, password)


def edit_steam_credentials():
    identifier = input("Please input the title or paste the Server ID of the credentials you wish to change:\n")
    username = input("Please input the username of the steam account:\n")
    password = input("Please input the password of the steam account:\n")
    data_interface.edit_credentials(identifier, username, password)
    print("Credentials updated")


def delete_steam_credentials():
    identifier = input("Please input the title or paste the Server ID of the credentials you wish to delete:\n")
    login_list = data_interface.get_reference_list(identifier)
    if not login_list:
        print("no credentials match this record")
        return
    else:
        for credentials in login_list:
            if not credentials[1]:
                server_id = "NULL"
            else:
                server_id = str(credentials[1])
            print(
                "Details you wish to delete are:\n" + credentials[0] + " | " + server_id)
    confirm = input("Are you sure you wish to delete this record (enter 'yes' to confirm)\n")
    if confirm == "yes":
        data_interface.delete_credentials(identifier)
        print("Record deleted")
    else:
        return


def import_database():
    # TODO: add a way to import old databases
    print("This feature has not been implemented yet")
    return


def update_bot_token():
    token = input("Please paste your Discord Bot Token here (leave empty to skip this step):\n")
    if not token:
        return
    data_interface.set_env_variable("TOKEN", token)


def main():
    if not data_interface.database_exists():
        print("Database contains no tables, creating now")
        data_interface.create_tables()
    exit_loop = False
    while not exit_loop:
        print("Welcome to the Database Manager. Please input the number that matches the option you want.")
        option = input("""1. Update Discord Bot Token\n2. View Steam Credentials\n3. Import Database\n4. Exit\n""")
        match option:
            case "1":
                update_bot_token()
            case "2":
                view_steam_credentials()
            case "3":
                import_database()
            case "4":
                exit_loop = True
            case _:
                print("Please input a number corresponding to an option")
    print("Exiting program. Thank you for using database manager!")
    return

main()
