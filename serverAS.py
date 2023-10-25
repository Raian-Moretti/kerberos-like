import string
import random
import pickle
import socket
import time
from utilities import getPass, encryptAES, decryptAES, parse_message, getKey, rotateKey


host = '127.0.0.1'
port = 48792

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host,port))
        while True:
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                connectionStatus = True
                while connectionStatus:
                    message_data = conn.recv(1024)
                    if(not message_data):
                        connectionStatus = False
                    else:
                        # Recebe mensagem do client.py
                        print("<<A primeira mensagem foi recebida do Cliente!\n")
                        first_message = pickle.loads(message_data) #M1
                        client_ticket_identifier_tgs = first_message[0] # ID_C
                        client_key = getPass(client_ticket_identifier_tgs)[:32] #K_c
                        client_key = client_key.encode()

                        decrypted_message = decryptAES(first_message[1],client_key) #Decrypted_M1
                        decrypted_message = parse_message(decrypted_message)
                        service_identifier_tgs = decrypted_message[0] #T_R
                        client_ticket_duration_tgs = decrypted_message[1] #T_R
                        first_random = decrypted_message[2] #N1

                        client_key_tgs = ''.join(random.choices(string.ascii_uppercase + string.digits, k=32)) #K_c_tgs
                        rotateKey('tgs')
                        client_ticket_key_tgs = getKey('tgs') #K_tgs
                        client_ticket_key_tgs = client_ticket_key_tgs.encode()
                        buffer_1 = f"{client_key_tgs},{first_random}"
                        buffer_2 = f"{client_ticket_identifier_tgs},{client_ticket_duration_tgs},{client_key_tgs}"
                        second_message = [encryptAES(buffer_1, client_key), encryptAES(buffer_2, client_ticket_key_tgs)] #M2
                        second_message_data = pickle.dumps(second_message)
                        time.sleep(5)
                        print(">>A segunda mensagem foi enviada ao Cliente!\n")
                    conn.sendall(second_message_data)
            conn.close()
if __name__ == "__main__":
    main()