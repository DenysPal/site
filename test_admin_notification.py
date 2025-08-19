#!/usr/bin/env python3
"""
Тест функції send_activity_notification_to_admin
"""

import sqlite3
import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_notification():
    """Тестує функцію send_activity_notification_to_admin"""
    
    print("🧪 Тестування функції send_activity_notification_to_admin...")
    
    # Підключаємося до бази даних
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        print("✅ Підключення до бази даних успішне")
    except Exception as e:
        print(f"❌ Помилка підключення до бази даних: {e}")
        return
    
    # Тестуємо пошук admin_id для різних page_code
    test_cases = [
        ("1-4", "Тестовий page_code з event_links"),
        ("1-5", "Тестовий page_code з event_links"),
        ("1-6", "Тестовий page_code з event_links"),
        ("2-37", "Неіснуючий page_code"),
        ("", "Порожній page_code")
    ]
    
    for page_code, description in test_cases:
        print(f"\n📋 Тест: {description}")
        print(f"   page_code: '{page_code}'")
        
        try:
            # Спочатку шукаємо в event_links
            c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
            row = c.fetchone()
            
            if row:
                admin_id = row[0]
                print(f"   ✅ Знайдено в event_links: user_id = {admin_id}")
            else:
                print(f"   ❌ Не знайдено в event_links")
                
                # Якщо не знайдено в event_links, шукаємо в site_users
                c.execute('SELECT tg_id FROM site_users WHERE page_code=?', (page_code,))
                row = c.fetchone()
                
                if row:
                    admin_id = row[0]
                    print(f"   ✅ Знайдено в site_users: tg_id = {admin_id}")
                else:
                    print(f"   ❌ Не знайдено в site_users")
                    continue
            
            # Перевіряємо, чи є цей user_id в таблиці users
            if admin_id:
                c.execute('SELECT user_id, username FROM users WHERE user_id=?', (admin_id,))
                user_row = c.fetchone()
                if user_row:
                    print(f"   👤 Користувач знайдений: ID={user_row[0]}, username={user_row[1]}")
                else:
                    print(f"   ⚠️ Користувач не знайдений в таблиці users")
            
        except Exception as e:
            print(f"   ❌ Помилка пошуку: {e}")
    
    # Показуємо статистику
    print(f"\n📊 Статистика бази даних:")
    
    c.execute('SELECT COUNT(*) FROM event_links')
    event_links_count = c.fetchone()[0]
    print(f"   event_links: {event_links_count} записів")
    
    c.execute('SELECT COUNT(*) FROM site_users')
    site_users_count = c.fetchone()[0]
    print(f"   site_users: {site_users_count} записів")
    
    c.execute('SELECT COUNT(*) FROM users')
    users_count = c.fetchone()[0]
    print(f"   users: {users_count} записів")
    
    # Показуємо приклади page_code
    print(f"\n🔍 Приклади page_code з event_links:")
    c.execute('SELECT event_code, user_id FROM event_links LIMIT 5')
    rows = c.fetchall()
    for row in rows:
        print(f"   {row[0]} → user_id: {row[1]}")
    
    conn.close()
    print(f"\n✅ Тест завершено")

if __name__ == "__main__":
    test_admin_notification()
