import sqlite3


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(f'../../data/inhouse.db')
        self.cur = self.conn.cursor()

    def view_steam_credentials(self):
        exit_loop = False
        while not exit_loop:
            print("Saved steam login credentials\n")
            login_list = list(self.cur.execute("""SELECT Title, ServerId, Username, Password FROM SteamLogin""").fetchall())
            if not login_list:
                print("[NONE]")
            else:
                for credentials in login_list:
                    if not credentials[1]:
                        server_id = "NULL"
                    else:
                        server_id = str(credentials[1])
                    print(credentials[0] + " | " + server_id + " | " + credentials[2] + " | " + credentials[3])
            option = input("\n1. Add new login\n2. Edit login\n3. Delete login\n4. Return\n")
            match option:
                case "1":
                    self.add_steam_credentials()
                case "2":
                    self.edit_steam_credentials()
                case "3":
                    self.delete_steam_credentials()
                case "4":
                    return
                case _:
                    print("Please input a number corresponding to an option")

    def add_steam_credentials(self):
        title = input("Please set a title (for ease of reference, such as the associated server name):\n")
        server = input("Please paste the Server ID (refer to the setup guide for more details):\n")
        username = input("Please input the username of the steam account:\n")
        password = input("Please input the password of the steam account:\n")
        self.cur.execute("""INSERT INTO SteamLogin (ServerId, Title, Username, Password) Values (?, ?, ?, ?)""",
                         [server, title, username, password])
        self.conn.commit()

    def edit_steam_credentials(self):
        identifier = input("Please input the title or paste the Server ID of the credentials you wish to change:\n")
        username = input("Please input the username of the steam account:\n")
        password = input("Please input the password of the steam account:\n")
        self.cur.execute("""UPDATE SteamLogin SET Username = ?, Password = ? WHERE serverId = ? OR Title = ?""",
                         [username, password, identifier, identifier])
        self.conn.commit()
        print("Credentials updated")

    def delete_steam_credentials(self):
        identifier = input("Please input the title or paste the Server ID of the credentials you wish to delete:\n")
        credentials = list(self.cur.execute("""SELECT Title, ServerId, Username, Password FROM SteamLogin
                                            WHERE Title = ? OR ServerId = ?""", [identifier, identifier]).fetchall())
        if not credentials:
            print("no credentials match this record")
            return
        else:
            if not credentials[1]:
                server_id = "NULL"
            else:
                server_id = str(credentials[1])
            print("Details you wish to delete are:\n" + credentials[0] + " | " + server_id + " | " + credentials[2] + " | " + credentials[3])
        confirm = input("Are you sure you wish to delete this record (enter 'yes' to confirm)\n")
        if confirm == "yes":
            self.cur.execute("""DELETE FROM SteamLogin WHERE Title = ? OR ServerId = ?""", [identifier, identifier])
            self.conn.commit()
            print("Record deleted")
        else:
            return

    def import_databse(self):
        # TODO: add a way to import old databases
        print("This feature has not been implemented yet")
        return

    def add_bot_token(self):
        self.cur.execute("""INSERT INTO DiscordConnection (Id) VALUES (1)""")
        self.update_bot_token()
        self.conn.commit()

    def update_bot_token(self):
        token = input("Please paste your Discord Bot Token here (leave empty to skip this step):\n")
        if not token:
            return
        self.cur.execute("""UPDATE DiscordConnection SET Token = ? WHERE Id = 1""", [token])
        self.conn.commit()

    def create_tables(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS DiscordConnection(Id UNIQUE NOT NULL, Token CHAR)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS User(Id INT PRIMARY KEY, Discord BIGINT UNIQUE, Steam BIGINT UNIQUE,
            MMR INT, Verified BOOL, Pos1 INT, Pos2 INT,Pos3 INT, Pos4 INT, Pos5 INT, LastUpdated DATETIME)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Server(Id INTEGER PRIMARY KEY, Server BIGINT, AdminChannel BIGINT,
            QueueChannel BIGINT GlobalChannel BIGINT ChatChannel BIGINT ChampionRole BIGINT)""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS UserStats(UserId INT, ServerId INT, Wins INT, Losses INT,
            FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS ServerSettings(ServerId INT UNIQUE, AfkTimer INT, SkillFloor INT,
            SkillCeiling INT, QueueName CHAR, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS GlobalQueue(ServerId INT UNIQUE, PublicListing BOOL, InviteLink CHAR,
            FOREIGN KEY(ServerId) REFERENCES Server(Id))""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Banned(UserId INT NOT NULL, ServerId INT NOT NULL,
            FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id), PRIMARY KEY(UserId, ServerId))""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Admin(UserId INT NOT NULL, ServerId INT NOT NULL,
            FOREIGN KEY(UserId) REFERENCES User(Id), FOREIGN KEY(ServerId) REFERENCES Server(Id), PRIMARY KEY(UserId, ServerId))""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS SteamLogin(ServerId INT UNIQUE, Title CHAR, Username CHAR,
        Password CHAR, FOREIGN KEY(ServerId) REFERENCES Server(Id))""")

    def main(self):
        database_exists = self.cur.execute("""SELECT name FROM sqlite_master; """).fetchall()
        if not database_exists:
            print("Database contains no tables, creating now")
            self.create_tables()
        bot_credentials = self.cur.execute("""SELECT Token FROM DiscordConnection; """).fetchall()
        if not bot_credentials:
            print("No bot token found, please add new token")
            self.add_bot_token()
        exit_loop = False
        while not exit_loop:
            print("Welcome to the Database Manager. Please input the number that matches the option you want.")
            option = input("""1. Update Discord Bot Token\n2. View Steam Credentials\n3. Import Database\n4. Exit\n""")
            match option:
                case "1":
                    self.update_bot_token()
                case "2":
                    self.view_steam_credentials()
                case "3":
                    self.import_databse()
                case "4":
                    exit_loop = True
                case _:
                    print("Please input a number corresponding to an option")
        print("Exiting program. Thank you for using database manager!")
        return


foo = DatabaseManager()
foo.main()
