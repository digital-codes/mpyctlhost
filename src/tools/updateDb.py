"""update mpyctl device in database"""
import sqlite3
from sqlite3 import Error
import os
import sys

from devDb import DatabaseManager

# local copy file
_cfg_file = ".cfg.json"

# Database file
#db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_dir = "."
_db_name = 'devices.db'


if len(sys.argv) > 1 :
    if len(sys.argv) > 1 :
        # assume param is databasefile
        _database = sys.argv[1]
    else:
        _database = os.sep.join(_db_dir.split("/") + [_db_name])

# Create a database connection
dbm = DatabaseManager(_database)

# read base config
cmd = f"mpremote run mpyGetConfig.py > {_cfg_file}"
if os.system(cmd) != 0:
    print("Read failed")
    sys.exit()

updated = dbm.update_config(_cfg_file)
print("Updated: ",updated)
    

# Close connection
dbm.close()


