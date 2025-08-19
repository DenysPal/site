#!/usr/bin/env python3
"""
Скрипт для створення відсутніх page_code в базі даних
"""

import sqlite3

def create_missing_page_codes():
    """Створює відсутні page_code в базі даних"""
    
    print("🔧 Створення відсутніх page_code в базі даних...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Дефолтний адмін для нових page_code
        default_admin_id = 7855499159  # hexwizarsjsjbx
        
        print(f"👤 Використовую дефолтного адміна: {default_admin_id}")
        
        # Отримуємо всі існуючі page_code з event_links
        c.execute('SELECT event_code FROM event_links')
        existing_codes = {row[0] for row in c.fetchall()}
        
        print(f"📋 Існуючі page_code: {len(existing_codes)}")
        
        # Створюємо популярні page_code, які можуть використовуватися
        popular_codes = [
            "2-37", "2-38", "2-39", "2-40", "2-41", "2-42", "2-43", "2-44", "2-45",
            "3-50", "3-51", "3-52", "3-53", "3-54", "3-55", "3-56", "3-57", "3-58",
            "4-60", "4-61", "4-62", "4-63", "4-64", "4-65", "4-66", "4-67", "4-68"
        ]
        
        created_count = 0
        
        for code in popular_codes:
            if code not in existing_codes:
                try:
                    c.execute('INSERT INTO event_links (event_code, user_id) VALUES (?, ?)', 
                             (code, default_admin_id))
                    print(f"✅ Створено: {code} → адмін {default_admin_id}")
                    created_count += 1
                except Exception as e:
                    print(f"❌ Помилка створення {code}: {e}")
        
        conn.commit()
        
        print(f"\n📊 Результат:")
        print(f"   Створено нових page_code: {created_count}")
        print(f"   Загальна кількість: {len(existing_codes) + created_count}")
        
        # Показуємо приклади створених
        if created_count > 0:
            print(f"\n🔍 Приклади створених page_code:")
            c.execute('SELECT event_code, user_id FROM event_links WHERE event_code IN (?, ?, ?)', 
                     ("2-39", "2-40", "3-50"))
            rows = c.fetchall()
            for row in rows:
                print(f"   {row[0]} → user_id: {row[1]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_missing_page_codes()
