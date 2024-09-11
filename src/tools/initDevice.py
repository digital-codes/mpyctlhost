"""create and maintain mpyctl device database"""
import sqlite3
from sqlite3 import Error
import os
import json
import sys
import getopt

from devDb import DatabaseManager

from typeConfig import TypeConfig

# defs

# Database file
#_db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_name = 'devices.db'
_cfg_file = ".cfg.json"

cmdOpts = "hd:p:t:"
_type = None
_database = _database = os.sep.join([".",_db_name])
_port = "u0"

def usage() :
    print("Usage: initDevice.py [-d database] [-p port] <-t type>")

def getOptions():
    global _database, _port, _type
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
        elif o == "-t":
            _type = a
        else:
            assert False, "unhandled option"

getOptions() 

print(
    "Database: ",_database,
    "Port: ",_port,
    "Type: ",_type
    )

if _type is None:
    usage()
    sys.exit()

# read base config
cmd = f"mpremote {_port} sleep .5 run mpyGetConfig.py > {_cfg_file}"
if os.system(cmd) != 0:
    print("Read failed")
    sys.exit()
    
try:
    tc = TypeConfig(_cfg_file) # default config
    cfg = tc.setTypeConfigs(_type)
    json.dump(cfg, open(_cfg_file, "w"))
except:
    print("Failed to udate config file")
    sys.exit()    

# Create a database connection
dbm = DatabaseManager(_database)

# check if the device exists already
addr = cfg["ble"]["addr"].lower().lower()
item = dbm.get_by_address(addr)
if len(item) > 0:
    print(f"Device exists already {item[0]["name"]}")
    # Close connection
    dbm.close()
    sys.exit()

latest = dbm.get_latest_id()
print("Latest: ",latest)

    
dbm.insert_config(_cfg_file)
newest = dbm.get_latest_id()
print("Newest: ",newest)

# update device with config
cmd = f"mpremote {_port} sleep .5 cp {_cfg_file} :config.json"
if os.system(cmd) != 0:
    print("Write to device failed")
    # Close connection
    dbm.close()
    sys.exit()


# Close connection
dbm.close()


