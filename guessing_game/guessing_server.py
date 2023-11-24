import socket
import threading
import random
import time
from typing import List

POLISH_ALPHABET = ['a', 'ą', 'b', 'c', 'ć', 'd', 'e', 'ę', 'f', 'g', 'h', 'i', 'j', 'k',
                  'l', 'ł', 'm', 'n', 'ń', 'o', 'ó', 'p', 'r', 's', 'ś', 't', 'u', 'w', 'y', 'z', 'ż', 'ź']


def get_word() -> str:
    with open('slowa.txt', 'r', encoding='utf-8') as file:
        words = list(file)

    my_word = random.choice(words)
    while len(my_word) < 5:
        my_word = random.choice(words)
    return my_word.replace('\n', '')


def word_obfuscation(word: str, letters: List[str]) -> str:
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
            data = data.replace('\r\n', '').replace('\n', '')
            print(f"Received message from {client_socket.getpeername()}: {data}")
            return data


def handle_client(client_socket, clients, start_game, turn_thread_events, word, word_obfuscated, letters: list, game_finished) -> None:
    client_socket.send(('Please enter your name: \r\n').encode('utf-8'))
    name = get_line(client_socket)

    start_game.wait()
    client_socket.send((f'The game has begun! Wait for your turn, word is {len(word_obfuscated)} letters long\r\n'
                       f'Send a single letter or !<word> to guess\r\n').encode('utf-8'))

    while not game_finished.is_set():
        turn_thread_events[client_socket].wait()
        letters_string = ' ,'.join(letters)
        word_obfuscated = word_obfuscation(word, letters)

        client_socket.send((f'Your turn to enter a letter, word: {word_obfuscated}\r\n'
                           f'Letters used: {letters_string}\r\n').encode('utf-8'))
        player_input = get_line(client_socket)

        if len(player_input) == 1:
            if player_input in word and player_input not in letters:
                letters.append(player_input)
                word_obfuscated = word_obfuscation(word, letters)
                client_socket.send((f'Congrats, your letter is correct! Word after your guess: {word_obfuscated}\r\n').encode('utf-8'))
                if word_obfuscated == word:
                    game_finished.set()
                    broadcast(f'The game is over! Winner is {name}', clients)
                    end_connections(clients)
            elif player_input in letters:
                client_socket.send((f'Letter was already used! You wasted your turn\r\n').encode('utf-8'))
            elif player_input not in word:
                letters.append(player_input)
                client_socket.send((f'Your letter was incorrect! Good luck next time!\r\n').encode('utf-8'))
            else:
                print(f'There seems to be an error in handle_client with letter: {player_input}')
        else:
            if player_input[0] == '!':
                if word == player_input[1:]:
                    client_socket.send((f'Congrats, your guess is correct! Word: {word}\r\n').encode('utf-8'))
                    game_finished.set()
                    broadcast(f'The game is over! Winner is {name}', clients)
                    end_connections(clients)
                else:
                    client_socket.send((f'Your guess is not correct! Word: {word_obfuscated}\r\n').encode('utf-8'))
            else:
                client_socket.send((f'Incorrect input! Don\'t send data when it is not your turn!\r\n').encode('utf-8'))
        turn_thread_events[client_socket].clear()

    clients.remove(client_socket)
    print(f"Connection closed with {name} {client_socket.getpeername()}")
    client_socket.close()


def end_connections(clients):
    for client in clients:
        client.close()
        print(f'Connection closed with {client.getpeername()}')


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
    print('start_game_announcement was sent!')
    broadcast('The game will start in 10s! No players can join\r\n', clients)


def turn_management(turn_thread_events: dict, game_finished) -> None:
    while not game_finished.is_set():
        for event in list(turn_thread_events.values()):
            if game_finished.is_set():
                break
            event.set()
            print(event, '\'s turn')
            time.sleep(10)


def server_logic():
    letters = []
    wait_for_game = 10
    word = get_word()
    print(f'Word for this round: {word}')
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

    announcment_thread = threading.Thread(
        target=announce_start, args=(clients,))
    game_start_thread = threading.Thread(
        target=start_game_delay_seconds, args=(start_game, wait_for_game))
    turn_thread_events = dict()

    while True:
        if not start_game.is_set():
            client, addr = server.accept()
            clients.append(client)
            client_handler = threading.Thread(target=handle_client,
                                              args=(client, clients, start_game, turn_thread_events, word, word_obfuscated, letters, game_finished))
            client_handler.start()
            turn_thread_events[client] = threading.Event()
            if len(clients) >= 2 and not start_game_announcement.is_set():
                start_game_announcement.set()
                announcment_thread.start()
                game_start_thread.start()
                time.sleep(wait_for_game)
                turn_management(turn_thread_events, game_finished)
        else:
            break


if __name__ == "__main__":
    server_logic()
