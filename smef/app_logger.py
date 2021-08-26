import os
import sys
import time
import coloredlogs
import logging
coloredlogs.DEFAULT_FIELD_STYLES = {'threadName': {'color': 'red'}, 'levelname': {'bold': True, 'color': 'green'},
                                    'name': {'color': 'blue'}, 'funcName': {'color': 'blue'},
                                    'message': {'color': 'white'}, 'filename': {'color': 'yellow'},
                                    'lineno': {'color': 'blue'}}
_log_format = coloredlogs.ColoredFormatter("[%(levelname)s] [(%(threadName)s)] - %(name)s - "
                                           "[%(filename)s.%(funcName)s():%(lineno)d] - %(message)s")
_log_file_format = logging.Formatter("[%(levelname)s] [(%(threadName)s)] - %(name)s - [%(asctime)s] "
                                     "[%(filename)s.%(funcName)s():%(lineno)d] - %(message)s")

def get_file_handler():
    if not os.path.isdir(os.getcwd() + '/event_log'):
        os.mkdir('event_log')
    file_handler = logging.FileHandler("event_log/event_log" + time.strftime("%Y-%m-%d_%H.%M.%S",
                                                                             time.localtime()) + ".log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(_log_file_format)
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(_log_format)
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())

    sys.excepthook = lambda type_, value, tb: logger.exception(f"Uncaught exception: {type_, value, tb}")

    return logger
