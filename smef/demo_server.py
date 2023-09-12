import random
import socket
from threading import Thread
import os
import selectors
import socket
from datetime import datetime

class DemoServer:
    def __init__(self, daemon: bool = True, **kwargs):
        self.ports = [4001, 4002, 4003, 4004, 4005]
        self.threads = []
        self.debug_print_flag = kwargs.get('debug_print', True)
        self.connections = []
        for i, port in enumerate(self.ports):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.listen(1)
            # sock.settimeout(2)
            # sock.setblocking(False)
            self.threads.append(Thread(name=f'{port} port socket', target=self.routine, args=[sock, i], daemon=daemon))

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

    def routine(self, sock: socket.socket, i: int):
        while True:
            self.debug_print(f'Socket {i} {sock} waiting connection...')
            connection, client_address = sock.accept()
            self.connections.append(connection)
            try:
                self.debug_print('Connected to: ' + str(client_address))
                while True:
                    data: bytes = connection.recv(16)
                    if not data:
                        break
                    decoded_data = data.decode()
                    self.debug_print(f'Get: {decoded_data}')

                    if decoded_data == '*IDN?\r':
                        connection.sendall(b'AR-WORLDWIDE,FI7000,REV3.10\r\n')
                    elif decoded_data == 'I\r':
                        connection.sendall(b':I,FL7040,00357221,_REV_1.80_,01/15/21,S\n\r')
                    elif decoded_data == 'D\r':
                        self.send_sock(connection, i)  # b':D04.1402.0702.2505.14S\n\r'
            except TimeoutError as ex:
                print(ex)
                break
            except KeyboardInterrupt:
                print('Shutdonw...')
            finally:
                connection.close()
                print('connection close')




    def on_connect(self, sock: socket.socket, addr):
        print("Connected by", addr)

    def on_disconnect(self, sock: socket.socket, addr):
        print("Disconnected by", addr)

    def handle(self, sock: socket.socket, addr: str):
        try:
            data = sock.recv(1024)  # Should be ready
        except ConnectionError:
            print(f"Client suddenly closed while receiving")
            return False
        now = datetime.now().astimezone().strftime("%H:%M:%S %d-%m-%Y")
        print(f"{now} > {list(data)} len: {len(data)} from: {addr}")
        if not data:
            print("Disconnected by", addr)
            return False
        sock.send(b'cmd')
        if data[:4] == b'\xad\xde\xaf\xbe':
            path = os.path.join(os.path.dirname(__file__), 'gsm_data.txt')
            with open(path, 'a', encoding='utf-8') as file:
                file.write(f"{now} > {list(data)}\n")
        else:
            sock.close()
        # try:
        #     sock.send(data)  # Hope it won't block
        # except ConnectionError:
        #     print(f"Client suddenly closed, cannot send")
        #     return False
        return True

    def run_server(self, host, port, on_connect, on_read, on_disconnect):
        def on_accept_ready(sel, serv_sock, mask):
            sock, addr = serv_sock.accept()  # Should be ready

            # sock.setblocking(False)
            sel.register(sock, selectors.EVENT_READ, on_read_ready)
            if on_connect:
                on_connect(sock, addr)

        def on_read_ready(sel, sock, mask):
            addr = sock.getpeername()
            if not on_read or not on_read(sock, addr):
                if on_disconnect:
                    on_disconnect(sock, addr)
                sel.unregister(sock)
                sock.close()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serv_sock:
            serv_sock.bind((host, port))
            # serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serv_sock.listen(3)
            serv_sock.setblocking(False)
            sel = selectors.DefaultSelector()
            sel.register(serv_sock, selectors.EVENT_READ, on_accept_ready)
            try:
                while True:
                    print("Waiting for connections or data...")
                    events = sel.select()
                    for key, mask in events:
                        callback = key.data
                        callback(sel, key.fileobj, mask)
            except (KeyboardInterrupt, SystemExit):
                print('Shutdown')



if __name__ == '__main__':
    server = DemoServer()
    server.start_server()
