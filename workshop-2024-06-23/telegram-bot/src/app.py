import base64
import httpx
import os
from io import BytesIO
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Я искуственный интеллект. Задай мне вопрос.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text, quote=True)#, reply_to_message_id=update.message.id)

async def chat_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = client.chat.completions.create(
        model=oai_model,
        messages=[
            {"role": "user", "content": update.message.text}
        ]
    )
    # Access text content from "message" within the first "Choice"
    await update.message.reply_text(response.choices[0].message.content, quote=True)

async def create_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Напиши описание картинки после команды /image", reply_to_message_id=update.message.message_id)
        return
        
    prompt = ' '.join(context.args)
    response = client.images.generate(
        model=oai_dalle_model,
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="b64_json")
    if hasattr(response, 'data') and len(response.data) > 0:
        await update.message.reply_photo(photo=BytesIO(base64.b64decode(response.data[0].b64_json)))
    else:
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