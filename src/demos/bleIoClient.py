
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
    rem = len(data) % block_size
    padding_required = block_size - rem
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
        print("Checking:",d["config"]["ble"])
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

async def discoverDevices():
    return await BleakScanner.discover(timeout = 5.0)

bleDevs = asyncio.run(discoverDevices())
print("BLE devs:",bleDevs)
for i,b in enumerate(bleDevs):
    if b.name != None:
        name = b.name
    elif b.details != None:
        name = b.details
    else:
        name = "Unknown"
    if "MpyCtl" in name:
        print(i,name)

idx = int(input("Enter index of device: "))
name = bleDevs[idx].name

async def findDevs(name):
    print(f"Scanning for {name}")
    dev = await BleakScanner.find_device_by_name(name)
    #device = await BleakScanner.find_device_by_filter(devFilter)
    return dev.address

dev = asyncio.run(findDevs(name))
print("device:",dev)
key = find_key(name)
print("key:",key)


#sys.exit()

check_services = True

async def main(address):
    await BleakClient(address).disconnect()
    time.sleep(.3)
    async with BleakClient(address) as client:
        if client.is_connected:
            #await client.pair()
            # get read from devicelist
            #
            if check_services:
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
                # we have the key already from device selection
                msg = encrypt(pairVal,key)
                await client.write_gatt_char(DEVICE_PAIR,msg)
                time.sleep(.1)
            except:
                print("config and pair failed")
                raise BaseException("Pair failed")


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

