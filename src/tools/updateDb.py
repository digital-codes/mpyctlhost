"""update mpyctl device in database"""
import sqlite3
from sqlite3 import Error
import os
import sys

import getopt
from typeConfig import TypeConfig

from devDb import DatabaseManager

# local copy file
_cfg_file = ".cfg.json"

# Database file
#db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_name = 'devices.db'

cmdOpts = "hd:p:"
_type = None
_database = os.sep.join([".",_db_name])
_port = "u0"

def usage() :
    print("Usage: updateDb.py [-d database] [-p port]")

def getOptions():
    global _database, _port
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
        elif o == "-p":
            _port = a
        else:
            assert False, "unhandled option"

getOptions() 


# Create a database connection
dbm = DatabaseManager(_database)

# read base config
cmd = f"mpremote {_port} sleep .5 run mpyGetConfig.py > {_cfg_file}"
if os.system(cmd) != 0:
    print("Read failed")
    sys.exit()

updated = dbm.update_config(_cfg_file)
print("Updated: ",updated)
    

# Close connection
dbm.close()


