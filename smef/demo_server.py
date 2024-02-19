import random
import socket
from threading import Thread
import time

class DemoServer:
    def __init__(self, daemon: bool = True, **kwargs):
        self.ports = [4001, 4002, 4003, 4004, 4005]
        self.threads = []
        self.debug_print_flag = kwargs.get('debug_print', True)
        self.connections = []
        for (i, port), probe_id in zip(enumerate(self.ports), range(357217, 3572122)):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.listen(5)
            # sock.settimeout(2)
            # sock.setblocking(False)
            self.threads.append(Thread(name=f'{port} port socket', target=self.routine, args=[sock, i, probe_id],
                                       daemon=daemon))

    def debug_print(self, *args):
        if self.debug_print_flag:
            print(*args)

    def start_server(self):
        for thread in self.threads:
            thread.start()

    def send_sock(self, sock: socket.socket, i: int):
        packet: bytes = b':D00.0000.0000.000' + str.encode(f'{(random.uniform(-1.0, 1.0) + i * 2 + 1):.2f}') + b'S\n\r'
        self.debug_print(packet)
        sock.sendall(packet)

    def routine(self, sock: socket.socket, i: int, probe_id: int):
        print('demo server started at localhost')
        while True:
            self.debug_print(f'Socket {i} waiting connection...')
            connection, client_address = sock.accept()
            self.connections.append(connection)
            try:
                self.debug_print(f'Connected to: {client_address}\n')
                while True:
                    data: bytes = connection.recv(1024)
                    if not data:
                        break
                    decoded_data = data.decode()
                    self.debug_print(f'Get: {decoded_data}\n')

                    if decoded_data == '*IDN?\r':
                        connection.sendall(b'AR-WORLDWIDE,FI7000,REV3.10\r\n')
                    elif decoded_data == 'I\r':
                        connection.sendall(f':I,FL7040,00{probe_id},_REV_1.80_,01/15/21,S\n\r'.encode('utf-8'))
                    elif decoded_data == 'D\r':
                        self.send_sock(connection, i)  # b':D04.1402.0702.2505.14S\n\r'
                    time.sleep(0.001)
            except ConnectionResetError as err:
                print(err)
            except TimeoutError as ex:
                print(ex)
                break
            except KeyboardInterrupt:
                print('Shutdonw...\n')
            finally:
                connection.close()
                print('connection close\n')


if __name__ == '__main__':
    server = DemoServer()
    server.start_server()
    try:
        while True:
            in_data = input('>')
    except KeyboardInterrupt:
        print('shutting down')
