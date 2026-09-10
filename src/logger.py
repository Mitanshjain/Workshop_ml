import logging   # logging is a built-in Python module used to record what your program is doing.

import os        # os is also a built-in Python module, but it is used to interact with the operating system.

from datetime import datetime

# Logs folder creation
LOGS_DIR = os.path.join(os.getcwd(),"logs")
os.makedirs(LOGS_DIR,exist_ok=True)

# Logs file creation means hows the log goes into log folder
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"   # geting current datetime using now, tehn use string forward time that 
                                                                    # how organize our time and .log is extension.

LOG_FILE_PATH = os.path.join(LOGS_DIR,LOG_FILE)


logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s -%(levelname)s -%(message)s",
    level = logging.INFO
)

def get_logger(name:str = __name__) -> None:
    logger = logging.getLogger(name)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s -%(name)s -%(message)s"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger

if __name__ == "__main__":
    log = get_logger(__name__)
    log.info("Logger test message - Logs Started")