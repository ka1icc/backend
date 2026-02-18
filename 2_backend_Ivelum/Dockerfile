# Прокси-сервер для Hacker News (добавление ™ после слов из 6 букв).
# Сборка: docker build -t hn-proxy .
# Запуск: docker run -d -p 8232:8232 hn-proxy

FROM python:3.12-slim

WORKDIR /app

COPY config.py .
COPY html_processor.py .
COPY handler.py .
COPY main.py .

EXPOSE 8232

# Слушать на всех интерфейсах, чтобы контейнер был доступен с хоста
ENV HOST=0.0.0.0
ENV PORT=8232

CMD ["python", "main.py"]
