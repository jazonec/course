'''Взаимодействие с базой данных'''
import logging
import asyncpg
from config import get_db_url
logger = logging.getLogger(__name__)

async def db_connect():
    '''Возвращает подключение к базе данных'''
    logger.info("Connect to database")
    logger.debug("connectionstring = %s", get_db_url())
    try:
        conn = await asyncpg.connect(dsn=get_db_url())
        logger.info(f"Connected to database")
    except Exception as e:
        logger.error(f"Connection ERROR. {e}")
    return conn

async def create_user(user_id: int, username: str):
    '''Создает пользователя'''
    conn = await db_connect()
    try:
        existing_user = await conn.fetchval(
            "SELECT user_id FROM users WHERE user_id = $1", user_id)
        if existing_user is None:
            logger.info("Создаем нового пользователя, id=$1; name=$2", user_id, username)
            result = await conn.execute(
                "INSERT into users(user_id, username) VALUES($1, $2)", user_id, username)
            logger.info("Результат создания %s, id=%s; name=%s", result, user_id, username)
        else:
            logger.info("Пользователь уже существует, id=%s; name=%s", user_id, username)
    except Exception as e:
        logger.error(
            "Ошибка создания нового пользователя, id=%s; name=%s. %s",
            user_id, username, e)
    finally:
        await conn.close()

async def is_user_allowed(user_id: int, username: str, claim: str) -> tuple[bool, str]:
    '''Проверка разрешения на использование бота'''
    conn = await db_connect()
    try:
        logger.info("Проверяем право %s пользователя, id=%s; name=%s", claim, user_id, username)
        user_data = await conn.fetchrow(f'''SELECT COALESCE(balance, 0) as balance, {claim}
                                         FROM users LEFT JOIN user_balance
                                         ON users.user_id = user_balance.user_id
                                         WHERE users.user_id = {user_id}''')
        logger.debug("user_data = %s", user_data)
        if user_data is None:
            return False, "не зарегистрирован"
        if not bool(user_data.get(claim, False)):
            return False, "не разрешено"
        if user_data.get('balance', 0) <= 0:
            return False, "не хватает баланса"
        return True, ""
    except Exception as e:
        logger.error(
            "Ошибка проверки права %s пользователя id=%s; name=%s. %s",
            claim, user_id, username, e)
    finally:
        await conn.close()
