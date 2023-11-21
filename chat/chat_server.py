import socket
import threading


def get_line(client_socket):
    data = ''
    while True:
        char = client_socket.recv(1024).decode('utf-8')
        data += char
        if char in ['\n', '\r\n'] or '\n' in char or '\r\n' in char:
            print(f"Received message from {client_socket.getpeername()}: {data}")
            return data.replace('\r\n', '').replace('\n', '')


def handle_client(client_socket):
    client.send(('Please enter your name: ').encode('utf-8'))
    name = get_line(client_socket)
    data = ''
    while True:
        char = client_socket.recv(1024).decode('utf-8')
        data += char
        if char in ['\n', '\r\n'] or '\n' in char or '\r\n' in char:
            print(
                f"Received message from {name} {client_socket.getpeername()}: {data}")
            broadcast_exclude(f'{name}: {data}', client_socket)
            data = ''
            

        if not char:
            break

    clients.remove(client_socket)
    print(f"Connection closed with {name} {client_socket.getpeername()}")
    client_socket.close()


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
    
    PORT = 12345
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))  
    server.listen(5)

    print("[*] Listening on  0.0.0.0:",str(PORT))

    clients = []

    while True:
        client, addr = server.accept()
        clients.append(client)
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()
