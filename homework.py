import os
import time
import logging
import sys

import requests
import telegram
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

PRACTICUM_TOKEN: Optional[str] = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: Optional[str] = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: Optional[str] = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS: dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=logging.StreamHandler(sys.stdout),
)
logger = logging.getLogger(__name__)


def check_tokens() -> None:
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.critical('Не все переменные окружения доступны')
        raise ValueError('Не все переменные окружения доступны')


def send_message(bot, message: str) -> None:
    """Отправляет сообщение в телеграм."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug(f'Сообщение "{message}" успешно отправлено в телеграм')
    except telegram.error.TelegramError as e:
        logger.error(f'Ошибка при отправке сообщения в телеграм: {e}')


def get_api_answer(timestamp: int) -> dict[str, list[dict[str, str]]]:
    """Запрос к API."""
    params: dict[str, int] = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.exceptions.RequestException as e:
        logger.error(f'Ошибка при запросе к API: "{e}"')
        raise Exception(f'Ошибка при запросе к API: "{e}"')
    if response.status_code != 200:
        logger.error(
            f'Ошибка при запросе к API. Код ошибки: "{response.status_code}"'
        )
        raise Exception(
            f'Ошибка при запросе к API. Код ошибки: "{response.status_code}"'
        )
    return response.json()


def check_response(api_answer: dict[str, list[dict[str, str]]]) -> None:
    """Проверяет корректность ответа от API."""
    if not isinstance(api_answer, dict):
        message = 'Ответ от API должен быть словарем.'
        logging.error(message)
        raise TypeError(message)
    if "homeworks" not in api_answer:
        message = 'Отсутствует поле homeworks в ответе API.'
        logging.error(message)
        raise ValueError(message)
    elif not isinstance(api_answer["homeworks"], list):
        message = 'Поле homeworks в ответе API должно быть списком.'
        logging.error(message)
        raise TypeError(message)
    if "current_date" not in api_answer:
        message = 'Отсутствует поле current_date в ответе API.'
        logging.error(message)
        raise ValueError(message)
    elif not isinstance(api_answer["current_date"], int):
        message = 'Поле current_date в ответе API должно быть числом.'
        logging.error(message)
        raise ValueError(message)


def parse_status(homework: dict[str, str]) -> str:
    """Получает статус работы."""
    status = homework.get("status")
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неожиданный статус работы: "{status}"')
    verdict = HOMEWORK_VERDICTS.get(status)
    homework_name = homework.get("homework_name")
    if homework_name is None:
        raise ValueError("В ответе API отсутствует ключ 'homework_name'")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            api_answer = get_api_answer(timestamp)
            if api_answer is None:
                time.sleep(RETRY_PERIOD)
                continue
            check_response(api_answer)
            homeworks = api_answer["homeworks"]
            if homeworks:
                for homework in homeworks:
                    message = parse_status(homework)
                    send_message(bot, message)
            timestamp = api_answer["current_date"]
            time.sleep(RETRY_PERIOD)
        except Exception as e:
            print(f'Возникла непредвиденная ошибка: "{e}"')
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
