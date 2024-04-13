import os
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    """
    Initializes Database driver, makes connection to a file called users.db and loads it
    """
    def __init__(self):
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.create_users_table()

    """
    Creates the table of users, with columns for id, name and username (which are non-optional, hence NOT NULL), and optional balance (default value of 0)
    """
    def create_users_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT NOT NULL,
                    balance INTEGER
                );
            """)
        except Exception as e:
            print("Error creating users table", e)

    """
    Reset tables, to ensure graders receive same empty database for postman.
    """
    def reset_tables(self):
        self.conn.execute("DROP TABLE IF EXISTS users;")
        self.create_users_table() #Removes existing table, and resets ID numbering by making new table
        self.conn.commit()  

    """
    Returns id, name, and username (but not balance) for each user in users database
    """
    def query_all_users(self):
        cursor = self.conn.execute("SELECT id, name, username FROM users;")
        user_list = []

        for row in cursor: 
            user_list.append({"id": row[0], "name": row[1], "username": row[2]})

        return user_list
    
    """
    Inserts user with name, username, balance parameters. Default value of balance is 0 if unspecified.
    Note name and username input validation (i.e., failure response if not present) will be handled in create_user method in app.py
    """
    def insert_user_table(self, name, username, balance=0):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (name, username, balance) VALUES (?, ?, ?);", 
            (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid

    """
    Returns the ID, name, username, and balance of a specified (by ID) user from users table
    """
    def query_user_by_id(self, id):
        cursor = self.conn.execute("SELECT * FROM users WHERE ID = ?", (id,))

        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None
    """
    Removes user with specified id from users table
    """
    def remove_user(self, id):
        self.conn.execute("""
        DELETE FROM users
        WHERE id = ?;        
        """, (id,))
        self.conn.commit()

    """
    Adds the amount specified to user with specified id in users table (note: call -amount in app.py to remove money, 
    and validation of amount handled there as well).
    """
    def update_user(self, id, amount):
        self.conn.execute("""
            UPDATE users 
            SET balance = balance + ?
            WHERE id = ?;
        """, (amount,id))
        self.conn.commit()

    """
    Helper method to send_money in app.py, gets the balance of sender's account
    """
    def query_user_balance(self, id): 
        cursor = self.conn.execute("SELECT balance FROM users WHERE ID = ?", (id,))

        for row in cursor:
            return row[0] #returns balance of the sole user with that id.
        return None

# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
