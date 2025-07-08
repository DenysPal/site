#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки нової системи page_code
"""
import sqlite3
import json

def test_page_system():
    """Тестує нову систему page_code"""
    print("=== ТЕСТ НОВОЇ СИСТЕМИ PAGE_CODE ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо останні записи
    c.execute('SELECT id, page_code FROM site_users ORDER BY created_at DESC LIMIT 5')
    recent_users = c.fetchall()
    
    print("Останні 5 користувачів:")
    for user_id, page_code in recent_users:
        print(f"  - ID: {user_id}, Page Code: {page_code}")
    
    # Перевіряємо event_links
    c.execute('SELECT event_code, user_id FROM event_links ORDER BY event_code DESC LIMIT 5')
    recent_links = c.fetchall()
    
    print("\nОстанні 5 event_links:")
    for event_code, user_id in recent_links:
        print(f"  - Event Code: {event_code}, User ID: {user_id}")
    
    # Тестуємо пошук по page_code
    print("\nТестуємо пошук по page_code:")
    for user_id, page_code in recent_users[:3]:  # Тестуємо перші 3
        print(f"\nПошук для page_code: {page_code}")
        
        # Шукаємо в event_links
        c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        event_link_result = c.fetchone()
        if event_link_result:
            print(f"  ✅ Знайдено в event_links: {event_link_result[0]}")
        else:
            print(f"  ❌ Не знайдено в event_links")
        
        # Шукаємо в site_users
        c.execute('SELECT id FROM site_users WHERE page_code=?', (page_code,))
        site_user_result = c.fetchone()
        if site_user_result:
            print(f"  ✅ Знайдено в site_users: {site_user_result[0]}")
        else:
            print(f"  ❌ Не знайдено в site_users")
    
    conn.close()

def test_url_generation():
    """Тестує генерацію URL з новою системою"""
    print("\n=== ТЕСТ ГЕНЕРАЦІЇ URL ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Отримуємо останній запис
    c.execute('SELECT id, page_code FROM site_users ORDER BY created_at DESC LIMIT 1')
    row = c.fetchone()
    
    if row:
        user_id, page_code = row
        print(f"Останній користувач: ID={user_id}, Page Code={page_code}")
        
        # Генеруємо URL
        main_url = f"http://artpullse.com/?page={page_code}"
        event_url = f"http://artpullse.com/terroir-and-traditions/?page={page_code}"
        
        print(f"\nЗгенеровані URL:")
        print(f"  - Головна сторінка: {main_url}")
        print(f"  - Сторінка івенту: {event_url}")
        
        # Перевіряємо, чи існує запис в event_links
        c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        event_link = c.fetchone()
        if event_link:
            print(f"  ✅ Запис в event_links існує")
        else:
            print(f"  ⚠️ Запис в event_links відсутній")
    
    conn.close()

def main():
    test_page_system()
    test_url_generation()
    print("\n✅ Тестування завершено!")

if __name__ == "__main__":
    main() 