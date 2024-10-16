"""create and maintain mpyctl device database"""
import sqlite3
from sqlite3 import Error
import os
import json
import sys
from devDb import DatabaseManager
import getopt


# Database file
#db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_name = 'devices.db'

cmdOpts = "hd:"
_database = os.sep.join([".",_db_name])

def usage() :
    print("Usage: listDevices.py [-d database] ")

def getOptions():
    global _database
    try:
        opts, _ = getopt.getopt(sys.argv[1:], cmdOpts, [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o == "-h":
            usage()
            sys.exit()
        elif o == "-d":
            _database = a
        else:
            assert False, "unhandled option"


def main():
    getOptions() 
    # Create a database connection
    if not os.path.isfile(_database):
        print(f"Database file {_database} does not exist.")
        sys.exit()
    dbm = DatabaseManager(_database)
    latest = dbm.get_latest_id()
    if latest is None:
        print("No devices in database")
        sys.exit()

    items = []
    for i in range(1,latest + 1):
        item = dbm.get_by_id(i)
        if item:
            item = dict(item[0])
            item["config"] = json.loads(item["config"])
            items.append(item)

    # Close connection
    dbm.close()
    print(json.dumps(items))

if __name__ == "__main__":
    main()

