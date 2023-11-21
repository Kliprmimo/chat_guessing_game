import telnetlib
import threading

IP = "127.0.0.1"
PORT = 12345

def receive_data(tn):
    while True:
        data = tn.read_very_eager()
        if data != b'':
            print(data.decode('ascii').replace('\r\n', '').replace('\n', ''))

tn = telnetlib.Telnet(IP, PORT)

receive_thread = threading.Thread(target=receive_data, args=(tn,))
receive_thread.start()

try:
    while True:
        user_input = input("")
        tn.write(user_input.encode('ascii') + b'\n')

except KeyboardInterrupt:
    tn.close()