""" mpyctl type configuration """

import sys
import os
import json


class TypeConfig:
    """
    Class representing the configuration for a specific type of device.
    """

    def __init__(self, cfg=".cfg.json"):
        """
        Initializes a new instance of the TypeConfig class.

        Args:
            cfg (Union[str, object], optional): The path to the configuration file as a string or the configuration object itself. Defaults to ".cfg.json".
        """
        if isinstance(cfg, str):
            if not os.path.isfile(cfg):
                print(f"Config file {cfg} not found")
                raise BaseException("Missing config file")
            self.cfg_file = cfg
            try:
                with open(self.cfg_file) as f:
                    self.config = json.load(f)
            except:
                self.cfg_file = None
                self.config = None
                raise BaseException("Invlaid config file")
        else:
            self.cfg_file = None
            self.config = cfg

    def getCfg(self):
        """
        Retrieves the configuration.

        Returns:
            dict: The configuration as a dictionary.
        """
        return self.config

    def setTypeConfigs(self, type):
        """
        Sets the type-specific configurations for the device.

        Args:
            type (str): The type of the device.

        Returns:
            dict: The updated configuration.
        """
        if type.lower() not in [x.lower() for x in TypeConfig.knownTypes]:
            raise BaseException("Unknown type")
        tIdx = [x.lower() for x in TypeConfig.knownTypes].index(type.lower())
        type = TypeConfig.knownTypes[tIdx]
        if self.config is None:
            self.getCfg()
        self.config["type"] = type
        for key, value in TypeConfig.ioSettings[type].items():
            if self.config["io"].get(key) is None and value is not None:
                self.config["io"][key] = value
        return self.config

    def getTypes(self):
        """
        Retrieves the known types of devices.

        Returns:
            list: The known types of devices.
        """
        return TypeConfig.knownTypes
    
    # type and settings constants
    knownTypes = [
        "AtomMx", "AtomLite", "AtomS3", "AtomS3U",
        "StampPico", "StampS3", "StampC3", "StampC3U",
        "Gray"
    ]
    ioSettings = {
        # lcd is type, like "s3atom"
        "AtomMx": {
                "led": 27,
                "btn": 39,
                "i2c": {
                    "scl": 25,
                    "sda": 21
                },
                "grove": [
                    32,
                    26
                ],
            "lcd": None,
            "pin": None,
            "imu": "mpu6886"
        },
        "AtomLite": {
                "led": 27,
                "btn": 39,
                "i2c": {
                    "scl": 25,
                    "sda": 21
                },
                "grove": [
                    32,
                    26
                ],
            "lcd": None,
            "pin": None,
            "imu":None
        },
        "AtomS3": {
            "grove": [
                1,
                2
            ],
            "i2c": {
                "sda": 38,
                "scl": 39
            },
            "btn": 41,
            "lcd": "s3atom",
            "led": None,
            "pin": None,
            "imu":"mpu6886"
        },
        "AtomS3U": {
            "led": 35,
            "btn": 41,
            "grove": [
                2,
                1
            ],
            "lcd": None,
            "i2c": None,
            "pin": [14,17,42,40],
            "imu":None
        },
        "StampPico": {
            "led": 27,
            "btn": 39,
            "lcd": None,
            "i2c": None,
            "grove": [32,33],
            "pin": None,
            "imu":None
        },
        "StampS3": {
            "led": 21,
            "btn": 0,
            "lcd": None,
            "i2c": None,
            "grove": None,
            "pin": None,
            "imu":None
        },
        "StampC3": {
            "led": 2,
            "btn": 3,
            "lcd": None,
            "i2c": None,
            "grove": None,
            "pin": None,
            "imu":None
        },
        "StampC3U": {
            "led": 2,
            "btn": 9,
            "lcd": None,
            "i2c": None,
            "grove": None,
            "pin": None,
            "imu":None
        },
        "Gray": {
            "led": None,
            "btn": None,
            "lcd": None,
            "i2c": None,
            "grove": None,
            "pin": None,
            "imu":None
        },
    }
    

if __name__ == "__main__":
    import getopt
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "ht:", [])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        print("usage: typeConfig.py -t <type>")
        sys.exit(-1)

    for o, a in opts:
        if o == "-h":
            print("usage: typeConfig.py -t <type>")
            sys.exit()
        elif o == "-t":
            type_config = TypeConfig()
            print(type_config.getCfg())
            type_config.setTypeConfigs(a)
            print(type_config.config)
            sys.exit()
        else:
            assert False, "unhandled option"
            
    print("Missing type")
    sys.exit(-1)