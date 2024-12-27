# Базовый образ. По умолчанию берется из https://hub.docker.com/_/python
FROM python:3.12-slim

# Поменять рабочую директорию. Если ее нет, создать ее.
WORKDIR /app

# Скопировать из материнской машины в контейнер
COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

# Запустить команду
CMD ["python", "web_app.py"]