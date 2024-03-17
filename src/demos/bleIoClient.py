
import asyncio
from bleak import BleakClient
import struct
import time
import random

address = "94:b9:7e:92:b6:d2" # matrix 1
address = "AC:0B:FB:6F:40:B2" # stamp normal
address = "60:55:F9:57:B1:C2" # stamp c3u
address = "64:E8:33:00:7C:16" # xiao c3
address = "DC:54:75:CE:A3:F6" # stamp s3
address = "D8:A0:1D:5C:89:66" # lite
address = "DC:54:75:C8:96:06" # S3

# need to run ble1 at least once bofore using this ...

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


async def main(address):
    async with BleakClient(address) as client:
        if client.is_connected:
            await client.pair()
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
                await client.write_gatt_char(DEVICE_PAIR,bytearray([1,2,3,3,2,1]))
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


            

asyncio.run(main(address))

