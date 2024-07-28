import logging
import asyncpg
from config import get_db_url
logger = logging.getLogger(__name__)

async def db_connect():
    logger.info(f"Connect to database")
    logger.debug(f"connectionstring = {get_db_url()}")
    try:
        conn = await asyncpg.connect(dsn=get_db_url())
        logger.info(f"Connected to database")
    except Exception as e:
        logger.error(f"Connection ERROR. {e}")
    return conn

async def create_user(user_id: int, username: str):
    conn = await db_connect()
    try:
        existing_user = await conn.fetchval("SELECT user_id FROM users WHERE user_id = $1", user_id)
        if existing_user is None:
            logger.info(f"Создаем нового пользователя, id={user_id}; name={username}")
            result = await conn.execute(
                "INSERT into users(user_id, username) VALUES($1, $2)", user_id, username)
            logger.info(f"Результат создания {result}, id={user_id}; name={username}")
        else:
            logger.info(f"Пользователь уже существует, id={user_id}; name={username}")
    except Exception as e:
        logger.error(f"Ошибка создания нового пользователя, id={user_id}; name={username}. {e}")
    finally:
        await conn.close()

async def is_user_allowed(user_id: int, username: str, claim: str) -> tuple[bool, str]:
    conn = await db_connect()
    try:
        logger.info(f"Проверяем право {claim} пользователя, id={user_id}; name={username}")
        user_data = await conn.fetchrow(f'''SELECT COALESCE(balance, 0) as balance, {claim} 
                                        FROM users LEFT JOIN user_balance 
                                        ON users.user_id = user_balance.user_id 
                                        WHERE users.user_id = {user_id}''')
        logger.debug(f"user_data = {user_data}")
        if user_data is None:
            return False, "не зарегистрирован"
        elif not bool(user_data.get(claim, False)):
            return False, "не разрешено"
        elif user_data.get('balance', 0) <= 0:
            return False, "не хватает баланса"
        else:
            return True, ""
    except Exception as e:
        logger.error(
            f"Ошибка проверки права {claim} пользователя id={user_id}; name={username}. {e}")
    finally:
        await conn.close()
