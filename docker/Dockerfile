# Базовый образ Python 3.11 (slim-версия)
FROM python:3.11-slim

# Установить рабочий каталог для приложения
WORKDIR /app

# Установить переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Установить системные зависимости
RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && apt-get clean \
    && rm -rf \
        /tmp/* \
        /var/lib/apt/lists/* \
        /var/cache/apt/* \
        /var/tmp/*

# Установить зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt /app/
RUN pip install -r requirements.txt

# Создать пользователя для запуска приложения и передать права на рабочий каталог
RUN adduser --disabled-password --gecos '' user \
    && chown -R user:user /app

# Переключаем пользователя
USER user

# Запустить сервер
CMD ["/bin/sh"]