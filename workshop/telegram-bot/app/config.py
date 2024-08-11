''' Модуль обеспечивает настройки для остальных модулей'''
import os
from dataclasses import dataclass

@dataclass
class Settings():
    ''' Класс хранит настройки приложения '''
    oai_key = os.getenv("OAIKEY")
    oai_model = os.getenv("OAIMODEL")
    oai_dalle_model = os.getenv("OAIDALLEMODEL")
    bot_key = os.getenv("BOTKEY")
    proxy_host = os.getenv("PROXYHOST")
    proxy_user = os.getenv("PROXYLOGIN")
    proxy_pass = os.getenv("PROXYPASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_NAME = os.getenv("POSTGRES_DB")
    LOG_TO_FILE = os.getenv("LOG_TO_FILE", "False").lower()

settings = Settings()

def get_db_url():
    '''Возвращает строку подключения к базе данных'''
    _url = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    _url = _url + f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    return _url

def get_oaiproxy_url():
    '''Возвращает строку подключения к прокси (для OpenAI)'''
    return f"http://{settings.proxy_user}:{settings.proxy_pass}@{settings.proxy_host}"
