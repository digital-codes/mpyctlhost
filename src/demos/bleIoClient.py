
import asyncio
from bleak import BleakClient
from bleak import BleakScanner
from bleak import BLEDevice
import struct
import time
import random
import json
import sys
from Crypto.Cipher import AES

address = "94:b9:7e:92:b6:d2" # matrix 1
address = "AC:0B:FB:6F:40:B2" # stamp normal
address = "60:55:F9:57:B1:C2" # stamp c3u
address = "64:E8:33:00:7C:16" # xiao c3
address = "DC:54:75:CE:A3:F6" # stamp s3
address = "D8:A0:1D:5C:89:66" # lite
address = "DC:54:75:C8:96:06" # S3

# need to run ble1 at least once bofore using this ...

# pairing stuff
# load devices
devList = []
try:
    with open("devices.json") as f:
        devList = json.load(f)
except:
    print("Device list error")
    #sys.exit()

print(f"Devices: {devList}")

def pkcs7_padding(data, block_size=16):
    padding_required = block_size - (len(data) % block_size)
    padding = bytes([padding_required] * padding_required)
    return data + padding

_mtu = 20
_msgBytes = 4
_ivBase = bytearray([0]*(16 - _msgBytes)) # first 3/4 iv
_cryptMode = AES.MODE_CBC  # CBC

# find key for device
def find_key(dev):
    key = None
    for d in devList:
        print(d["config"]["ble"])
        if d["name"] == dev:
            key = bytes.fromhex(d["config"]["ble"]["key"])
            break
    return key

def encrypt(msg,key):
    payload = None
    try:
        ivPart = bytearray([random.randint(0, 255) for i in range(4)])  # Note the range is 0-255 for valid byte values
        # Combine and convert to bytes
        iv = bytes(_ivBase + ivPart)
        # Initialize AES cipher
        fwd = AES.new(key, _cryptMode, iv)
        pmsg = bytes(pkcs7_padding(msg))
        digest = fwd.encrypt(pmsg)
        payload = digest + ivPart
        return payload
    except:
        print("Crypt error")
        raise BaseException("Invalid Config")        



################

def callback(sender, data):
    print(f"{sender}: {data}")

def decode_temperature(data):
    # <h: unsigned short, little endian
    return struct.unpack("<h", data)[0]/100

def encode_ctl(data):
    # b: unsigned char
    return struct.pack("b", data)

DEVICE_CONFIG_RD = "19e2282a-0777-4519-9d08-9bc983c3a7d0"
DEVICE_PAIR = "bda7b898-782a-4a50-8d10-79d897ea82c2"

#await asyncio.BleakClient(address).disconnect()

async def findDevs(name):
    print(f"Scanning for {name}")
    dev = await BleakScanner.find_device_by_name(name)
    #device = await BleakScanner.find_device_by_filter(devFilter)
    return dev.address

name = devList[0]["name"]

dev = asyncio.run(findDevs(name))
print("device:",dev)
key = find_key(name)
print("key:",key)


#sys.exit()

async def main(address):
    await BleakClient(address).disconnect()
    time.sleep(1)
    async with BleakClient(address) as client:
        if client.is_connected:
            #await client.pair()
            # get read from devicelist
            #
            services = client.services
            print("Services:",services)
            for s in services:
                print("\n",s)
                chars = s.characteristics
                print("characters:",chars)
                for c in chars:
                    print(c)

            env = services.get_service("0000181a-0000-1000-8000-00805f9b34fb")
            print("\n\nhr:",env)
            chars = env.characteristics
            print("characters:",chars)
            for c in chars:
                print("\nchar:",c)

            ctl = services.get_service("00001815-0000-1000-8000-00805f9b34fb")
            print("\n\nctl:",ctl)
            chars = ctl.characteristics
            print("characters:",chars)
            for c in chars:
                print("\nchar:",c)

            info = services.get_service("0000180a-0000-1000-8000-00805f9b34fb")
            print("\n\ninfo:",info)
            chars = info.characteristics
            print("characters:",chars)
            for c in chars:
                print("\nchar:",c)

            mfc = info.get_characteristic("00002a29-0000-1000-8000-00805f9b34fb")
            print("mfg char:",mfc,"\n-  ",mfc.description)
            mfcVal = await client.read_gatt_char("00002a29-0000-1000-8000-00805f9b34fb")
            print("mfg val:",mfcVal)
            mdlVal = await client.read_gatt_char("00002a24-0000-1000-8000-00805f9b34fb")
            print("mdl val:",mdlVal)

            # config and pairing
            try:
                cfgVal = await client.read_gatt_char(DEVICE_CONFIG_RD)
                print("cfg val:",cfgVal)
                pairVal = await client.read_gatt_char(DEVICE_PAIR)
                print("pair val:",pairVal)
                # encrypt
                key = find_key(name)
                if key == None:
                    raise BaseException("No Key")
                msg = encrypt(pairVal,key)
                await client.write_gatt_char(DEVICE_PAIR,msg)
                time.sleep(.1)
            except:
                print("config and pair failed")


            tmp = env.get_characteristic("00002a6e-0000-1000-8000-00805f9b34fb")
            print("rate char:",tmp,"\n-  ",tmp.description)
            out = ctl.get_characteristic("00002a56-0000-1000-8000-00805f9b34fb")
            print("rate char:",out,"\n-  ",out.description)
            
            try:
                data = False
                for i in range(10):
                    bat = await client.read_gatt_char("00002a6e-0000-1000-8000-00805f9b34fb")
                    print("BAT", decode_temperature(bat))
                    time.sleep(1)
                    try:
                        data = True if data == False else False
                        print("CTL:",data)
                        await client.write_gatt_char("00002a56-0000-1000-8000-00805f9b34fb",encode_ctl(data))
                    except:
                        print("Write failed")
                    

            except:
                print("failed")
            
        else:
            print("not connected")


            

asyncio.run(main(dev))

