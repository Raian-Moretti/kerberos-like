import string
import random
import pickle
import socket
import time
from utilities import encryptAES, decryptAES, parse_message, getKey, rotateKey 

host = '127.0.0.1'
port = 35146

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host,port))
        while True:
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                connectionStatus = True
                while connectionStatus:
                    third_message_data = conn.recv(1024)
                    if(not third_message_data):
                        connectionStatus = False
                    else:
                        # Recebe mensagem do client.py
                        print("<<A terceira mensagem foi recebida do Cliente!")
                        third_message = pickle.loads(third_message_data) #M3
                        tgs_key = getKey('tgs')
                        tgs_key = tgs_key.encode()

                        sh_decrypted_message = decryptAES(third_message[1], tgs_key) #SecondHalf_M3
                        sh_decrypted_message = parse_message(sh_decrypted_message)
                        client_key_tgs = sh_decrypted_message[2] #K_c_tgs
                        client_key_tgs = client_key_tgs.encode()

                        fh_decrypted_message = decryptAES(third_message[0], client_key_tgs) #FirstHalf_M3
                        fh_decrypted_message = parse_message(fh_decrypted_message)
                        client_ticket_identifier_service = fh_decrypted_message[0] #ID_C
                        client_ticket_duration_tgs = fh_decrypted_message[2] #T_R
                        second_random = fh_decrypted_message[3] #N2

                        client_key_service = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)) #K_c_s
                        time_auth = time.time() + int(client_ticket_duration_tgs)*60 #T_A
                        rotateKey('service')
                        client_ticket_key_service = getKey('service') #K_s
                        client_ticket_key_service = client_ticket_key_service.encode()

                        buffer_1 = f"{client_key_service},{time_auth},{second_random}"
                        buffer_2 = f"{client_ticket_identifier_service},{time_auth},{client_key_service}"
                        fourth_message = [encryptAES(buffer_1, client_key_tgs), encryptAES(buffer_2, client_ticket_key_service)] #M4
                        

                        fourth_message_data = pickle.dumps(fourth_message)
                        time.sleep(5)
                        print(">>A quarta mensagem foi enviada ao Cliente!")
                    conn.sendall(fourth_message_data)
            conn.close()

if __name__ == "__main__":
     main()