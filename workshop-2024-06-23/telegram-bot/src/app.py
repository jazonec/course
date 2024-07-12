import base64
import httpx
import os
import re
import asyncio
import logging
from io import BytesIO
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI
from logfmter import Logfmter

formatter = Logfmter(
    keys=["at", "process", "level", "msg"],
    mapping={"at": "asctime", "process": "processName", "level": "levelname", "msg": "message"},
    datefmt='%H:%M:%S %d/%m/%Y'
)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
file_handler = logging.FileHandler("./logs/bot.log")
file_handler.setFormatter(formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[stream_handler, file_handler])

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

oai_key = os.getenv("OAIKEY")
oai_model = os.getenv("OAIMODEL")
oai_dalle_model = os.getenv("OAIDALLEMODEL")
bot_key = os.getenv("BOTKEY")
proxy_host = os.getenv("PROXYHOST")
proxy_user = os.getenv("PROXYLOGIN")
proxy_pass = os.getenv("PROXYPASS")
client = OpenAI(api_key=oai_key,
                http_client=httpx.Client(
                    proxies={"http:": f"http://{proxy_user}:{proxy_pass}@{proxy_host}",
                             "https:": f"http://{proxy_user}:{proxy_pass}@{proxy_host}"}
                             ))

async def send_status(action: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        logger.debug(f"{action}...")
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
        await asyncio.sleep(2)

def escape_markdown(text: str) -> str:
    """Helper function to escape telegram markup symbols."""

    escape_chars = r"\_*[]()~>#+-=|{}.!"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Приветствуем нового пользователя {update.effective_user.username}")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Я искуственный интеллект. Задай мне вопрос.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text, quote=True)#, reply_to_message_id=update.message.id)

async def chat_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    logging.info(f"User {update.effective_chat.username}, prompt query {update.message.text}]")
    logging.debug("start typing...")
    typing_task = asyncio.create_task(send_status("typing", update, context))

    response = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: client.chat.completions.create(
            model=oai_model,
            messages=[
                {"role":"user", "content":update.message.text}
            ]
        )
    )

    logging.debug("stop typing...")
    typing_task.cancel()
    # Access text content from "message" within the first "Choice"
    ai_response = escape_markdown(response.choices[0].message.content)
    await update.message.reply_text(ai_response, quote=True)

async def create_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not context.args:
        logging.error(f"Пользователь {user.id} ({user.username}) не предоставил описание для генерации картинки в команде /image")
        await update.message.reply_text("Напиши описание картинки после команды /image", reply_to_message_id=update.message.message_id)
        return
        
    logging.debug("start upload photo...")
    logging.info(f"User {user.username}, dall-e query {update.message.text}]")
    typing_task = asyncio.create_task(send_status("upload_photo", update, context))

    prompt = ' '.join(context.args)
    response = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: client.images.generate(
            model=oai_dalle_model,
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json")
    )

    logging.debug("stop upload photo...")
    typing_task.cancel()
    if hasattr(response, 'data') and len(response.data) > 0:
        logging.error(f"Успешно сгенерирована картинка для запроса {prompt}")
        await update.message.reply_photo(photo=BytesIO(base64.b64decode(response.data[0].b64_json)))
    else:
        logging.error(f"Ошибка генерации картинки для запроса {prompt}")
        await update.message.reply_text("Упс, что-то пошло не так.",
                                        reply_to_message_id=update.message.message_id)
    

def main() -> None:
    """Запускаем бота"""
    logging.info("Запускаю бот...")
    logging.info(f"Модель промтов: {oai_model}")
    logging.info(f"Модель dall-e: {oai_dalle_model}")
    logging.info(f"proxy: {proxy_host}")
    application = ApplicationBuilder().token(bot_key).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("image", create_image))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_prompt))

    application.run_polling()

if __name__ == '__main__':
    main()