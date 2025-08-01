#!/usr/bin/env python3
"""
Скрипт для перевірки даних івентів в базі даних
"""
import sqlite3
import json

def debug_event_data():
    # Підключаємося до бази даних
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print("=== ПЕРЕВІРКА ДАНИХ ІВЕНТІВ ===\n")
    
    # Отримуємо всі записи з site_users
    c.execute('SELECT id, page_code, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price FROM site_users ORDER BY created_at DESC LIMIT 5')
    rows = c.fetchall()
    
    if not rows:
        print("❌ Немає записів в таблиці site_users")
        return
    
    for i, row in enumerate(rows, 1):
        user_id, page_code, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price = row
        
        print(f"📋 ЗАПИС #{i}")
        print(f"   User ID: {user_id}")
        print(f"   Page Code: {page_code}")
        print(f"   Ціна: {price} {currency}")
        print(f"   Адреса: {street}")
        print(f"   Дати/час:")
        
        events = [
            'Terroir and Traditions',
            'Collection Co–selection', 
            'Snucie',
            'Art that saves lives',
            'Gotong Royong',
            'Anna Konik',
            'Uncensored',
            'Jacek Adamas'
        ]
        
        dates = [date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8]
        
        for j, (event_name, date_time) in enumerate(zip(events, dates)):
            print(f"     {j}: {event_name} → {date_time or 'ПУСТО'}")
        
        print()
    
    conn.close()

if __name__ == '__main__':
    debug_event_data()
