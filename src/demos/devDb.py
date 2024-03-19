"""create and maintain mpyctl device database"""
import sqlite3
from sqlite3 import Error
import os
import json
import sys

# defs
# Device name
_devName = "MpyCtl"

# Database file
#_db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_dir = "."
_db_name = 'devices.db'
_database = os.sep.join(_db_dir.split("/") + [_db_name])
print("DB:",_database)

#cmd = "mpremote run /home/kugel/temp/m5/mpyctl/src/demos/devConfig.py > .cfg.json"

class DatabaseManager:
    def __init__(self, db_file):
        """
        Initialize the DatabaseManager class.

        Args:
            db_file (str): The path to the SQLite database file.
        """
        self.conn = self.create_connection(db_file)

    def create_connection(self, db_file):
        """
        Create a database connection to a SQLite database.

        Args:
            db_file (str): The path to the SQLite database file.

        Returns:
            conn (sqlite3.Connection): The database connection object.
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except Error as e:
            print(e)
        return conn

    def create_tables(self):
        """
        Create the 'devices' table if it doesn't exist.
        """
        try:
            c = self.conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS devices
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            address TEXT NOT NULL,
                            config TEXT NOT NULL)''')
        except Error as e:
            print(e)

    def insert_config(self, config_file):
        """
        Insert a new row into the 'devices' table from a config file

        Args:
            config_file (str): Name of the config file

        Returns:
            row_id (int): The ID of the inserted row.
        """
        try:
            with open(config_file) as f:
                config = json.load(f)
            address = config["ble"]["addr"].lower()
            # 1) check if device exists
            # 2) check if device is set
            # 3) check if model is set
            items = self.get_by_address(address)
            if len(items) > 0:
                print(f"Exists:{items[0]}")
                return
            if config["device"] == -1:
                config["device"] = self.get_latest_id() + 1
            if config["model"] == "":
                config["model"] = _devName
            name = "_".join([config["model"],f"{(config['device']):04}"])
            
            sql = ''' INSERT INTO devices(config, address, name)
                        VALUES(?,?,?) '''
            cur = self.conn.cursor()
            cur.execute(sql, (json.dumps(config), address, name))
            self.conn.commit()
            return cur.lastrowid
        except Error as e:
            print(e)

    def insert_row(self, json_string, mac_address, dev_name):
        """
        Insert a new row into the 'devices' table.

        Args:
            json_string (str): The JSON string to be inserted.
            mac_address (str): The MAC address to be inserted.
            dev_name (str): The name to be inserted.

        Returns:
            row_id (int): The ID of the inserted row.
        """
        try:
            sql = ''' INSERT INTO devices(config, address, name)
                        VALUES(?,?,?) '''
            cur = self.conn.cursor()
            cur.execute(sql, (json_string, mac_address, dev_name))
            self.conn.commit()
            return cur.lastrowid
        except Error as e:
            print(e)

    def get_latest_id(self):
        """
        Get the ID of the latest row in the 'devices' table.

        Returns:
            latest_id (int): The ID of the latest row.
        """
        try:
            sql = ''' SELECT id FROM devices ORDER BY id DESC LIMIT 1'''
            cur = self.conn.cursor()
            cur.execute(sql)
            latest_id = cur.fetchone()
            return latest_id[0] if latest_id else 0
        except Error as e:
            print(e)

    def get_by_name(self, name):
        """
        Get rows from the 'devices' table by name.

        Args:
            name (str): The name to search for.

        Returns:
            rows (list): A list of rows matching the name.
        """
        try:
            sql = ''' SELECT * FROM devices WHERE name = ?'''
            cur = self.conn.cursor()
            cur.execute(sql, (name,))
            rows = cur.fetchall()
            return rows
        except Error as e:
            print(e)

    def get_by_address(self, addr):
        """
        Get rows from the 'devices' table by address.

        Args:
            addr (str): The name to search for.

        Returns:
            rows (list): A list of rows matching the name.
        """
        try:
            sql = ''' SELECT * FROM devices WHERE address = ?'''
            cur = self.conn.cursor()
            cur.execute(sql, (addr,))
            rows = cur.fetchall()
            return rows
        except Error as e:
            print(e)

    def get_by_id(self, id):
        """
        Get rows from the 'devices' table by ID.

        Args:
            id (int): The ID to search for.

        Returns:
            rows (list): A list of rows matching the ID.
        """
        try:
            sql = ''' SELECT * FROM devices WHERE id = ?'''
            cur = self.conn.cursor()
            cur.execute(sql, (id,))
            rows = cur.fetchall()
            return rows
        except Error as e:
            print(e)

    def close(self):
        """
        Close the database connection.
        """
        self.conn.close()

    @staticmethod
    def initialize(db_dir,db_file):
        """
        Create and initialize new database
        Args:
            db_dir (str): base directory of database
            db_file (str): database file name
        """
        # Create a database connection
        dbm = DatabaseManager(os.sep.join([db_dir,db_file]))
        # Create table
        dbm.create_tables()
    


def main():
    # Create a database connection
    dbm = DatabaseManager(_database)

    latest = dbm.get_latest_id()
    print("Latest: ",latest)

    if len(sys.argv) > 1 :
        # assume param is configfile
        dbm.insert_config(sys.argv[1])
    else:
        for i in range(1,latest + 1):
            item = dbm.get_by_id(i)
            print(item)

    # Close connection
    dbm.close()

if __name__ == "__main__":
    main()

