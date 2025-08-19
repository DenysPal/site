#!/usr/bin/env python3
"""
Простий тест bot
"""

import asyncio
import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_bot_simple():
    """Простий тест bot"""
    
    print("🧪 Простий тест bot...")
    
    try:
        # Імпортуємо bot з main.py
        from main import bot
        
        print("✅ Bot успішно імпортований")
        print(f"🔑 Bot token: {bot.token[:20]}...")
        
        # Тестовий admin_id
        admin_id = 7855499159
        
        # Просте тестове повідомлення
        test_message = "🧪 Тестове повідомлення від bot"
        
        print(f"📤 Відправляю тестове повідомлення адміну {admin_id}...")
        print(f"📝 Повідомлення: {test_message}")
        
        # Відправляємо повідомлення
        result = await bot.send_message(admin_id, test_message)
        
        print(f"✅ Повідомлення успішно відправлено!")
        print(f"📊 Результат: {result}")
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print(f"🔍 Тип помилки: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Запускаємо асинхронну функцію
    asyncio.run(test_bot_simple())
