FROM python:3.10

WORKDIR /home/db
WORKDIR /home

ENV TELEGRAM_API_TOKEN=""
ENV TELEGRAM_ACCESS_ID=""


RUN pip install -U pip aiogram pytz && apt-get update && apt-get install sqlite3

COPY *.py ./
COPY createDb.sql ./
COPY aiogram_calendar/ ./
COPY aiogram_calendar/__init__.py aiogram_calendar/
COPY aiogram_calendar/simple_time.py aiogram_calendar/



ENTRYPOINT ["python", "bot.py"]