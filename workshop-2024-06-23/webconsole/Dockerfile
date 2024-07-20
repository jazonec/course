FROM python:3.11

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY ./__init__.py /app/webconsole
COPY ./database.py /app/webconsole
COPY ./routes.py /app/webconsole
COPY ./static /app/webconsole/static
COPY ./templates /app/webconsole/templates

CMD ["waitress-serve", "webconsole:create_app"]
