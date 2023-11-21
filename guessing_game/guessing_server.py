import socket
import threading
import random
import time
from typing import List

POLISH_ALPHABET = ['a', 'ą', 'b', 'c', 'ć', 'd', 'e', 'ę', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'ł', 'm', 'n', 'ń', 'o', 'ó', 'p', 'r', 's', 'ś', 't', 'u', 'w', 'y', 'z', 'ż', 'ź'] 

def get_word() -> str:
    with open('slowa.txt', 'r', encoding='utf-8') as file:
        words = list(file)

    my_word = random.choice(words)
    while len(my_word) < 5:
        my_word = random.choice(words)
    return my_word.replace('\n', '')

def word_obfuscation(word:str, letters: List[str]) -> str:
    new_word = ''
    for letter in word:
        if letter in letters:
            new_word += letter
        else:
            new_word += '_'
    return new_word

def get_line(client_socket) -> str:
    data = ''
    while True:
        char = client_socket.recv(1024).decode('utf-8')
        data += char
        if char in ['\n', '\r\n'] or '\n' in char or '\r\n' in char:
            print(f"Received message from {client_socket.getpeername()}: {data}")
            return data.replace('\r\n', '').replace('\n', '')

def handle_client(client_socket, clients, start_game, turn_thread_events, word, word_obfuscated, letters:list, game_finished)-> None:
    client_socket.send(('Please enter your name: ').encode('utf-8'))
    name = get_line(client_socket)
    data = ''
    start_game.wait()    
    client_socket.send((f'The game has begun! Wait for you turn , word is {len(word_obfuscated)} letters long\n send single letter or !<word> to guess\n').encode('utf-8'))
    while not game_finished.is_set():
        turn_thread_events[client_socket].wait()
        letters_string  = ' ,'.join(letters)
        client_socket.send((f'Your turn to enter a letter, word: {word_obfuscated}\nletters used: {letters_string}\n').encode('utf-8'))
        input = get_line(client_socket)
        if len(input) == 1:
            if input in word and input not in letters:
                word_obfuscated = word_obfuscation( word_obfuscated, letters)
                client_socket.send((f'Congrats, your letter is correct! word after your guess: {word_obfuscated}\n').encode('utf-8'))
            elif input in letters:
                client_socket.send((f'Letter was already used! You wasted your turn\n').encode('utf-8'))
            elif input not in word:
                client_socket.send((f'Your letter was incorrect! Good luck next time!\n').encode('utf-8'))
            else:
                print(f'There seems to be an error in hadndle_client with letter: {input}')
        else:
            if input[0] == '!':
                if word == input[1:]:
                    client_socket.send((f'Congrats, your guess is correct! word: {word}\n').encode('utf-8'))
                    game_finished.set()
                else:
                    client_socket.send((f'Your guess is not correct! word: {word_obfuscated}\n').encode('utf-8'))

            #to_do check logic



    # while True:
    #     char = client_socket.recv(1024).decode('utf-8')
    #     data += char
    #     if char in ['\n', '\r\n'] or '\n' in char or '\r\n' in char:
    #         print(f"Received message from {name} {client_socket.getpeername()}: {data}")
    #         data = ''
            
    #     if not char:
    #         break

    clients.remove(client_socket)
    print(f"Connection closed with {name} {client_socket.getpeername()}")
    client_socket.close()

def broadcast(message, clients) -> None:
    for client in clients:
        try:
            client.send((message).encode('utf-8'))
        except:
            clients.remove(client)

def broadcast_exclude(message, client_excluded, clients) -> None:
    for client in clients:
        if client != client_excluded:
            try:
                client.send((message).encode('utf-8'))
            except:
                clients.remove(client)

def start_game_delay_seconds(start_game, seconds) -> None:
    time.sleep(seconds)
    start_game.set()

def announce_start(clients) -> None:
    print('start_game_announcement was sent!\n')
    broadcast('The game will start in 30s! No players can join', clients)

def turn_management(turn_thread_events: dict) -> None:
    for client in list(turn_thread_events.keys()):
         turn_thread_events[client].set()
         time.sleep(10)

def server_logic():
    letters = []
    word = get_word()
    word_obfuscated = word_obfuscation(word, letters)
    PORT = 12345
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))  
    server.listen(10)
    print("[*] Listening on 0.0.0.0:", str(PORT))

    clients = []

    start_game_announcement = threading.Event()
    start_game = threading.Event()
    game_finished = threading.Event()
    
    announcment_thread = threading.Thread(target=announce_start, args=(clients,))
    game_start_thread = threading.Thread(target=start_game_delay_seconds, args = (start_game, 30))
    turn_thread_events = dict()

    while True:
        if not start_game.is_set():
            client, addr = server.accept()
            clients.append(client)
            turn_thread_events[client] = threading.Event()
            if len(clients) >= 2 and not start_game_announcement.is_set():
                start_game_announcement.set()
                announcment_thread.start()
                game_start_thread.start()
                turn_management(turn_thread_events)
            client_handler = threading.Thread(target=handle_client, args=(client, clients, start_game, turn_thread_events, word, word_obfuscated, letters ,game_finished))
            client_handler.start()
        else:
            break

if __name__ == "__main__":
    server_logic()
