import logging
from logfmter import Logfmter
import httpx

def init_logger():
    formatter = Logfmter(
        keys=["at", "process", "level", "msg"],
        mapping={"at": "asctime", "process": "processName", "level": "levelname", "msg": "message"},
        datefmt='%H:%M:%S %d/%m/%Y'
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler("./logs/bot.log")
    file_handler.setFormatter(formatter)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.INFO,
        handlers=[stream_handler, file_handler])
