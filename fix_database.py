#!/usr/bin/env python3
import sqlite3
import sys

def fix_event_links():
    """Виправляє записи в event_links, де user_id містить event_code замість site_user_id"""
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print("=== Виправлення таблиці event_links ===")
    
    # Отримуємо всі записи з event_links
    c.execute('SELECT event_code, user_id FROM event_links')
    records = c.fetchall()
    
    print(f"Знайдено {len(records)} записів:")
    for event_code, user_id in records:
        print(f"  {event_code} -> {user_id}")
    
    # Перевіряємо, які записи потрібно виправити
    to_fix = []
    for event_code, user_id in records:
        # Якщо user_id має довжину 6 символів (як event_code) або містить цифри на початку
        if len(user_id) == 6 or (len(user_id) > 6 and user_id[:6].isdigit()):
            to_fix.append((event_code, user_id))
    
    if not to_fix:
        print("✅ Всі записи вже правильні!")
        return
    
    print(f"\nПотрібно виправити {len(to_fix)} записів:")
    for event_code, wrong_user_id in to_fix:
        print(f"  {event_code} -> {wrong_user_id} (НЕПРАВИЛЬНИЙ)")
    
    # Отримуємо всі site_user_id з таблиці site_users
    c.execute('SELECT id, price, currency, street, date_1 FROM site_users ORDER BY created_at DESC')
    site_users = c.fetchall()
    
    print(f"\nДоступні site_user_id ({len(site_users)}):")
    for site_user_id, price, currency, street, date_1 in site_users:
        print(f"  {site_user_id} -> {price} {currency}, {street}, {date_1}")
    
    # Виправляємо записи
    print("\n=== Виправлення ===")
    for event_code, wrong_user_id in to_fix:
        # Знаходимо відповідний site_user_id
        # Беремо останній створений (найновіший)
        if site_users:
            correct_site_user_id = site_users[0][0]  # Беремо перший (найновіший)
            
            # Оновлюємо запис
            c.execute('UPDATE event_links SET user_id=? WHERE event_code=?', 
                     (correct_site_user_id, event_code))
            
            print(f"✅ Виправлено: {event_code} -> {correct_site_user_id}")
            
            # Видаляємо використаний site_user_id зі списку
            site_users = site_users[1:]
        else:
            print(f"❌ Немає доступних site_user_id для {event_code}")
    
    conn.commit()
    conn.close()
    
    print("\n=== Результат ===")
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