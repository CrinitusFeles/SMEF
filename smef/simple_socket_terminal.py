
import socket

def terminal():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('10.6.1.95', 4005))
    sock.settimeout(1)
    try:
        while True:
            in_data = input('>')
            print(f'sending {in_data.encode()}')
            sock.send(in_data.encode() + b'\r')
            try:
                data = b''
                while True:
                    data += sock.recv(1024)
                    if data.endswith(b'\n\r'):
                        break
                print(data)
            except TimeoutError as tm:
                print(tm)
    except KeyboardInterrupt:
        print('shutting down...')
    sock.close()

if __name__ == '__main__':
    terminal()