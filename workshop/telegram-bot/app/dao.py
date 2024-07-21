from config import get_db_url
import asyncpg
import logging

async def db_connect():
    logging.info(f"Connect to database")
    logging.debug(f"connectionstring = {get_db_url()}")
    try:
        conn = await asyncpg.connect(dsn=get_db_url())
        logging.info(f"Connected to database")
    except Exception as e:
        logging.error(f"Connection ERROR. {e}")
    return conn

async def create_user(user_id: int, username: str):
    conn = await db_connect()
    try:
        existing_user = await conn.fetchval("SELECT user_id FROM users WHERE user_id = $1", user_id)
        if existing_user is None:
            logging.info(f"Создаем нового пользователя, id={user_id}; name={username}")
            result = await conn.execute("INSERT into users(user_id, username) VALUES($1, $2)", user_id, username)
            logging.info(f"Результат создания {result}, id={user_id}; name={username}")
        else:
            logging.info(f"Пользователь уже существует, id={user_id}; name={username}")
    except Exception as e:
        logging.error(f"Ошибка создания нового пользователя, id={user_id}; name={username}. {e}")
    finally:
        await conn.close()

async def is_user_allowed(user_id: int, username: str, claim: str) -> tuple[bool, str]:
    conn = await db_connect()
    try:
        logging.info(f"Проверяем право {claim} пользователя, id={user_id}; name={username}")
        user_data = await conn.fetchrow(f"SELECT COALESCE(balance, 0) as balance, {claim} FROM users LEFT JOIN user_balance ON users.user_id = user_balance.user_id WHERE users.user_id = $1", user_id)
        logging.debug(f"user_data = {user_data}")
        if user_data is None:
            return False, "не зарегистрирован"
        elif not bool(user_data.get(claim, False)):
            return False, "не разрешено"
        elif user_data.get('balance', 0) <= 0:
            return False, "не хватает баланса"
        else:
            return True, ""
        #return False if claim_granted is None else bool(claim_granted)
    except Exception as e:
        logging.error(f"Ошибка проверки права {claim} пользователя id={user_id}; name={username}. {e}")
    finally:
        await conn.close()
