"""create and maintain mpyctl device database"""
import sqlite3
from sqlite3 import Error
import os
import json
import sys
from devDb import DatabaseManager

# defs
# Device name
_devName = "MpyCtl"

# Database file
#db_dir = "/home/kugel/daten/work/database/mpyctl"
_db_dir = "."
_db_name = 'devices.db'


def main():
    # Create a database connection
    if len(sys.argv) > 1 :
        # assume param is databasefile
        _database = sys.argv[1]
    else:
        _database = os.sep.join(_db_dir.split("/") + [_db_name])
    dbm = DatabaseManager(_database)

    latest = dbm.get_latest_id()
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

