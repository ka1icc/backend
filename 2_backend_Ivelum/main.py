#!/usr/bin/env python3
"""
Точка входа: запуск HTTP-прокси для Hacker News.

Прокси слушает на 127.0.0.1:8232, проксирует запросы на news.ycombinator.com,
добавляет ™ после слов из 6 букв и переписывает ссылки на адрес прокси.
"""

from http.server import HTTPServer

from config import HOST, PORT
from handler import ProxyHandler


def run_server() -> None:
    """Запустить прокси-сервер и обслуживать запросы до прерывания."""
    server = HTTPServer((HOST, PORT), ProxyHandler)
    print(f'Proxy server running on http://{HOST}:{PORT}')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        server.shutdown()


if __name__ == '__main__':
    run_server()
