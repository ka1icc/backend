# Via.com — сравнение маршрутов

Это веб-приложение, которое парсит два XML-ответа API партнёра Via.com и показывает отличия между результатами двух запросов по маршрутам (тег `Flights`).

---

## Задача проекта

Мне нужно было:

- распарсить два XML-файла (`RS_Via-3.xml` и `RS_ViaOW.xml`) — это ответы на запросы к API Via.com;
- вывести **списком** отличия между двумя ответами по маршрутам;
- по каждому маршруту показать: **какие рейсы входят**, **время начала и конца**, **цену**;
- ответить на вопросы: **что изменилось по условиям?** и **добавился ли новый маршрут?**

Реализация: Python 3, веб-интерфейс (FastAPI), база данных PostgreSQL, ORM SQLAlchemy. Стиль кода — PEP8 и wemake-python-styleguide, линтер flake8, сортировка импортов isort.

---

## Структура проекта (декомпозиция)

Код приложения разбит на модули:

| Папка/файл | Назначение |
|------------|------------|
| `app/main.py` | Точка входа FastAPI, создание таблиц БД |
| `app/api.py` | Роуты: главная страница, загрузка XML, JSON API сравнения |
| `app/config.py` | Конфигурация из переменных окружения и `.env` |
| `app/database.py` | Подключение к PostgreSQL, сессии SQLAlchemy |
| `app/models.py` | Модели ORM: XmlResponse, Route, FlightSegment |
| `app/parser.py` | Парсинг XML-ответов Via.com и запись в БД |
| `app/services.py` | Логика сравнения маршрутов (новые, общие, отличия) |
| `templates/index.html` | Шаблон главной страницы (Jinja2 + Bootstrap) |

Данные для парсинга: `RS_Via-3.xml`, `RS_ViaOW.xml` в корне проекта. Docker: `Dockerfile`, `docker-compose.yml`, скрипты `deploy.bat` / `deploy.sh`.

---

## Инструкция для локального запуска


### Что нужно заранее

- **Python 3.10+** (у меня 3.12).
- **PostgreSQL** — установленный и запущенный. Базу создала вручную одной командой в psql: `CREATE DATABASE via_compare;`

### Шаги

1. **Открыть папку проекта** в терминале (PowerShell или командная строка):
   ```powershell
   cd C:\Users\yulia\Desktop\4_KosyanMedia
   ```

2. **Создать виртуальное окружение** (если ещё нет папки `venv`):
   ```powershell
   python -m venv venv
   ```

3. **Активировать его и поставить зависимости:**
   ```powershell
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Файл `.env`** — в корне проекта создать файл `.env` (см. `.env.example`). Вариант с отдельными переменными (удобно на Windows):
   ```
   PGHOST=127.0.0.1
   PGUSER=postgres
   PGPASSWORD=ваш_пароль
   PGPORT=5432
   PGDATABASE=via_compare
   XML_DIR=.
   ```

5. **Запуск приложения:**
   ```powershell
   uvicorn app.main:app --reload
   ```
   Если порт 8000 занят: `uvicorn app.main:app --reload --port 8001`

6. **В браузере** открыть [http://localhost:8000](http://localhost:8000) (или 8001). На главной нажать **«Загрузить XML-данные»** — появятся результаты сравнения маршрутов.

---

## Инструкция для запуска в Docker

Если Docker у вас установлен и работает, можно поднять и базу, и приложение одной командой.

### Что нужно

- Установленный [Docker Desktop](https://www.docker.com/products/docker-desktop/) (или Docker Engine).

### Автоматический запуск

В папке проекта есть скрипты:

- **Windows:** запустить `deploy.bat`
- **Linux / macOS:** в терминале выполнить `chmod +x deploy.sh` и затем `./deploy.sh`

Скрипт соберёт образы, поднимет контейнеры (PostgreSQL + веб-приложение) и выведет адрес. Обычно это [http://localhost:8000](http://localhost:8000).

### Ручной запуск

В терминале в папке проекта:

```powershell
docker compose up --build -d
```

Подождать несколько секунд, затем открыть в браузере [http://localhost:8000](http://localhost:8000) и нажать «Загрузить XML-данные».

Остановить всё:

```powershell
docker compose down
```

Чтобы ещё и удалить данные из БД: `docker compose down -v`.

