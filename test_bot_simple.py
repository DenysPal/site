#!/usr/bin/env python3
"""
Простой тест для проверки бота
"""

import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN

async def test_bot():
    try:
        bot = Bot(token=API_TOKEN)
        me = await bot.get_me()
        print(f"Бот успешно подключен: {me.first_name} (@{me.username})")
        await bot.session.close()
        return True
    except Exception as e:
        print(f"Ошибка подключения к боту: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot())
    if success:
        print("✅ Бот работает корректно")
    else:
        print("❌ Проблема с ботом")
