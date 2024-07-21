import os

class Settings():
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

settings = Settings()


def get_db_url():
    return (f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

def get_oaiproxy_url():
    return(f"http://{settings.proxy_user}:{settings.proxy_pass}@{settings.proxy_host}")