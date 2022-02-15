import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = "https://practicum.yandex.ru/api/user_api/homework_statuses/"
HEADERS = {"Authorization": f"OAuth {PRACTICUM_TOKEN}"}

HOMEWORK_STATUSES = {
    "approved": "Работа проверена: ревьюеру всё понравилось. Ура!",
    "reviewing": "Работа взята на проверку ревьюером.",
    "rejected": "Работа проверена: у ревьюера есть замечания.",
}

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)


class TGBotError(Exception):
    """Кастомный класс для исключений с логированием уровня "error"."""

    pass


class TGBotInfo(Exception):
    """Кастомный класс для исключений с логированием уровня "info"."""

    pass


def send_message(bot, message):
    """Функция отправки сообщения в чат с пользователем."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f'Бот отправил сообщение: "{message}"')
    except telegram.TelegramError as error:
        logger.error(f'Ошибка отправки сообщения "{error}"')


def get_api_answer(current_timestamp):
    """Функция, делающая запрос к API и передающая ответ."""
    timestamp = current_timestamp or int(time.time())
    params = {"from_date": timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except requests.RequestException:
        print("Не удалось отправить запрос к эндпоинту")
    else:
        if response.status_code != HTTPStatus.OK:
            raise TGBotError(
                f"Эндпоинт {ENDPOINT} недоступен."
                f"Код ответа {response.status_code}."
            )
        return response.json()


def check_response(response):
    """Функция, проверяющая и распаковывающая ответ."""
    if not response:
        raise TGBotError("Отсутствие ожидаемых ключей в ответе API")
    if isinstance(response, list):
        homework = response[0].get("homeworks")
    else:
        homework = response.get("homeworks")
    if not homework:
        raise TGBotInfo("Отсутствие в ответе новых статусов")
    if not isinstance(homework, list):
        raise TGBotError('Данные под ключом "homeworks" не в виде списка')
    return parse_status(homework)


def parse_status(homework):
    """Функция, получающая данные из распакованного ответа."""
    if isinstance(homework, str):
        raise KeyError("Некорректный формат данных")
    if isinstance(homework, list):
        homework = homework[0]
    homework_name = homework.get("homework_name")
    homework_status = homework.get("status")
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция, проверяющая наличие необходимых токенов и переменных."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    logger.critical(
        "Отсутствие обязательных переменных окружения во время запуска бота"
    )
    return False


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        sys.exit()

    while True:
        try:
            response = get_api_answer(current_timestamp)
            message = check_response(response)
            if message:
                send_message(bot, message)
        except TGBotError as error:
            logger.error(error)
            message = f"Сбой в работе программы: {error}"
            send_message(bot, message)
        except TGBotInfo as error:
            logger.info(error)
        except Exception as error:
            logger.exception(error)
            message = f"Сбой в работе программы: {error}"
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
