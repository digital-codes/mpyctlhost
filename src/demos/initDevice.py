"""create and maintain mpyctl device database"""
import sqlite3
from sqlite3 import Error
import os
import json
import sys
import sys

from devDb import DatabaseManager

# defs
# Device name
_devName = "MpyCtl"

# Database file
#_db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_dir = "."
_db_name = 'devices.db'
_cfg_file = ".cfg.json"

if len(sys.argv) > 1 :
    # assume param is path to database
    _database = os.sep.join(sys.argv[1].split("/") + [_db_name])
else:
    _database = os.sep.join([".",_db_name])

# Create a database connection
dbm = DatabaseManager(_database)

latest = dbm.get_latest_id()
print("Latest: ",latest)

# read base config
cmd = f"mpremote run mpyGetConfig.py > {_cfg_file}"
if os.system(cmd) != 0:
    print("Read failed")
    # Close connection
    dbm.close()
    sys.exit()

dbm.insert_config(_cfg_file)
newest = dbm.get_latest_id()
print("Newest: ",newest)

# update device with config
cmd = f"mpremote cp {_cfg_file} :config.json"
if os.system(cmd) != 0:
    print("Write to device failed")
    # Close connection
    dbm.close()
    sys.exit()


# Close connection
dbm.close()


