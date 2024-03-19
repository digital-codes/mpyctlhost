from Crypto.Cipher import AES
import random
import secrets
import os
import base64

# device is
devNum = 123
idString = f"{devNum:06}"
# shared key
#key1 = b'0123456789ABCDEF'  # 16 bytes key
key1=secrets.token_bytes(16)
print(f"KEY: {key1.hex()}")

fout = f"{idString}.png"
cmd = f"qrencode -m5 -s5 \'{idString} {key1.hex()}\' -o {fout}"
print(cmd)
os.system(cmd)

with open(fout,"rb") as f:
    qr = f.read()
    qrcode = base64.b64encode(qr)
print(qrcode)    


# convert back from hex like:
# bytes.fromhex(k)



def pkcs7_padding(data, block_size=16):
    padding_required = block_size - (len(data) % block_size)
    padding = bytes([padding_required] * padding_required)
    return data + padding


# Fixed IV part
iv_fix_ = [1, 2, 3, 4, 1, 2, 3, 4]
# Generate the random part of the IV
ivPart_ = [random.randint(0, 255) for i in range(8)]  # Note the range is 0-255 for valid byte values

# Combine and convert to bytes
iv = bytes(iv_fix_ + ivPart_)
print(f"IV: {iv.hex()}")

# Assuming key1 and mode are defined elsewhere in your code. For example:
mode = AES.MODE_CBC  # Example mode

# Initialize AES cipher
fwd = AES.new(key1, mode, iv)

# msgBytes is assumed to be defined elsewhere. It indicates the size in bytes for the message.
msgBytes = 4  # Example size

# Generate random PIN
pin = random.getrandbits(8 * msgBytes) % 1000000
print(f"PIN: {pin}")

# Convert PIN to bytes and pad the message to 16 bytes for AES encryption
msg = pin.to_bytes(msgBytes, "big")
msg_padded = pkcs7_padding(msg)
print(f"MSG: {msg_padded.hex()}")

# Encrypt the message
encoded = fwd.encrypt(msg_padded)
print(f"ENC: {encoded.hex()}")
