import telnetlib

if __name__ == "__main__":
    tn = telnetlib.Telnet("127.0.0.1", 12345) 
    while True:
        data = tn.read_very_eager()
        if data != b'':
            print(data.decode('ascii'))
        user_input = input("Enter a message: ")
        tn.write(user_input.encode('ascii') + b'\n')