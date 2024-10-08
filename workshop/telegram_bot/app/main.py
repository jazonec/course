'''Основной модуль'''
import logging
from logfmter import Logfmter
from config import settings

formatter = Logfmter(
    keys=["at", "process", "level", "msg"],
    mapping={"at": "asctime", "process": "processName", "level": "levelname", "msg": "message"},
    datefmt='%H:%M:%S %d/%m/%Y'
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
enabled_handlers = [stream_handler]
if settings.LOG_TO_FILE == "true":
    file_handler = logging.FileHandler("./logs/bot.log")
    file_handler.setFormatter(formatter)
    enabled_handlers.append(file_handler)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.INFO,
    handlers=enabled_handlers
)

from telegram import Update
from telegram.ext import ApplicationBuilder
import handlers

application = ApplicationBuilder().token(settings.bot_key).build()
handlers.init_handlers(application)
logging.info("Запускаю бот...")
logging.info("Модель промтов: %s", settings.oai_model)
logging.info("Модель dall-e: %s", settings.oai_dalle_model)
application.run_polling(allowed_updates=Update.ALL_TYPES)
