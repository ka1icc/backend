"""
Обработка HTML-контента: модификация текста и переписывание URL.

Модуль добавляет символ ™ после слов из 6 букв и переписывает ссылки на HN
на адрес прокси, чтобы навигация оставалась через прокси.
"""

import re

from config import PROXY_BASE


def add_trademark(text: str) -> str:
    """
    Добавить ™ после каждого слова из ровно 6 букв.

    Обрабатываются только слова из латинских букв (a-zA-Z).
    Границы слов задаются через \\b.

    Args:
        text: Исходная строка.

    Returns:
        Строка с добавленным ™ после 6-буквенных слов.
    """
    pattern = r'\b([a-zA-Z]{6})\b'
    return re.sub(pattern, r'\1™', text)


def rewrite_urls(content: str) -> str:
    """
    Переписать все URL Hacker News на адрес прокси.

    Обрабатываются:
    - абсолютные URL (https://news.ycombinator.com/...);
    - относительные пути в атрибутах href, src, action и др.

    Внешние ссылки (не на HN) не изменяются.

    Args:
        content: HTML-контент (или любой текст с URL).

    Returns:
        Контент с переписанными URL на PROXY_BASE.
    """
    # Абсолютные URL HN
    content = re.sub(
        r'https?://news\.ycombinator\.com([^\s"\'<>]*)',
        lambda m: PROXY_BASE + (m.group(1) if m.group(1) else ''),
        content
    )

    # Относительные URL в href
    def rewrite_href(match):
        quote = match.group(2)
        path = match.group(3)
        if PROXY_BASE in path or path.startswith('http'):
            return match.group(0)
        return f'href={quote}{PROXY_BASE}{path}{quote}'

    content = re.sub(
        r'href=(["\'])(/[^"\']*)\1',
        rewrite_href,
        content
    )

    # Остальные атрибуты с путями (src, action, formaction и т.д.)
    def rewrite_other_attr(match):
        attr_name = match.group(1)
        quote = match.group(2)
        path = match.group(3)
        if PROXY_BASE in path or path.startswith('http'):
            return match.group(0)
        return f'{attr_name}={quote}{PROXY_BASE}{path}{quote}'

    content = re.sub(
        r'(src|action|data-href|data-url|formaction)=(["\'])(/[^"\']*)\2',
        rewrite_other_attr,
        content
    )

    return content


def modify_html(html_content: str) -> str:
    """
    Модифицировать HTML: добавить ™ к тексту и переписать URL.

    Содержимое <script> и <style> не изменяется, чтобы не сломать
    работу страницы. Обрабатывается только текстовое содержимое
    между тегами.

    Args:
        html_content: Исходный HTML-документ.

    Returns:
        Модифицированный HTML (™ в тексте, URL переписаны на прокси).
    """
    script_pattern = r'<script[^>]*>.*?</script>'
    style_pattern = r'<style[^>]*>.*?</style>'
    scripts = {}
    styles = {}

    # Временно убираем скрипты и стили из обработки
    for i, match in enumerate(re.finditer(script_pattern, html_content,
                                           re.DOTALL | re.IGNORECASE)):
        placeholder = f'__SCRIPT_PLACEHOLDER_{i}__'
        scripts[placeholder] = match.group(0)
        html_content = html_content.replace(match.group(0), placeholder, 1)

    for i, match in enumerate(re.finditer(style_pattern, html_content,
                                           re.DOTALL | re.IGNORECASE)):
        placeholder = f'__STYLE_PLACEHOLDER_{i}__'
        styles[placeholder] = match.group(0)
        html_content = html_content.replace(match.group(0), placeholder, 1)

    # Разбиваем на теги и текст
    parts = []
    last_pos = 0
    tag_pattern = r'<[^>]+>'

    for match in re.finditer(tag_pattern, html_content):
        text_before = html_content[last_pos:match.start()]
        if text_before:
            parts.append(('text', text_before))
        parts.append(('tag', match.group(0)))
        last_pos = match.end()

    if last_pos < len(html_content):
        parts.append(('text', html_content[last_pos:]))

    # Модифицируем только текст
    result = []
    for part_type, content in parts:
        if part_type == 'text':
            result.append(add_trademark(content))
        else:
            result.append(content)

    modified_html = ''.join(result)

    # Возвращаем скрипты и стили на место
    for placeholder, original in scripts.items():
        modified_html = modified_html.replace(placeholder, original)
    for placeholder, original in styles.items():
        modified_html = modified_html.replace(placeholder, original)

    modified_html = rewrite_urls(modified_html)
    return modified_html
