import logging
import asyncio
import sqlite3
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
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
#API_TOKEN = "8055265032:AAHdP7_hwpJ--mzXYBQgbrJduxJ-uczEPGQ"
API_TOKEN = "5619487724:AAFeBptlX1aJ9IEAFLMUXN3JZBImJ35quWk"
ADMIN_GROUP_ID = -828011200
ADMIN_IDS = {7973971109}

logging.basicConfig(level=logging.INFO)
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
    keyboard=[[KeyboardButton(text="🚫 Заблокировать / разблокировать")], [KeyboardButton(text="💸 Начислить выплату")], [KeyboardButton(text="⬅️ Назад")]], resize_keyboard=True
)

# --- Анкета ---
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    db_user = get_user(uid)
    if db_user:
        if db_user['status'] == 'pending':
            await message.answer("Ваша заявка уже отправлена, ожидайте проверки.")
            return
        elif db_user['status'] == 'approved':
            kb = admin_menu_kb if is_admin(uid) else main_menu_kb
            await message.answer("Ваша заявка одобрена!\nДля продолжения работы используйте меню ниже:", reply_markup=kb)
            return
        elif db_user['status'] == 'rejected':
            if db_user['last_submit']:
                last = datetime.fromisoformat(db_user['last_submit'])
                if datetime.utcnow() - last < timedelta(days=7):
                    next_time = last + timedelta(days=7)
                    await message.answer(f"Ваша заявка была отклонена. Повторно подать заявку можно {next_time.strftime('%d.%m.%Y %H:%M')}")
                    return
    user_data[uid] = {}
    user_step[uid] = 'source'
    await message.answer("📢 Откуда о нас узнали?", reply_markup=source_kb)

@router.message(lambda m: m.text and (m.text.lower() == 'отмена' or m.text.lower() == '❌ отмена'))
async def cancel_any_action(message: types.Message):
    uid = message.from_user.id
    user_step[uid] = None
    user_data[uid] = {}
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)

