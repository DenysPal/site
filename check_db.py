
#!/usr/bin/env python3
import sqlite3

def check_database():
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
        
        # Створюємо відсутні записи
        print(f"\n=== СТВОРЕННЯ ВІДСУТНІХ SITE_USERS ===")
        
        if site_users:
            # Беремо дані з останнього запису
            last_record = site_users[0]
            price, currency, street = last_record[1], last_record[2], last_record[3]
            
            # Отримуємо дати
            c.execute('SELECT date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8 FROM site_users ORDER BY created_at DESC LIMIT 1')
            dates = c.fetchone()
            
            for missing_id in missing_site_users:
                print(f"Створюю запис для {missing_id}...")
                
                c.execute('''INSERT INTO site_users 
                             (id, price, currency, street, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8) 
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                          (missing_id, price, currency, street, *dates))
                
                print(f"✅ Створено запис для {missing_id}")
            
            conn.commit()
            print("\n✅ Всі відсутні записи створені!")
        else:
            print("❌ Немає жодного запису в site_users для копіювання даних")
    else:
        print("  ✅ Всі user_id з event_links існують в site_users")
    
    conn.close()

if __name__ == '__main__':
    check_database() 