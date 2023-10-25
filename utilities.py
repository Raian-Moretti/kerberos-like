from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64
import random
import string

def iv():
    return get_random_bytes(16)

def encryptAES(message, key):
    message = str(message)
    message = message.encode()
    padded_message = pad(message, AES.block_size)
    iv_val = iv()
    cipher = AES.new(key[:32], AES.MODE_CBC, iv_val)
    encoded_message = cipher.encrypt(padded_message)
    return base64.b64encode(iv_val + encoded_message).decode('utf-8')

def decryptAES(encoded_message, key):
    encoded_message = base64.b64decode(encoded_message)
    iv_val = encoded_message[:16]
    encoded_message = encoded_message[16:]
    cipher = AES.new(key[:32], AES.MODE_CBC, iv_val)
    decoded_message = cipher.decrypt(encoded_message)
    decoded_message = unpad(decoded_message, AES.block_size)
    return decoded_message.decode('utf-8')

def newUser(username):
    with open('client_userdata.txt','r',newline='\n') as f:
        for line in f:
            components = line.strip().split(':')
            if len(components) == 2 and components[0] == username:
                return False
        return True

def userLogin(username, password):
    with open('client_userdata.txt','r', newline='\n') as f:
        for line in f:
            components = line.strip().split(':')
            if len(components) == 2 and components[0] == username:
                if components[1] == password:
                    return True
        return False

def parse_message(message):
    parsed_string = message.strip("'")
    parsed_list = parsed_string.split(",")
    return parsed_list

# Cria usuário no cliente
def createUser(username, password):
    with open('client_userdata.txt', 'a+') as f:
        f.write(f'{username}:{password}\n')

# Cria usuário no servidorAS.py
def createASUser(username,password):
    with open('as_userdata.txt', 'a+') as f:
            f.write(f'{username}:{password}\n')
    return

def getPass(username):
    with open('client_userdata.txt','r', newline='\n') as f:
        for line in f:
            components = line.strip().split(':')
            if len(components) == 2 and components[0] == username:
                pwd = components[1]
                return pwd
        return -1
        
def getKey(server):
    with open(f'{server}_data.txt','r', newline='\n') as f:
        for line in f:
            components = line.strip().split(':')
            if len(components) == 1:
                key = components[0]
                return key
        return -1
    
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def rotateKey(server):
    random = generate_random_string(32)
    with open(f'{server}_data.txt', 'w') as f:
        f.write(f'{random}')