#!/usr/bin/env python3
"""
Тест для перевірки callback'ів кнопок
"""

import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Тестовий токен (замініть на свій)
API_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=API_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

@router.message(Command("test"))
async def test_command(message: types.Message):
    """Тестова команда для перевірки кнопок"""
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Card", callback_data="card:192.168.1.1"),
                InlineKeyboardButton(text="Block", callback_data="block:192.168.1.1"),
                InlineKeyboardButton(text="Unblock", callback_data="unblock:192.168.1.1"),
                InlineKeyboardButton(text="Code", callback_data="code:192.168.1.1"),
                InlineKeyboardButton(text="Push", callback_data="push:192.168.1.1:1-91")
            ],
            [
                InlineKeyboardButton(text="Тех поддержка", callback_data="support:192.168.1.1:1-91"),
                InlineKeyboardButton(text="Text", callback_data="text:192.168.1.1:1-91")
            ]
        ]
    )
    
    await message.answer("🧪 Тестуємо кнопки:", reply_markup=kb)

@router.callback_query(lambda c: c.data and (
    c.data.startswith('card:') or c.data.startswith('block:') or c.data.startswith('unblock:') or
    c.data.startswith('code:') or c.data.startswith('support:') or c.data.startswith('text:') or
    c.data.startswith('push:')
))
async def test_callback_handler(call: types.CallbackQuery):
    """Тестовий обробник callback'ів"""
    print(f"[TEST] Callback received: {call.data}")
    
    parts = call.data.split(':')
    action = parts[0]
    ip = parts[1] if len(parts) > 1 else None
    page_code = parts[2] if len(parts) > 2 else None
    
    print(f"[TEST] Action: {action}, IP: {ip}, Page Code: {page_code}")
    
    # Прості відповіді для тестування
    if action == 'card':
        await call.answer("✅ Card button works!")
    elif action == 'block':
        await call.answer("✅ Block button works!")
    elif action == 'unblock':
        await call.answer("✅ Unblock button works!")
    elif action == 'code':
        await call.answer("✅ Code button works!")
    elif action == 'push':
        await call.answer("✅ Push button works!")
    elif action == 'support':
        await call.answer("✅ Support button works!")
    elif action == 'text':
        await call.answer("✅ Text button works!")
    
    print(f"[TEST] Callback {action} processed successfully")

async def main():
    print("🚀 Starting test bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Replace API_TOKEN with your actual bot token!")
    print("💡 Use /test command to test buttons")
    asyncio.run(main())
