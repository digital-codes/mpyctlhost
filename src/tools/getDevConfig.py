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
_cfg_file = ".cfg.json"

cmdOpts = "hd:i:"
_type = None
_database = _database = os.sep.join([".",_db_name])
_id = None

def usage() :
    print("Usage: getDevConfig.py [-d database] <-i id> ")

def getOptions():
    global _database, _id
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
        elif o == "-i":
            _id = a
        else:
            assert False, "unhandled option"

getOptions() 

if _id is None:
    usage()
    sys.exit()


def main():
    global _database, _id
    dbm = DatabaseManager(_database)

    item = dbm.get_by_id(_id)
    if item:
        item = dict(item[0])
        config = json.loads(item["config"])
        print(json.dumps(config))
        with open(_cfg_file, "w") as cfg:
            json.dump(config,cfg)
    else:    
        print(f"Item with id {_id} not found")
    # Close connection
    dbm.close()

if __name__ == "__main__":
    main()

