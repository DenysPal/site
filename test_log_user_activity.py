#!/usr/bin/env python3
"""
Тест функції log_user_activity
"""

import sqlite3
import sys
import os

# Додаємо поточну директорію до шляху для імпорту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_log_user_activity():
    """Тестує функцію log_user_activity"""
    
    print("🧪 Тестування функції log_user_activity...")
    
    try:
        # Імпортуємо функцію
        from main import log_user_activity
        
        print("✅ Функція log_user_activity успішно імпортована")
        
        # Тестові дані
        test_data = {
            "page_code": "1-4",
            "user_ip": "37.52.215.105",
            "page_url": "/buy-tickets/loading/",
            "action_type": "page_view",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "referer": "https://metanoia-gallery.com/"
        }
        
        print(f"📝 Тестові дані: {test_data}")
        
        # Викликаємо функцію
        print("🔄 Викликаю log_user_activity...")
        log_user_activity(**test_data)
        
        print("✅ log_user_activity виконана успішно")
        
        # Перевіряємо, чи зберігся лог в базі
        print("🔍 Перевіряю базу даних...")
        
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM user_activity_logs 
            WHERE page_code = ? AND user_ip = ? 
            ORDER BY id DESC LIMIT 1
        ''', (test_data['page_code'], test_data['user_ip']))
        
        row = c.fetchone()
        if row:
            print(f"✅ Лог знайдено в базі: ID={row[0]}")
            print(f"   page_code: {row[1]}")
            print(f"   user_ip: {row[2]}")
            print(f"   user_country: {row[3]}")
            print(f"   page_name: {row[4]}")
            print(f"   page_url: {row[5]}")
            print(f"   action_type: {row[6]}")
        else:
            print("❌ Лог не знайдено в базі")
        
        conn.close()
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("💡 Переконайтеся, що main.py доступний для імпорту")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        print(f"🔍 Тип помилки: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_log_user_activity()
