'''Взаимодействие с OpenAI'''
from io import BytesIO
import re
import logging
import asyncio
import base64
import httpx
from openai import OpenAI
from config import settings, get_oaiproxy_url
from exceptions import OAICreateImageException

logging.info("proxy: %s", settings.proxy_host)
client = OpenAI(api_key=settings.oai_key,
                http_client=httpx.Client(
                    proxies={"http:": get_oaiproxy_url(),
                         "https:": get_oaiproxy_url()}
                )
)

async def get_prompt(message_text: str):
    """Генерация ответа на запрос."""
    response = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: client.chat.completions.create(
            model=settings.oai_model,
            messages=[
                {"role":"user", "content":message_text}
            ]
        )
    )

    # Access text content from "message" within the first "Choice"
    return escape_markdown(response.choices[0].message.content)

async def get_image(message_text: str):
    """Генерация картинки."""
    response = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: client.images.generate(
            model=settings.oai_dalle_model,
            prompt=message_text,
            n=1,
            size="1024x1024",
            response_format="b64_json")
    )
    if hasattr(response, 'data') and len(response.data) > 0:
        logging.debug("Успешно сгенерирована картинка для запроса %s", message_text)
        return BytesIO(base64.b64decode(response.data[0].b64_json))
    logging.error("Ошибка генерации картинки для запроса %s", message_text)
    raise OAICreateImageException("OAI: Ошибка генерации картинки")

def escape_markdown(text: str) -> str:
    """Helper function to escape telegram markup symbols."""
    escape_chars = r"\_*[]()~>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)
