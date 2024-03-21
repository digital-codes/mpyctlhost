"""update mpyctl device in database"""
import sqlite3
from sqlite3 import Error
import os
import sys

from devDb import DatabaseManager

# Database file
#_db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_name = 'devices.db'
_cfg_file = ".cfg.json"

if len(sys.argv) > 1 :
    # assume param is path to database
    _database = os.sep.join(sys.argv[1].split("/") + [_db_name])
else:
    _database = os.sep.join([".",_db_name])

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


