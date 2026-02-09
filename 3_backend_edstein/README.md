# Weather Backend

Бэкенд для погоды города Казань. Данные берём из AccuWeather API.  
Сделано на Python, FastAPI, PostgreSQL, SQLAlchemy. Есть простая веб-страница и Swagger.

---

## Задача проекта

Нужно было сделать REST API для погоды: текущая температура, почасовая за 24 часа, плюс макс/мин/среднее за сутки и поиск по времени. Всё это тянем из AccuWeather. Нагрузка небольшая — до 5 запросов в секунду на эндпоинт.

---

## Как задача решается

- Запросы к AccuWeather идут через бэкенд (клиент в `app/services/accuweather.py`). Ответы кешируем на несколько минут, чтобы не дёргать API лишний раз.
- Текущая погода — либо из эндпоинта «текущие условия», либо, если он не отвечает, подставляем последнее значение из почасовой истории за 24 ч.
- Почасовая история за 24 ч — один эндпоинт AccuWeather (historical/24). По нему считаем макс, мин и среднее.
- На главной странице (веб-интерфейс) все цифры — текущая, макс, мин, среднее и список почасовых — получаем из одного запроса к нашему API: `/weather/historical`. Так надёжнее: один источник данных, всё считается на фронте из одного ответа.

---

## Инструкция для локального запуска

### Что нужно

- Python 3.10 или новее
- Работающий PostgreSQL (порт 5432)
- Ключ AccuWeather (можно взять бесплатно на [developer.accuweather.com](https://developer.accuweather.com/))

### Что делать по шагам

1. Открыть папку проекта в терминале:
   ```bash
   cd 3_backend_Edstein
   ```

2. Создать виртуальное окружение и включить его:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
   На Linux/macOS вместо второй строки: `source .venv/bin/activate`

3. Поставить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. В PostgreSQL создать базу:
   ```sql
   CREATE DATABASE weather_db;
   ```

5. В корне проекта создать файл `.env` и написать в нём:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:ВАШ_ПАРОЛЬ@localhost:5432/weather_db
   ACCUWEATHER_API_KEY=ваш_ключ_от_accuweather
   LOCATION_KEY=295954
   ```
   (295954 — это ключ локации Казани в AccuWeather.)

6. Запустить сервер:
   ```bash
   python run.py
   ```
   Или так:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. В браузере открыть:
   - главную с погодой: http://localhost:8000/
   - документацию API (Swagger): http://localhost:8000/docs

---

## Инструкция для запуска в Docker

### Что нужно

- Установленные Docker и Docker Compose.

### Что делать по шагам

1. В корне проекта создать файл `.env` и указать ключ AccuWeather (базу в Docker поднимать не нужно — она уже в docker-compose):
   ```
   ACCUWEATHER_API_KEY=ваш_ключ
   LOCATION_KEY=295954
   ```
   Строку `DATABASE_URL` можно не писать — в `docker-compose.yml` для приложения уже прописан адрес к PostgreSQL внутри контейнеров.

2. Собрать и запустить контейнеры:
   ```bash
   docker compose up -d
   ```

3. Приложение будет доступно по адресу http://localhost:8000/  
   База PostgreSQL крутится в контейнере `db` в той же сети.

4. Остановить всё:
   ```bash
   docker compose down
   ```

Файлы для Docker лежат в корне: `Dockerfile` и `docker-compose.yml`.

---

## API (кратко)

| Метод | Путь | Что делает |
|-------|------|------------|
| GET | `/health` | Проверка, что бэкенд живой (всегда OK) |
| GET | `/weather/current` | Текущая температура |
| GET | `/weather/historical` | Почасовая температура за последние 24 часа |
| GET | `/weather/historical/max` | Максимум за 24 ч |
| GET | `/weather/historical/min` | Минимум за 24 ч |
| GET | `/weather/historical/avg` | Среднее за 24 ч |
| GET | `/weather/by_time?timestamp=...` | Температура ближайшая к указанному времени (Unix timestamp); если данных нет — 404 |

---

## Проверка кода (стиль)

```bash
flake8 app run.py
isort app run.py --check-only
```

---

## Структура проекта

```
3_backend_Edstein/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── static/
│       └── index.html
├── requirements.txt
├── setup.cfg
├── run.py
├── README.md
├── TASK.md
└── SCREEN.md
```
