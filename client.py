import sys
import os
import socket
import pickle
import hashlib
import time
import random
from utilities import getPass, encryptAES, decryptAES, parse_message, newUser, createUser, createASUser, userLogin   

# Variaveis
host = '127.0.0.1'
as_port = 48792
tgs_port = 35146
service_port = 35142

def service(username):
    ticket_duration = input("Informe a duração desejada do ticket em minutos: ") #T_R
    try:
        ticket_duration = int(ticket_duration)
    except ValueError:
        print("Duração incorreta")
        sys.exit()
    
    client_key = getPass(username)[:32] #Kc
    client_identifier = username # ID_C
    service_identifier = "portal" #ID_S
    first_random = random.getrandbits(32) #N1
    first_random = '%08x' % first_random 
    
    client_key = client_key.encode()
    buffer = f"{service_identifier},{ticket_duration},{first_random}"
    first_message = [client_identifier, encryptAES(buffer, client_key)]

    # Envia a primeira mensagem para o serverAS.py
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        time.sleep(5)
        sock.connect((host,as_port))
        first_message_data = pickle.dumps(first_message)
        print("\n>>A primeira mensagem foi enviada ao servidor AS!\n")
        sock.sendall(first_message_data)
        
        # Espera pela segunda mensagem do serverAS.py
        second_message = sock.recv(1024)
        second_message = pickle.loads(second_message) #M2

    # Verifica se o primeiro número aleatório está correto
    decrypted_message = decryptAES(second_message[0],client_key)
    decrypted_message = parse_message(decrypted_message)

    if(decrypted_message[1] != first_random):
        print("-------Número aleatório 1 está incorreto-------")
        sys.exit()

    print("<<A segunda mensagem foi recebida do servidor AS!\n")
    client_key_tgs = decrypted_message[0] #K_c_tgs
    client_key_tgs = client_key_tgs.encode()

    second_random = random.getrandbits(32) #N2
    second_random = '%08x' % second_random

    buffer = f"{client_identifier},{service_identifier},{ticket_duration},{second_random}"
    third_message =[encryptAES(buffer, client_key_tgs), second_message[1]]#M3

    # Envia a terceira mensagem para o serverTGS.py
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        time.sleep(5)
        sock.connect((host,tgs_port))
        third_message_data = pickle.dumps(third_message)
        print(">>A terceira mensagem foi enviada ao servidor TGS!\n")
        sock.sendall(third_message_data)
        
        # Espera pela quarta mensagem do serverTGS.py
        fourth_message = sock.recv(1024)
        fourth_message = pickle.loads(fourth_message) #M4

    decrypted_message = decryptAES(fourth_message[0],client_key_tgs)
    decrypted_message = parse_message(decrypted_message)
    # Verifica se o segundo número aleatório está correto
    if(decrypted_message[2] != second_random):
        print("-------Número aleatório 2 está incorreto-------\n")
        sys.exit()     

    print("<<A quarta mensagem foi recebida do servidor TGS!\n")
    client_key_service = decrypted_message[0] #K_c_s
    client_key_service = client_key_service.encode()
    client_ticket_duration_service = decrypted_message[1] #T_A

    requested_service = 'validate' #S_R

    print(f'!! Você possui até {time.ctime(float(client_ticket_duration_service))} para utilizar nossos serviços !!\n')

    third_random = random.getrandbits(32) #N3
    third_random = '%08x' % third_random

    buffer = f"{client_identifier},{client_ticket_duration_service},{requested_service},{third_random}"

    fifth_message =[encryptAES(buffer, client_key_service), fourth_message[1]]#M3

    # Envia a quinta mensagem para o serverService.py
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        time.sleep(5)
        sock.connect((host,service_port))
        fifth_message_data = pickle.dumps(fifth_message)
        while(True):
            sock.sendall(fifth_message_data)
            print(">>A quinta mensagem foi enviada ao servidor de Serviços!\n")

            # Espera pela sexta mensagem do serverService.py
            sixth_message = sock.recv(1024)
            sixth_message = pickle.loads(sixth_message) #M6

            decrypted_message = decryptAES(sixth_message[0],client_key_service)
            decrypted_message = parse_message(decrypted_message)
    # Verifica se o terceiro número aleatório está correto
            if(decrypted_message[1] != third_random):
                print("-------Número aleatório 3 está incorreto-------\n")
                sys.exit()

            print("<<A sexta mensagem foi recebida do servidor de Serviços!\n")

            service_answer = decrypted_message[0]
            if(service_answer == '404'):
                print("!! Ticket expirado !!\n")
                sys.exit()
            else:
                print(service_answer)
            time.sleep(10)

def main():
    option = input('1 - Criar usuário\n2 - Login\nOutra opção - Sair\n')
    input("         Pressione uma tecla para avançar...")
    os.system('clear')
    if(option == '1'):
        username = input("Nome: ")
        
        if(newUser(username)):
            password = input("Senha: ")
            password = hashlib.sha256(password.encode()).hexdigest()
            createUser(username, password)
            createASUser(username,password)

            print("Usuário cadastrado")
        else:
            print("Usuário já existe")
            input("         Pressione uma tecla para encerrar...")
            os.system('clear')
            sys.exit()

    elif(option == '2'):
        username = input("Usuário: ")
        password = input("Senha: ")

        password = hashlib.sha256(password.encode()).hexdigest()

        if (userLogin(username, password)):
            print('Autenticado')
            input("         Pressione uma tecla para avançar...")
            os.system('clear')
            action = input('1 - Acessar serviço\nOutra opção - Sair\n')
            if(action == '1'):
                input("         Pressione uma tecla para avançar...")
                os.system('clear')
                service(username)
            else:
                input("         Pressione uma tecla para encerrar...")
                os.system('clear')
                sys.exit()
        else:
            print("Credenciais incorretas")
            input("         Pressione uma tecla para encerrar...")
            os.system('clear')
            sys.exit()
    else:
        sys.exit()
    input("         Pressione uma tecla para encerrar...")
    os.system('clear')

if __name__ == "__main__":
    main()