#!/usr/bin/env python3
import sqlite3

def check_database():
    """Перевіряє стан бази даних і знаходить проблеми"""
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print("=== ПЕРЕВІРКА БАЗИ ДАНИХ ===")
    
    # 1. Перевіряємо event_links
    print("\n1. Таблиця event_links:")
    c.execute('SELECT event_code, user_id FROM event_links')
    event_links = c.fetchall()
    
    for event_code, user_id in event_links:
        print(f"  {event_code} -> {user_id}")
    
    # 2. Перевіряємо site_users
    print("\n2. Таблиця site_users:")
    c.execute('SELECT id, price, currency, street, created_at FROM site_users ORDER BY created_at DESC')
    site_users = c.fetchall()
    
    for site_user_id, price, currency, street, created_at in site_users:
        print(f"  {site_user_id} -> {price} {currency}, {street}, {created_at}")
    
    # 3. Знаходимо проблеми
    print("\n3. ПРОБЛЕМИ:")
    
    # Перевіряємо, чи всі user_id з event_links існують в site_users
    event_links_user_ids = [row[1] for row in event_links]
    site_users_ids = [row[0] for row in site_users]
    
    missing_site_users = []
    for user_id in event_links_user_ids:
        if user_id not in site_users_ids:
            missing_site_users.append(user_id)
    
    if missing_site_users:
        print(f"  ❌ Відсутні site_user_id в таблиці site_users:")
        for missing_id in missing_site_users:
            print(f"    - {missing_id}")
    else:
        print("  ✅ Всі user_id з event_links існують в site_users")
    
    # Перевіряємо, чи всі site_users мають відповідні записи в event_links
    orphaned_site_users = []
    for site_user_id in site_users_ids:
        if site_user_id not in event_links_user_ids:
            orphaned_site_users.append(site_user_id)
    
    if orphaned_site_users:
        print(f"  ⚠️  Site_user_id без відповідних event_links:")
        for orphaned_id in orphaned_site_users:
            print(f"    - {orphaned_id}")
    else:
        print("  ✅ Всі site_user_id мають відповідні event_links")
    
    conn.close()
    
    return missing_site_users, orphaned_site_users

def fix_missing_site_users(missing_ids):
    """Створює відсутні записи в site_users"""
    
    if not missing_ids:
        print("Немає відсутніх site_user_id для створення")
        return
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print(f"\n=== СТВОРЕННЯ ВІДСУТНІХ SITE_USERS ===")
    
    # Беремо дані з останнього існуючого запису
    c.execute('SELECT price, currency, street, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8 FROM site_users ORDER BY created_at DESC LIMIT 1')
    last_record = c.fetchone()
    
    if not last_record:
        print("❌ Немає жодного запису в site_users для копіювання даних")
        return
    
    price, currency, street, *dates = last_record
    
    for missing_id in missing_ids:
        print(f"Створюю запис для {missing_id}...")
        
        c.execute('''INSERT INTO site_users 
                     (id, price, currency, street, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (missing_id, price, currency, street, *dates))
        
        print(f"✅ Створено запис для {missing_id}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    missing_ids, orphaned_ids = check_database()
    
    if missing_ids:
        print(f"\nЗнайдено {len(missing_ids)} відсутніх site_user_id")
        response = input("Створити відсутні записи? (y/n): ")
        if response.lower() == 'y':
            fix_missing_site_users(missing_ids)
            print("\nПісля виправлення:")
            check_database()
    else:
        print("\n✅ База даних у порядку!") 