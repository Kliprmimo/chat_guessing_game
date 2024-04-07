import socket
import threading
import ssl
import signal
from functools import partial

# niestety z niewiadomych mi przyczyn nie byłem w stanie sprawić aby sygnał SIGINT był łapany przez program
# przez to nie da się zabić procesu poprzez ctr +c


# def handler(signum, frame):
#     print('ctr+c was pressed')

def handle_client(client_socket):
    client_socket.send(('Please enter your name: ').encode('utf-8'))
    print('client just joined!')
    name = client_socket.recv(1024).decode('utf-8')

    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data != '':
            print(f"Received message from {name} {client_socket.getpeername()}: {data}")
            broadcast_exclude(f'{name}: {data}', client_socket)


    # clients.remove(client_socket)
    # print(f"Connection closed with {name} {client_socket.getpeername()}")
    # client_socket.close()


def broadcast(message):
    for client in clients:
        try:
            client.send((message).encode('utf-8'))
        except:
            clients.remove(client)


def broadcast_exclude(message, client_excluded):
    for client in clients:
        if client != client_excluded:
            try:
                client.send((message).encode('utf-8'))
            except:
                clients.remove(client)

if __name__ == '__main__':
    # partial_handler = partial(handler)
    # signal.signal(signal.SIGINT, partial_handler)

    HOST = '0.0.0.0'
    PORT = 12345
    CERT_FILE = 'server.crt'
    KEY_FILE = 'server.key'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))  
    server.listen(5)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ssl.pem', 'private.key')

    print(f"[*] Listening on  {HOST}:{str(PORT)}")

    clients = []
    with context.wrap_socket(server, server_side=True) as secure_server:
        while True:
            client, addr = secure_server.accept()
            clients.append(client)
            client_handler = threading.Thread(target=handle_client, args=(client,))
            client_handler.start()
