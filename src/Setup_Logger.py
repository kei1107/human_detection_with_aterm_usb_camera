import logging
import os


def Setup_Logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    log_file_path = os.path.join(os.path.abspath('.'), 'log')
    log_file_path = os.path.join(log_file_path, 'human_detection.log')
    fh = logging.FileHandler(log_file_path)
    logger.addHandler(fh)

    sh = logging.StreamHandler()
    logger.addHandler(sh)

    formatter = logging.Formatter(
        '%(asctime)s:%(lineno)d:%(levelname)s:%(message)s')
    fh.setFormatter(formatter)
    sh.setFormatter(formatter)

    return logger
