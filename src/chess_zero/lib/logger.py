import logging
import os
from logging import DEBUG, Formatter, StreamHandler, basicConfig, getLogger

from chess_zero.config import ResourceConfig


def setup_basic_logger(log_filename):
    pass
    # format_str = '%(asctime)s@%(name)s %(levelname)s # %(message)s'
    # basicConfig(filename=log_filename, level=DEBUG, format=format_str)
    # stream_handler = StreamHandler()
    # stream_handler.setFormatter(Formatter(format_str))
    # getLogger().addHandler(stream_handler)

def setup_module_logger(logger, logfile):
    rc = ResourceConfig()

    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.join(rc.log_dir, logfile))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(process)d:%(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


if __name__ == '__main__':
    setup_basic_logger("aa.log")
    logger = getLogger("test")
    logger.info("OK")
