'''Хэндлеры для взаимодействия с апи телеграмма'''
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import dao, oai
from exceptions import OAICreateImageException

def init_handlers(application: ApplicationBuilder):
    '''Инициализация хэндлеров'''
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler("image", create_image))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_prompt))

async def send_status(action: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Асинхронная отправка статусов в чат'''
    while True:
        logging.debug("Sending status %s...", action)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
        await asyncio.sleep(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Приветствие пользователя'''
    logging.info("Приветствуем нового пользователя %s", update.effective_user.username)
    await dao.create_user(update.effective_chat.id, update.effective_user.username)
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Я искуственный интеллект. Задай мне вопрос.")

async def chat_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Обработка запроса от пользователя'''
    user = update.effective_chat
    allow, why = await dao.is_user_allowed(user.id, user.username, "allow_prompt")
    if not allow:
        logging.info(
            "User %s (%s) tried to use GPT prompt but is not allowed. Cause is %s",
            user.id, user.username, why)
        await update.message.reply_text(
            f"Sorry, you are not allowed to text with me because of '{why}'.",
            reply_to_message_id=update.message.message_id)
        return

    logging.info("User %s, prompt query %s", user.username, update.message.text)
    logging.debug("start typing...")
    typing_task = asyncio.create_task(send_status("typing", update, context))
    ai_response = await oai.get_prompt(update.message.text)
    logging.debug("stop typing...")
    typing_task.cancel()
    await update.message.reply_text(ai_response, quote=True, parse_mode="MarkdownV2")

async def create_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Создание картинки по запросу от пользователя'''
    user = update.effective_chat
    allow, why = await dao.is_user_allowed(user.id, user.username, "allow_dalle")
    if not allow:
        logging.info("User %s (%s) tried to use GPT prompt but is not allowed.",
                     user.id, user.username)
        await update.message.reply_text(
            f"Sorry, you are not allowed to text with me because of '{why}'.",
            reply_to_message_id=update.message.message_id)
        return

    if not context.args:
        logging.error(
            "Пользователь %s (%s) не предоставил описание для генерации картинки в команде /image",
            user.id,user.username)
        await update.message.reply_text(
            "Напиши описание картинки после команды /image",
            reply_to_message_id=update.message.message_id)
        return

    logging.debug("start upload photo...")
    logging.info("User %s, send dall-e query %s", user.username, update.message.text)
    typing_task = asyncio.create_task(send_status("upload_photo", update, context))

    try:
        photo = await oai.get_image(' '.join(context.args))
        await update.message.reply_photo(photo=photo)
    except OAICreateImageException:
        await update.message.reply_text("Упс, что-то пошло не так.",
                                        reply_to_message_id=update.message.message_id)
    finally:
        logging.debug("stop upload photo...")
        typing_task.cancel()
