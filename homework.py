import os
import time

import requests
import telegram
from dotenv import load_dotenv
from typing import Dict, Optional

load_dotenv()

PRACTICUM_TOKEN: Optional[str] = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN: Optional[str] = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID: Optional[str] = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD: int = 600
ENDPOINT: str = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS: Dict[str, str] = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS: Dict[str, str] = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> None:
    """Проверяет доступность переменных окружения."""
    if not PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        raise ValueError('Не все переменные окружения доступны')


def send_message(bot, message: str) -> None:
    """Отправляет сообщение в телеграм."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def get_api_answer(timestamp: int) -> Dict[str, list[Dict[str, str]]]:
    """Запрос к API."""
    params: Dict[str, int] = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f'Возникла ошибка при запросе к API: {e}')
        return None
    return response.json()


def check_response(api_answer: Dict[str, list[Dict[str, str]]]) -> None:
    """Проверяет корректность ответа от API."""
    if "homeworks" not in api_answer:
        raise ValueError('Отсутствует поле homeworks в ответе API.')
    elif not isinstance(api_answer["homeworks"], list):
        raise ValueError('Поле homeworks в ответе API должно быть списком.')
    if "current_date" not in api_answer:
        raise ValueError('Отсутствует поле current_date в ответе API.')
    elif not isinstance(api_answer["current_date"], int):
        raise ValueError('Поле current_date в ответе API должно быть числом.')


def parse_status(homework: Dict[str, str]) -> str:
    """Получает статус работы."""
    status = homework["status"]
    homework_name = homework["homework_name"]
    verdict = HOMEWORK_VERDICTS[status]
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
            print(f"Возникла непредвиденная ошибка: {e}")
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
