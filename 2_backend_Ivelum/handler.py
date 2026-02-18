"""
HTTP-обработчик запросов прокси-сервера.

Принимает GET/POST от клиента, запрашивает страницу с Hacker News,
при необходимости модифицирует HTML и отдаёт ответ клиенту.
"""

import urllib.request
from http.server import BaseHTTPRequestHandler

from config import HN_BASE, REQUEST_TIMEOUT
from html_processor import modify_html


class ProxyHandler(BaseHTTPRequestHandler):
    """
    Обработчик HTTP-запросов для прокси Hacker News.

    Проксирует запросы на news.ycombinator.com, модифицирует HTML
    (добавление ™, переписывание URL) и возвращает ответ клиенту.
    """

    def _build_target_url(self) -> str:
        """Собрать целевой URL на HN из path и query строки запроса."""
        query_parts = self.path.split('?', 1)
        path = query_parts[0].lstrip('/')
        query = '?' + query_parts[1] if len(query_parts) > 1 else ''
        if path:
            return f'{HN_BASE}/{path}{query}'
        return f'{HN_BASE}{query}'

    def _send_response_with_content(self, response, content: bytes,
                                    content_type: str) -> None:
        """
        Отправить HTTP-ответ с телом content.

        Копирует заголовки из response, подменяет Content-Length.
        """
        self.send_response(response.status)
        for header, value in response.headers.items():
            if header.lower() not in ('content-length', 'transfer-encoding'):
                self.send_header(header, value)
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _handle_success(self, response) -> None:
        """
        Обработать успешный ответ от HN: прочитать тело, при необходимости
        модифицировать HTML, отправить клиенту.
        """
        content = response.read()
        content_type = response.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            html_text = content.decode('utf-8', errors='ignore')
            modified_content = modify_html(html_text)
            content = modified_content.encode('utf-8')

        self._send_response_with_content(response, content, content_type)

    def _handle_error(self, error: Exception) -> None:
        """Отправить клиенту ответ 500 с текстом ошибки."""
        try:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(error)}'.encode('utf-8'))
        except (ConnectionAbortedError, BrokenPipeError, OSError):
            pass

    def do_GET(self) -> None:
        """
        Обработать GET-запрос: запросить страницу с HN, модифицировать
        при необходимости, вернуть клиенту.
        """
        target_url = self._build_target_url()

        try:
            req = urllib.request.Request(target_url)
            req.add_header('User-Agent', 'Mozilla/5.0')

            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                self._handle_success(resp)
        except (ConnectionAbortedError, BrokenPipeError, OSError):
            pass
        except Exception as e:
            self._handle_error(e)

    def do_POST(self) -> None:
        """
        Обработать POST-запрос (например, отправка форм): передать тело
        и заголовки на HN, модифицировать ответ и вернуть клиенту.
        """
        target_url = self._build_target_url()

        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None

            req = urllib.request.Request(target_url, data=post_data)
            req.add_header('User-Agent', 'Mozilla/5.0')
            for header in ('Content-Type', 'Referer', 'Origin'):
                if header in self.headers:
                    req.add_header(header, self.headers[header])

            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
                self._handle_success(resp)
        except (ConnectionAbortedError, BrokenPipeError, OSError):
            pass
        except Exception as e:
            self._handle_error(e)

    def log_message(self, format, *args) -> None:
        """Отключить стандартное логирование каждого запроса в консоль."""
        pass
