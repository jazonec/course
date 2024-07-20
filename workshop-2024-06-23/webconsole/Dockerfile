FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app.py /app
COPY ./static /app/static
COPY ./templates /app/templates

CMD ["python", "app.py"]
