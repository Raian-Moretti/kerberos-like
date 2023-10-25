import pickle
import socket
import time
from utilities import encryptAES, decryptAES, parse_message, getKey  


host = '127.0.0.1'
port = 35142

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host,port))
        while True:
            sock.listen()
            conn, addr = sock.accept()
            with conn:
                connectionStatus = True
                while connectionStatus:
                    fifth_message_data = conn.recv(1024)
                    if(not fifth_message_data):
                        connectionStatus = False
                    else:
                        # Recebe mensagem do client.py
                        print("<<A quinta mensagem foi recebida do Cliente!\n")
                        fifth_message = pickle.loads(fifth_message_data)

                        answer = '200'
                        service_key = getKey('service')
                        service_key = service_key.encode()
                        sh_decrypted_message = decryptAES(fifth_message[1],service_key) #SecondHalf_M5
                        sh_decrypted_message = parse_message(sh_decrypted_message)

                        client_ticket_key_service = sh_decrypted_message[2] #K_c_s
                        client_ticket_key_service = client_ticket_key_service.encode()

                        fh_decrypted_message = decryptAES(fifth_message[0],client_ticket_key_service) #FirstHalf_M5
                        fh_decrypted_message = parse_message(fh_decrypted_message)

                        client_identifier = fh_decrypted_message[0] #ID_C
                        print(client_identifier)
                        client_ticket_duration_service = fh_decrypted_message[1] #T_A
                        requested_service = fh_decrypted_message[2] #S_R
                        third_random = fh_decrypted_message[3] #N3

                        if(requested_service == 'validate'):
                            answer = f'<<Olá {str(client_identifier)} seu ticket é válido no servidor de Serviços\n'
                        if(time.time() > float((client_ticket_duration_service))):
                            answer = '404'
                        
                        buffer = f"{answer},{third_random}"

                        sixth_message = [encryptAES(buffer, client_ticket_key_service)] #M4
                        
                        sixth_message_data = pickle.dumps(sixth_message)
                        print(">>A sexta mensagem foi enviada ao Cliente!\n")
                        conn.sendall(sixth_message_data)
            conn.close()

if __name__ == "__main__":
    main()