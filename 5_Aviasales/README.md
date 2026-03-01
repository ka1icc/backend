# Aviasales — поиск перелётов DXB → BKK

Веб-сервис, который парсит XML-ответы от партнёра и отдаёт данные о перелётах через REST API в формате JSON.

## Описание проекта

Есть два XML-файла (`RS_Via-3.xml` и `RS_ViaOW.xml`) — это ответы на поисковые запросы от партнёра. В них лежат варианты перелётов из Дубая (DXB) в Бангкок (BKK).

Задача — на основе этих данных сделать веб-сервис с тремя эндпоинтами:
1. Показать все полученные варианты перелёта
2. Найти самый дорогой/дешёвый, быстрый/долгий и оптимальный вариант
3. Показать отличия между результатами двух запросов


## API

| Метод | URL | Что делает |
|-------|-----|------------|
| GET | `/api/flights` | Все варианты перелёта DXB → BKK |
| GET | `/api/flights/extremes` | Самый дешёвый, дорогой, быстрый, долгий и оптимальный |
| GET | `/api/diff` | Сравнение результатов двух XML (что есть только в одном, что в обоих) |

## Запуск локально

### Что нужно заранее

- Python 3.10+
- PostgreSQL (запущен, есть база `aviasales`)

### Шаги

1. Создать виртуальное окружение и поставить зависимости:

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Задать переменные окружения (PowerShell):

```
$env:PGCLIENTENCODING = "utf8"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "WinSer2016"
$env:POSTGRES_DB = "aviasales"
```

3. Запустить:

```
python run.py
```

4. Открыть в браузере: http://127.0.0.1:5000/api/flights

### Скрипт для быстрого запуска

Windows: `scripts\run_local.bat`

Linux/macOS: `./scripts/run_local.sh`

## Запуск в Docker

Из корня проекта:

```
docker compose up -d --build
```

Поднимутся два контейнера: `db` (PostgreSQL 16) и `web` (Flask-приложение). При старте приложение само создаст таблицу и загрузит данные из XML.

API будет на http://127.0.0.1:5000

Остановить:

```
docker compose down
```

Скрипты: `scripts\deploy_docker.bat` или `./scripts/deploy_docker.sh`

## Структура проекта

```
5_Aviasales/
├── app/
│   ├── __init__.py
│   ├── config.py           — конфигурация (БД, пути)
│   ├── extensions.py       — инициализация SQLAlchemy
│   ├── factory.py          — фабрика приложения Flask
│   ├── models.py           — модель FlightResult (ORM)
│   ├── routes/
│   │   └── flights.py      — три эндпоинта API
│   └── services/
│       └── xml_parser.py   — парсинг XML и загрузка в БД
├── data/
│   ├── RS_Via-3.xml
│   └── RS_ViaOW.xml
├── scripts/
│   ├── run_local.bat / .sh
│   └── deploy_docker.bat / .sh
├── run.py                  — точка входа
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── setup.cfg               — настройки flake8 и isort
├── TASK.md                 — описание задачи и процесс решения
└── SCREEN.md               — скриншоты работающего приложения
```