@router.message(lambda m: user_step.get(m.from_user.id) == 'source')
async def process_source(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    if message.text not in ["Реклама", "От друга"]:
        await message.answer("📢 Откуда о нас узнали?", reply_markup=source_kb)
        return
    user_data[uid]['source'] = message.text
    if message.text == "От друга":
        user_step[uid] = 'invited_by'
        await message.answer("👤 Кто пригласил? (tag или username)", reply_markup=ReplyKeyboardRemove())
    else:
        user_step[uid] = 'experience'
        await message.answer("💼 Укажите опыт работы\n⏰ Сколько времени готовы уделять?", reply_markup=ReplyKeyboardRemove())

@router.message(lambda m: user_step.get(m.from_user.id) == 'invited_by')
async def process_invited_by(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    user_data[uid]['invited_by'] = message.text
    user_step[uid] = 'experience'
    await message.answer("💼 Укажите опыт работы\n⏰ Сколько времени готовы уделять?", reply_markup=ReplyKeyboardRemove())

@router.message(lambda m: user_step.get(m.from_user.id) == 'experience')
async def process_experience(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    user_data[uid]['experience'] = message.text
    user_data[uid]['screenshots'] = []
    user_step[uid] = 'screenshots'
    await message.answer("🖼 Отправьте скриншоты ваших профитов (до 3х)\nМожно пропустить", reply_markup=skip_kb)

@router.message(lambda m: user_step.get(m.from_user.id) == 'screenshots' and m.text and m.text.strip().lower() == "пропустить")
async def skip_screenshots(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    await finish_form(message)

@router.message(lambda m: m.content_type == types.ContentType.PHOTO)
async def process_screenshots(message: types.Message):
    uid = message.from_user.id
    if user_step.get(uid) != 'screenshots':
        return
    user_data[uid]['screenshots'].append(message.photo[-1].file_id)
    if len(user_data[uid]['screenshots']) >= 3:
        await finish_form(message)
    else:
        await message.answer(f"Скриншот {len(user_data[uid]['screenshots'])} принят. Можете отправить еще или нажмите 'Пропустить'.", reply_markup=skip_kb)

@router.message(lambda m: user_step.get(m.from_user.id) == 'screenshots')
async def process_other(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    # Якщо користувач натиснув "Пропустить" (будь-який регістр/пробіли), не обробляємо тут
    if message.text and message.text.strip().lower() == "пропустить":
        return
    await message.answer("Пожалуйста, отправьте скриншот(ы) или нажмите 'Пропустить'.", reply_markup=skip_kb)

async def finish_form(message):
    uid = message.from_user.id
    username = message.from_user.username or "-"
    data = user_data[uid]
    text = f"Новая анкета!\n\nID: <code>{uid}</code>\nUsername: @{username}\nИсточник: {data.get('source')}\n"
    if data.get('source') == "От друга":
        text += f"Кто пригласил: {data.get('invited_by')}\n"
    text += f"Опыт: {data.get('experience')}\n"
    if data['screenshots']:
        text += f"Скриншоты: {len(data['screenshots'])} шт.\n"
    else:
        text += f"Скриншоты: не предоставлены\n"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Принять", callback_data=f"approve_{uid}"),
            InlineKeyboardButton(text="Отклонить", callback_data=f"reject_{uid}")
        ]]
    )
    await bot.send_message(ADMIN_GROUP_ID, text, parse_mode='HTML', reply_markup=kb)
    for ph in data['screenshots']:
        await bot.send_photo(ADMIN_GROUP_ID, ph)
    await message.answer("Ваша анкета проверяется администрацией!\nОжидайте решение", reply_markup=ReplyKeyboardRemove())
    save_user(uid, 'pending', username, data.get('source'), data.get('invited_by'), data.get('experience'), data.get('screenshots', []), data)
    user_step[uid] = None

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
    await message.answer(text, reply_markup=profile_inline_kb, parse_mode='HTML')
    user_step[uid] = None

@router.callback_query(lambda c: c.data == "change_nickname")
async def change_nickname_start(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = 'change_nickname'
    await call.message.answer("Введите новый псевдоним:")
    await call.answer()

@router.message(lambda m: user_step.get(m.from_user.id) == 'change_nickname')
async def change_nickname_save(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
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
    user_step[uid] = None
    await message.answer(f"Псевдоним изменён на: <b>{new_nick}</b>", parse_mode='HTML', reply_markup=main_menu_kb)

@router.callback_query(lambda c: c.data == "change_wallet")
async def change_wallet_start(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = 'change_wallet'
    await call.message.answer("Введите ваш USDT BEP-20 кошелек:")
    await call.answer()

@router.message(lambda m: user_step.get(m.from_user.id) == 'change_wallet')
async def change_wallet_save(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    new_wallet = message.text.strip()
    db_user = get_user(uid)
    form_json = db_user['form_json'] if db_user else {}
    form_json['wallet'] = new_wallet
    c = conn.cursor()
    c.execute('UPDATE users SET form_json=? WHERE user_id=?', (json.dumps(form_json), uid))
    conn.commit()
    user_step[uid] = None
    await message.answer(f"Кошелек сохранён: <code>{new_wallet}</code>", parse_mode='HTML', reply_markup=main_menu_kb)

# --- Админка ---
@router.message(lambda m: m.text == "🛠️ Админ панель" and is_admin(m.from_user.id))
async def admin_panel(message: types.Message):
    await message.answer("Админ-панель. Выберите действие:", reply_markup=admin_panel_kb)
    user_step[message.from_user.id] = 'admin_panel'

@router.message(lambda m: user_step.get(m.from_user.id) == 'admin_panel')
async def admin_panel_action(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    if message.text == "⬅️ Назад":
        kb = admin_menu_kb
        await message.answer("Возврат в главное меню.", reply_markup=kb)
        user_step[uid] = None
        return
    elif message.text == "🚫 Заблокировать / разблокировать":
        user_step[uid] = 'ban_unban_user'
        await message.answer("Введите username пользователя для блокировки/разблокировки (без @):", reply_markup=ReplyKeyboardRemove())
    elif message.text == "💸 Начислить выплату":
        user_step[uid] = 'pay_user'
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="payuser_back")]
            ]
        )
        await message.answer("Введите псевдоним пользователя:", reply_markup=kb)
    else:
        await message.answer("Неизвестная команда.")

@router.callback_query(lambda c: c.data == "payuser_back")
async def payuser_back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = 'admin_panel'
    await call.message.answer("Возврат в админ-панель.", reply_markup=admin_panel_kb)
    await call.answer()

# --- Выплаты ---
@router.message(lambda m: user_step.get(m.from_user.id) == 'pay_user')
async def admin_pay_user_profile(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
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
    user_data[uid] = {'pay_target': target_id, 'pay_username': nick}
    await message.answer(text, parse_mode='HTML', reply_markup=admin_pay_kb(nick))
    user_step[uid] = 'pay_user_profile'

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
async def admin_pay_amount(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
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
    user_step[uid] = 'admin_panel'
    await call.message.answer("Возврат в админ-панель.", reply_markup=admin_panel_kb)
    await call.answer()

# --- Блокировка/разблокировка пользователей ---
@router.message(lambda m: user_step.get(m.from_user.id) == 'ban_unban_user')
async def ban_unban_username(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
        return
    uid = message.from_user.id
    username = message.text.strip().lstrip('@')
    c = conn.cursor()
    c.execute('SELECT user_id, form_json FROM users WHERE LOWER(username)=?', (username.lower(),))
    row = c.fetchone()
    if not row:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="ban_back")]
            ]
        )
        await message.answer("Пользователь с таким username не найден. Введите корректный username или нажмите кнопку ниже.", reply_markup=kb)
        return
    target_id, form_json = row
    form_json = json.loads(form_json) if form_json else {}
    reason = form_json.get('ban_reason', 'Не указана') if form_json.get('banned', False) else ''
    text = f"Пользователь найден.\nСтатус: {'<b>Забанен</b>' if form_json.get('banned', False) else '<b>Не забанен</b>'}"
    if form_json.get('banned', False):
        text += f"\nПричина: <b>{reason}</b>"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Забанить", callback_data=f"ban:{target_id}"),
             InlineKeyboardButton(text="Разбанить", callback_data=f"unban:{target_id}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="ban_back")]
        ]
    )
    await message.answer(text, parse_mode='HTML', reply_markup=kb)
    user_data[uid] = {'ban_target': target_id}
    user_step[uid] = 'ban_wait_action'

@router.callback_query(lambda c: c.data.startswith('ban:'))
async def ban_reason_ask(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = int(call.data.split(':', 1)[1])
    user_data[uid] = {'ban_target': target_id}
    user_step[uid] = 'ban_reason'
    await call.message.answer("Введите причину блокировки:")
    await call.answer()

@router.message(lambda m: user_step.get(m.from_user.id) == 'ban_reason')
async def ban_save(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
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

@router.callback_query(lambda c: c.data.startswith('unban:'))
async def unban_user(call: types.CallbackQuery):
    uid = call.from_user.id
    target_id = int(call.data.split(':', 1)[1])
    db_user = get_user(target_id)
    form_json = db_user['form_json'] if db_user else {}
    form_json['banned'] = False
    form_json['ban_reason'] = ''
    c = conn.cursor()
    c.execute('UPDATE users SET form_json=? WHERE user_id=?', (json.dumps(form_json), target_id))
    conn.commit()
    await call.message.answer("Пользователь разблокирован.", reply_markup=admin_panel_kb)
    user_step[uid] = 'admin_panel'
    await call.answer()

@router.callback_query(lambda c: c.data == "ban_back")
async def ban_back_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = 'admin_panel'
    await call.message.answer("Возврат в админ-панель.", reply_markup=admin_panel_kb)
    await call.answer()

# --- Билеты ---
@router.message(lambda m: m.text == "🎫Билеты")
async def tickets_message(message: types.Message):
    uid = message.from_user.id
    # Спочатку видаляємо клавіатуру через не-порожнє повідомлення
    await message.answer("Введіть дані для квитка:", reply_markup=ReplyKeyboardRemove())
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
    user_step[uid] = 'ticket_input'

TICKETS_DIR = 'tickets'
os.makedirs(TICKETS_DIR, exist_ok=True)

@router.message(lambda m: user_step.get(m.from_user.id) == 'ticket_input')
async def ticket_input_handler(message: types.Message):
    uid = message.from_user.id
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
    user_step[uid] = None

@router.callback_query(lambda c: c.data == "tickets_cancel")
async def tickets_cancel_handler(call: types.CallbackQuery):
    uid = call.from_user.id
    user_step[uid] = None
    user_data[uid] = {}
    kb = admin_menu_kb if is_admin(uid) else main_menu_kb
    await call.message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
    await call.answer()

# --- Хендлер для кнопки "Ссылки" ---
links_template_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Шаблон заполнения 📎")],
        [KeyboardButton(text="❌ Отмена")]
    ],
    resize_keyboard=True
)

@router.message(lambda m: m.text and 'ссылки' in m.text.lower())
async def handle_links_button(message: types.Message):
    print("handle_links_button called")
    text = (
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
    await message.answer(text, reply_markup=links_template_kb)
    user_step[message.chat.id] = 'event_all_fields'

@router.message(lambda m: user_step.get(m.from_user.id) == 'event_all_fields' and m.text and 'шаблон' in m.text.lower())
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

@router.message(lambda m: user_step.get(m.from_user.id) == 'event_all_fields')
async def event_all_fields_handler(message: types.Message):
    if message.text and (message.text.lower() == 'отмена' or message.text.lower() == '❌ отмена'):
        uid = message.from_user.id
        user_step[uid] = None
        user_data[uid] = {}
        kb = admin_menu_kb if is_admin(uid) else main_menu_kb
        await message.answer('Дія скасована. Ви повернуті у головне меню.', reply_markup=kb)
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

@router.message(lambda m: user_step.get(m.from_user.id) == 'links_template_wait' and m.text and 'отмена' in m.text.lower())
async def cancel_links_template(message: types.Message):
    await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
    user_step[message.chat.id] = None

# --- Універсальний хендлер (має бути нижче!) ---
@router.message()
async def block_others(message: types.Message):
    # Ігноруємо всі кроки сценарію івентів та всі варіанти кнопки 'Ссылки'
    if message.text and 'ссылки' in message.text.lower():
        return
    if user_step.get(message.from_user.id) in ['event_title', 'event_dates', 'event_times', 'event_all_fields']:
        return
    uid = message.from_user.id
    db_user = get_user(uid)
    if db_user and db_user['form_json'].get('banned', False):
        for chat_id in [ADMIN_GROUP_ID]:
            try:
                await bot.ban_chat_member(chat_id, uid)
            except Exception:
                pass
        return
    if message.text in ["⚙️Меню", "📎Ссылки", "🎫Билеты", "Добавить/Изменить кошелек", "Сменить псевдоним"]:
        return
    if message.text and message.text == '/start':
        return
    if is_admin(uid):
        if message.text in ["🛠️ Админ панель", "🚫 Заблокировать / разблокировать", "💸 Начислить выплату", "⬅️ Назад"]:
            return
        if user_step.get(uid) in ['admin_panel', 'ban_unban_user', 'pay_user', 'pay_user_profile', 'pay_amount']:
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
    event_id = str(uuid.uuid4())
    events_file = os.path.join('events-art.com', 'events.json')
    # Завантажуємо існуючі події
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except Exception:
        events = {}
    # Додаємо нову подію
    user_event = EVENT_user_data[chat_id]
    events[event_id] = {
        'title': user_event.get('title', 'Выставка'),
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
    # Формуємо повідомлення з посиланнями
    msg = f"Выставка успешно создана:\n<b>{user_event.get('title', 'Выставка')}</b>\nАфиша:\n"
    msg += f"<b>Главная страница:</b> http://{EVENT_DOMAIN}/\n"
    for idx, ev in enumerate(events[event_id]['events'], 1):
        link = f"http://{EVENT_DOMAIN}/{ev['path']}?event={event_id}&item={idx}"
        msg += f"{idx}. {ev['name']} ({ev['date']} {ev['time']})\n{link}\n"
    await message.answer(msg, parse_mode='HTML')
    # Повертаємо меню після створення виставки
    kb = admin_menu_kb if is_admin(message.from_user.id) else main_menu_kb
    await message.answer("Головне меню:", reply_markup=kb)

if __name__ == '__main__':
    async def main():
        await dp.start_polling(bot)
    asyncio.run(main()) 