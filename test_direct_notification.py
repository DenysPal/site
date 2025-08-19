#!/usr/bin/env python3
"""
Прямий тест функції send_activity_notification_to_admin
"""

import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_notification():
    """Тестує функцію send_activity_notification_to_admin безпосередньо"""
    
    print("🧪 Прямий тест send_activity_notification_to_admin...")
    
    try:
        # Імпортуємо функцію
        from main import send_activity_notification_to_admin
        
        print("✅ Функція send_activity_notification_to_admin успішно імпортована")
        
        # Тестові дані
        test_data = {
            "page_code": "1-4",
            "user_ip": "37.52.215.105",
            "user_country": "UA",
            "page_name": "Ввод карты",
            "page_url": "/buy-tickets/loading/",
            "action_type": "page_view"
        }
        
        print(f"📝 Тестові дані: {test_data}")
        
        # Викликаємо функцію
        print("🔄 Викликаю send_activity_notification_to_admin...")
        send_activity_notification_to_admin(**test_data)
        
        print("✅ send_activity_notification_to_admin виконана успішно")
        print("📱 Перевірте Telegram повідомлення адміну 7855499159")
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("💡 Переконайтеся, що main.py доступний для імпорту")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print(f"🔍 Тип помилки: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_notification()
