#!/usr/bin/env python3


import re
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

HN_BASE = 'https://news.ycombinator.com'
PROXY_BASE = 'http://127.0.0.1:8232'


def add_trademark(text):
    pattern = r'\b([a-zA-Z]{6})\b'
    return re.sub(pattern, r'\1™', text)


def rewrite_urls(content):
    # Step 1: Rewrite absolute HN URLs everywhere
    # This must catch: https://news.ycombinator.com/item?id=123
    content = re.sub(
        r'https?://news\.ycombinator\.com([^\s"\'<>]*)',
        lambda m: PROXY_BASE + (m.group(1) if m.group(1) else ''),
        content
    )
    
    # Step 2: Rewrite relative URLs in href attributes
    # Pattern: href="/item?id=123" or href='/item?id=123'
    def rewrite_href(match):
        quote = match.group(2)
        path = match.group(3)
        # Skip if already rewritten or external URL
        if PROXY_BASE in path or path.startswith('http'):
            return match.group(0)
        return f'href={quote}{PROXY_BASE}{path}{quote}'
    
    content = re.sub(
        r'href=(["\'])(/[^"\']*)\1',
        rewrite_href,
        content
    )
    
    # Step 3: Rewrite other attributes (src, action, etc.)
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


def modify_html(html_content):
    """Modify HTML: add ™ to text and rewrite URLs."""
    script_pattern = r'<script[^>]*>.*?</script>'
    style_pattern = r'<style[^>]*>.*?</style>'
    
    scripts = {}
    styles = {}
    
    for i, match in enumerate(re.finditer(script_pattern, html_content, re.DOTALL | re.IGNORECASE)):
        placeholder = f'__SCRIPT_PLACEHOLDER_{i}__'
        scripts[placeholder] = match.group(0)
        html_content = html_content.replace(match.group(0), placeholder, 1)
    
    for i, match in enumerate(re.finditer(style_pattern, html_content, re.DOTALL | re.IGNORECASE)):
        placeholder = f'__STYLE_PLACEHOLDER_{i}__'
        styles[placeholder] = match.group(0)
        html_content = html_content.replace(match.group(0), placeholder, 1)
    
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
    
    result = []
    for part_type, content in parts:
        if part_type == 'text':
            result.append(add_trademark(content))
        else:
            result.append(content)
    
    modified_html = ''.join(result)
    
    for placeholder, original in scripts.items():
        modified_html = modified_html.replace(placeholder, original)
    for placeholder, original in styles.items():
        modified_html = modified_html.replace(placeholder, original)
    
    modified_html = rewrite_urls(modified_html)
    return modified_html


class ProxyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests."""
        query_string = self.path.split('?', 1)
        path = query_string[0].lstrip('/')
        query = '?' + query_string[1] if len(query_string) > 1 else ''
        
        if path:
            target_url = f'{HN_BASE}/{path}{query}'
        else:
            target_url = f'{HN_BASE}{query}'
        
        try:
            req = urllib.request.Request(target_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                content_type = response.headers.get('Content-Type', '')
                
                if 'text/html' in content_type:
                    html_text = content.decode('utf-8', errors='ignore')
                    modified_content = modify_html(html_text)
                    content = modified_content.encode('utf-8')
                
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ('content-length', 'transfer-encoding'):
                        self.send_header(header, value)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except (ConnectionAbortedError, BrokenPipeError, OSError) as e:
            # Client disconnected, ignore silently
            pass
        except Exception as e:
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode('utf-8'))
            except (ConnectionAbortedError, BrokenPipeError, OSError):
                # Client disconnected during error response, ignore
                pass
    
    def do_POST(self):
        """Handle POST requests."""
        query_string = self.path.split('?', 1)
        path = query_string[0].lstrip('/')
        query = '?' + query_string[1] if len(query_string) > 1 else ''
        
        if path:
            target_url = f'{HN_BASE}/{path}{query}'
        else:
            target_url = f'{HN_BASE}{query}'
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else None
            
            req = urllib.request.Request(target_url, data=post_data)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            # Copy relevant headers
            for header in ['Content-Type', 'Referer', 'Origin']:
                if header in self.headers:
                    req.add_header(header, self.headers[header])
            
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                content_type = response.headers.get('Content-Type', '')
                
                if 'text/html' in content_type:
                    html_text = content.decode('utf-8', errors='ignore')
                    modified_content = modify_html(html_text)
                    content = modified_content.encode('utf-8')
                
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ('content-length', 'transfer-encoding'):
                        self.send_header(header, value)
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except (ConnectionAbortedError, BrokenPipeError, OSError) as e:
            # Client disconnected, ignore silently
            pass
        except Exception as e:
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Error: {str(e)}'.encode('utf-8'))
            except (ConnectionAbortedError, BrokenPipeError, OSError):
                # Client disconnected during error response, ignore
                pass
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 8232), ProxyHandler)
    print('Proxy server running on http://127.0.0.1:8232')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        server.shutdown()
