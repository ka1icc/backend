"""
Конфигурация прокси-сервера для Hacker News.

Содержит URL целевого сайта, адрес прокси, хост и порт сервера.
Переменные HOST и PORT можно переопределить через переменные окружения
(например, в Docker задать HOST=0.0.0.0).
"""

import os

# Базовый URL Hacker News (целевой сайт для проксирования)
HN_BASE = 'https://news.ycombinator.com'

# Публичный адрес прокси (подставляется в ссылки на страницах)
PROXY_BASE = os.environ.get('PROXY_BASE', 'http://127.0.0.1:8232')

# Хост и порт для запуска HTTP-сервера (в Docker задать HOST=0.0.0.0)
HOST = os.environ.get('HOST', '127.0.0.1')
PORT = int(os.environ.get('PORT', '8232'))

# Таймаут HTTP-запросов к HN (секунды)
REQUEST_TIMEOUT = 10
