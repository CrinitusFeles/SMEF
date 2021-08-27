import re
try:
    from .app_logger import *
except Exception as ex:
    from app_logger import *

logger = get_logger(__name__)


def read_sensor_ident(sock):
    try:
        ident = read_ident(sock)
        if ident != '':
            return True
        else:
            return False
    except Exception as ex:
        logger.error('Read identificator error:' + str(ex))
        return False


def read_ident(sock):
    answer = ''
    data_counter = 0
    sock.send('*IDN?\r'.encode())
    try:
        while True:
            data = sock.recv(1024)
            answer += data.decode()
            data_counter += len(data)
            if data[-1] == b'\r' or data_counter >= 29 or answer == 'AR-WORLDWIDE,FI7000,REV3.10':
                break
        logger.info('Sensor identificator:' + str(answer))
        return answer
    except Exception as ex:
        logger.warning('Can\'t read sensor identificator:' + str(ex) + '| read ' + str(data_counter) + ' bytes: ' + str(answer))
        return answer


def read_single_probe(sock):
    answer = ''
    bytes_array = b''
    data_counter = 0
    try:
        sock.send('D\r'.encode())
        while True:
            data = sock.recv(2048)
            bytes_array += data
            answer += data.decode()
            data_counter += len(data)
            if data_counter >= 25 or bytes_array[-1] == '\n':
                break
        # print(answer)
        # fields = [float(x) for x in re.findall(r'\d{2}\.{1}\d{2}', answer)]
        fields = [float(x) for x in re.findall(r'\d{2}\.\d{2}', answer)]
        return fields
    except Exception as ex:
        logger.error('Error at %s', 'socket', exc_info=ex)
        logger.info('Read ' + str(data_counter) + ' bytes: ' + str(answer))
