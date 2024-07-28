FROM python:3.9-slim

WORKDIR /tgbot

COPY ./requirements.txt /tgbot
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /tgbot/app

CMD ["python", "app/main.py"]
