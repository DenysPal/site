#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест реєстрації команд
"""

import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command

# Створюємо router і dispatcher як у main.py
router = Router()
dp = Dispatcher()

@router.message(Command("test"))
async def test_command(message: types.Message):
    await message.answer("✅ Тестова команда працює!")

@router.message(Command("top_day"))
async def test_top_day(message: types.Message):
    await message.answer("✅ Команда /top_day зареєстрована!")

@router.message(Command("top_month"))
async def test_top_month(message: types.Message):
    await message.answer("✅ Команда /top_month зареєстрована!")

@router.message(Command("top_all"))
async def test_top_all(message: types.Message):
    await message.answer("✅ Команда /top_all зареєстрована!")

# Включаємо router в dispatcher
dp.include_router(router)

async def main():
    print("🧪 Тестуємо реєстрацію команд...")
    
    # Перевіряємо, чи команди зареєстровані
    print(f"📊 Кількість handlers: {len(dp.message.handlers)}")
    
    for i, handler in enumerate(dp.message.handlers):
        print(f"Handler {i+1}: {handler}")
        if hasattr(handler, 'filters'):
            for filter_obj in handler.filters:
                print(f"  Filter: {filter_obj}")
    
    print("✅ Тест завершено!")

if __name__ == "__main__":
    asyncio.run(main())
