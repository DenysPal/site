#!/usr/bin/env python3
import sqlite3

def fix_event_links():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print("=== ВИПРАВЛЕННЯ EVENT_LINKS ===")
    
    # Отримуємо всі записи з event_links
    c.execute('SELECT event_code, user_id FROM event_links')
    records = c.fetchall()
    
    print(f"Знайдено {len(records)} записів:")
    for event_code, user_id in records:
        print(f"  {event_code} -> {user_id}")
    
    # Отримуємо всі site_user_id
    c.execute('SELECT id FROM site_users ORDER BY created_at DESC')
    site_users = [row[0] for row in c.fetchall()]
    
    print(f"\nДоступні site_user_id ({len(site_users)}):")
    for site_user_id in site_users:
        print(f"  {site_user_id}")
    
    # Виправляємо записи
    print("\n=== ВИПРАВЛЕННЯ ===")
    
    # Групуємо записи за user_id (Telegram ID)
    telegram_ids = {}
    for event_code, user_id in records:
        if user_id not in telegram_ids:
            telegram_ids[user_id] = []
        telegram_ids[user_id].append(event_code)
    
    print(f"Знайдено {len(telegram_ids)} унікальних Telegram user_id:")
    for telegram_id, event_codes in telegram_ids.items():
        print(f"  {telegram_id} -> {len(event_codes)} event_codes")
    
    # Видаляємо всі записи з event_links
    c.execute('DELETE FROM event_links')
    print("Видалено всі записи з event_links")
    
    # Створюємо нові записи з правильними site_user_id
    site_user_index = 0
    for telegram_id, event_codes in telegram_ids.items():
        if site_user_index < len(site_users):
            site_user_id = site_users[site_user_index]
            
            for event_code in event_codes:
                c.execute('INSERT INTO event_links (event_code, user_id) VALUES (?, ?)', 
                         (event_code, site_user_id))
                print(f"✅ {event_code} -> {site_user_id}")
            
            site_user_index += 1
        else:
            print(f"❌ Немає більше site_user_id для {telegram_id}")
    
    conn.commit()
    conn.close()
    
    print("\n=== РЕЗУЛЬТАТ ===")
    # Показуємо фінальний стан
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT event_code, user_id FROM event_links')
    final_records = c.fetchall()
    
    for event_code, user_id in final_records:
        print(f"  {event_code} -> {user_id}")
    
    conn.close()

if __name__ == '__main__':
    fix_event_links() 