import os
import time
import requests
import telegram
from dotenv import load_dotenv


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_VERDICTS = {
    "approved": "Ревьюеру всё понравилось, можно приступать к следующему уроку.",
    "rejected": "К сожалению в работе нашлись ошибки.",
    "reviewing": "Работа находится на проверке у ревьюера.",
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        raise ValueError("Не все переменные окружения доступны")


def send_message(bot, message):
    """Отправляет сообщение в телеграм."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp):
    ...


def check_response(response):
    ...


def parse_status(homework):
    ...

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    ...

    while True:
        try:

            ...

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            ...
        ...


if __name__ == '__main__':
    main()