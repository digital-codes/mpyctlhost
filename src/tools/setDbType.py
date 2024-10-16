"""update mpyctl device in database"""
import sqlite3
from sqlite3 import Error
import os
import sys
import json

import getopt
from typeConfig import TypeConfig

from devDb import DatabaseManager

# local copy file
_cfg_file = ".cfg.json"

# Database file
#db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_name = 'devices.db'

cmdOpts = "hd:i:t:"
_type = None
_database = os.sep.join([".",_db_name])
_id = None
_type = None

def usage() :
    print("Usage: updateDb.py [-d database] <-i id> <-t type>")

def getOptions():
    global _database, _id, _type
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
        elif o == "-t":
            _type = a
        else:
            assert False, "unhandled option"

getOptions() 
print(
    "Database: ",_database,
    "Id: ",_id,
    "Type: ",_type
    )

if _type is None or _id is None:
    usage()
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

item = dbm.get_by_id(_id)
config = dict(item[0])
cfg = json.loads(config["config"])
try:
    tc = TypeConfig(cfg) # default config
    cfg2 = tc.setTypeConfigs(_type)
except:
    print("Failed to udate configuration")
    sys.exit()    

print("New Config obj: ",cfg2)
# sc = {'id': 1, 'name': 'MpyCtl_0001', 'address': 'dc5475c89606', 'config': '{"id": "dc5475c89604", "wlan": {"ssid": "karlsruhe.freifunk.net", "addr": "dc5475c89604", "key": ""}, "model": "MpyCtl", "io": {"grove": [2, 1], "btn": 41}, "setting": -1, "device": 1, "ble": {"key": "ee540e93c07e27db8da1648ed27214dd", "pin": 786580, "addr": "dc5475c89606"}, "os": {"release": "1.22.0", "machine": "Generic ESP32S3 module with ESP32S3"}}'}
# updated = dbm.update_by_id(_id,json.loads(sc["config"])) #config)
updated = dbm.update_by_id(_id,cfg) #config)
print("Updated: ",updated)

# Close connection
dbm.close()


