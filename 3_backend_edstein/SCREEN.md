# Скриншоты работающего приложения

---

## 1. Главная страница — веб-интерфейс (Погода Казани)


![Погода Казани](screenshots/01-main-page.png)


---

## 2. Документация API (Swagger)


![Swagger](screenshots/02-swagger-docs.png)
![/weather/current](screenshots/02-swagger-docs(2).png)



---

## 3. Ответ эндпоинта /health

![Health](screenshots/03-health.png)

---

## 4. Ответ эндпоинта /weather/current

![Current](screenshots/04-weather-current.png)

---

## 5. Ответ эндпоинта /weather/historical

![Historical](screenshots/05-weather-historical.png)

---

## 6. Эндпоинты max / min / avg

![Max / Min / Avg](screenshots/06-historical-max-min-avg.png)

---

## 7. Эндпоинт /weather/by_time

![By time](screenshots/07-by-time.png)

---

## 8. Запуск тестов

**Команда:** `pytest tests -v`

**Что должно быть на скриншоте:**
- Терминал с результатами прогона тестов (passed/failed), список тестов и общий итог.

![Pytest](screenshots/08-pytest.png)

*Файл: `screenshots/08-pytest.png`*

---

## 9. Локальный запуск приложения

**Команда:** `python run.py` (или `uvicorn app.main:app ...`)

**Что должно быть на скриншоте:**
- Терминал с сообщением о старте Uvicorn (например, «Uvicorn running on http://0.0.0.0:8000» или «Application startup complete»).

![Run](screenshots/09-run.png)

*Файл: `screenshots/09-run.png`*

---
