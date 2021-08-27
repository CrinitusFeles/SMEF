import random
import socket
from threading import Thread


class DemoServer:
    def __init__(self, **kwargs):

        self.socket = [socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                       socket.socket(socket.AF_INET, socket.SOCK_STREAM)]
        self.ports = [4001, 4002, 4003, 4004, 4005]
        self.threads = [None, None, None, None, None]
        self.debug_print_flag = kwargs.get('debug_print', False)

        for sock, port, i in zip(self.socket, self.ports, range(5)):
            sock.bind(('localhost', port))
            sock.listen(1)
            self.threads[i] = Thread(name=str(port) + ' port socket', target=self.start, args=[sock, i], daemon=True)

    def debug_print(self, *args):
        if self.debug_print_flag:
            print(*args)

    def start_server(self):
        for i, thread in enumerate(self.threads):
            self.threads[i].start()

    def start(self, sock, i):
        while True:
            self.debug_print('Socket ' + str(i) + ' waiting connection...')
            connection, client_address = sock.accept()
            try:
                self.debug_print('Connected to: ' + str(client_address))
                while True:
                    data = connection.recv(16)
                    if not data:
                        break
                    decoded_data = data.decode()
                    self.debug_print('Get: ' + str(decoded_data))
                    if decoded_data == '*IDN?\r':
                        connection.sendall(b'AR-WORLDWIDE,FI7000,REV3.10\r\n')
                    elif decoded_data == 'D\r':
                        if i == 0:
                            val = '%.2f' % (random.uniform(-1.0, 1.0) + 16.0)
                            packet = b':D00.00.00.00.00.00.' + str.encode(val) + b'\r\n'
                            self.debug_print(packet)
                            connection.sendall(packet)
                        elif i == 1:
                            val = '%.2f' % (random.uniform(-1.0, 1.0) + 20.0)
                            packet = b':D00.00.00.00.00.00.' + str.encode(val) + b'\r\n'
                            self.debug_print(packet)
                            connection.sendall(packet)
                        elif i == 2:
                            val = '%.2f' % (random.uniform(-1.0, 1.0) + 15.0)
                            packet = b':D00.00.00.00.00.00.' + str.encode(val) + b'\r\n'
                            self.debug_print(packet)
                            connection.sendall(packet)
                        elif i == 3:
                            val = '%.2f' % (random.uniform(-1.0, 1.0) + 13.0)
                            packet = b':D00.00.00.00.00.00.' + str.encode(val) + b'\r\n'
                            self.debug_print(packet)
                            connection.sendall(packet)
                        elif i == 4:
                            val = '%.2f' % (random.uniform(-1.0, 1.0) + 12.0)
                            packet = b':D00.00.00.00.00.00.' + str.encode(val) + b'\r\n'
                            self.debug_print(packet)
                            connection.sendall(packet)
            except Exception as ex:
                print(ex)
            finally:
                connection.close()
                print('connection close')


if __name__ == '__main__':
    server = DemoServer()
    server.start_server()
