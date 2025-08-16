#!/usr/bin/env python3
"""
Дебаг callback'ів
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Налаштування логування
logging.basicConfig(level=logging.DEBUG)

# Тестовий токен (замініть на свій)
API_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=API_TOKEN)
router = Router()
dp = Dispatcher()
dp.include_router(router)

@router.message(Command("start"))
async def start_command(message: types.Message):
    """Команда /start"""
    await message.answer("🚀 Бот запущений! Використовуйте /test для тестування кнопок")

@router.message(Command("test"))
async def test_command(message: types.Message):
    """Тестова команда для перевірки кнопок"""
    print(f"[DEBUG] /test command received from user {message.from_user.id}")
    
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Card", callback_data="card:192.168.1.1"),
                InlineKeyboardButton(text="Block", callback_data="block:192.168.1.1"),
                InlineKeyboardButton(text="Code", callback_data="code:192.168.1.1")
            ],
            [
                InlineKeyboardButton(text="Push", callback_data="push:192.168.1.1:1-91"),
                InlineKeyboardButton(text="Тех поддержка", callback_data="support:192.168.1.1:1-91")
            ]
        ]
    )
    
    await message.answer("🧪 Тестуємо кнопки:", reply_markup=kb)
    print(f"[DEBUG] Test message sent with keyboard")

@router.callback_query(lambda c: True)
async def debug_callback(call: types.CallbackQuery):
    """Дебаг всіх callback'ів"""
    print(f"[DEBUG] ===== CALLBACK RECEIVED =====")
    print(f"[DEBUG] Data: {call.data}")
    print(f"[DEBUG] From user: {call.from_user.id}")
    print(f"[DEBUG] Message: {call.message.text if call.message else 'No message'}")
    print(f"[DEBUG] =============================")
    
    # Простий тест - відповідаємо на всі callback'и
    await call.answer(f"✅ Callback отримано: {call.data}")

async def main():
    print("🚀 Starting debug bot...")
    print("💡 Use /start and /test commands")
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("⚠️  IMPORTANT: Replace API_TOKEN with your actual bot token!")
    asyncio.run(main())
