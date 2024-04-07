import socket
import ssl
import threading

def receive_data(ssl_socket, end_event):
    while not end_event.is_set():
        data = ssl_socket.recv(1024).decode('utf-8')
        if data != '':
            print(f"{data}")


if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 12345
    CERT_FILE = 'client.crt'
    KEY_FILE = 'client.key'

    print('to exit chat type: exit()')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations('ssl.pem')

    with context.wrap_socket(client_socket, server_hostname=HOST) as ssl_socket:   
        end_chat = threading.Event()
        receive_thread = threading.Thread(target=receive_data, args=(ssl_socket, end_chat)) 
        receive_thread.start()
        
        while not end_chat.is_set():
            user_input = input("")
            if user_input == 'exit()':
                end_chat.set()
                ssl_socket.close()
                receive_thread.join()
                exit()
            ssl_socket.send((user_input).encode('utf-8'))
        
