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
ENDPOINT = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Ревьюеру всё понравилось, можно приступать к следующему уроку.',
    'rejected': 'К сожалению в работе нашлись ошибки.',
    'reviewing': 'Работа находится на проверке у ревьюера.',
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        raise ValueError('Не все переменные окружения доступны')


def send_message(bot, message):
    """Отправляет сообщение в телеграм."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp):
    """Запрос к API."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f'Возникла ошибка при запросе к API: {e}')
        return None
    return response.json()


def check_response(api_answer):
    """Проверяет корректность ответа от API."""
    if "homeworks" not in api_answer:
        raise ValueError('Отсутствует поле homeworks в ответе API.')
    elif not isinstance(api_answer["homeworks"], list):
        raise ValueError('Поле homeworks в ответе API должно быть списком.')
    if "current_date" not in api_answer:
        raise ValueError('Отсутствует поле current_date в ответе API.')
    elif not isinstance(api_answer["current_date"], int):
        raise ValueError('Поле current_date в ответе API должно быть числом.')


def parse_status(homework):
    """Получает статус работы."""
    status = homework["status"]
    homework_name = homework["homework_name"]
    verdict = HOMEWORK_VERDICTS[status]
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
