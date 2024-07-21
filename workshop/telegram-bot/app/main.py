import logging
from config import settings
import handlers, oai, logger
from telegram import Update
from telegram.ext import ApplicationBuilder

logger.init_logger()

application = ApplicationBuilder().token(settings.bot_key).build()
logging.info("Инициализирую хэндлеры...")
handlers.init_handlers(application)
logging.info("Запускаю бот...")
logging.info(f"Модель промтов: {settings.oai_model}")
logging.info(f"Модель dall-e: {settings.oai_dalle_model}")
application.run_polling(allowed_updates=Update.ALL_TYPES)
