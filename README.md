<h2 align="center">Telegram Bot</h2>

Данный Telegram bot обращается в API Яндекс.Практикум, запрашивает актуальный статус проверки домашнего задания и информирует пользователя в чат telegram об обновлении статусов.
Проект реализован на Python 3.8 с использованием API Telegram и API Яндекс.Практикум. Реализовано логгирование событий.

## Установка и использование

### Установка

Клонируйте файлы проекта в локальное хранилище и перейдите в папку с проектом:

`git clone https://github.com/idudnikov/homework_bot.git`

`cd homework_bot`

Создайте и активируйте виртуальное окружение:

`python3 -m venv venv`

`source venv/bin/activate`

Установите зависимости:

`python3 -m pip install --upgrade pip`

`pip install -r requirements.txt`

### Использование

Создайте файл .env и заполните его необходимыми токенами:

`nano .env`

>PRACTICUM_TOKEN=<персональный токен Яндекс.Практикум>br/>
>TELEGRAM_TOKEN=<токен бота><br/>
>TELEGRAM_CHAT_ID=<ID чата пользователя>
