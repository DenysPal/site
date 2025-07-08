#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки обох форматів URL
"""
import sqlite3
import requests
import json

def test_both_url_formats():
    """Тестує обидва формати URL"""
    print("=== ТЕСТ ОБОХ ФОРМАТІВ URL ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Отримуємо останній запис
    c.execute('SELECT id, page_code FROM site_users ORDER BY created_at DESC LIMIT 1')
    row = c.fetchone()
    
    if not row:
        print("❌ Немає записів в базі даних")
        return
    
    user_id, page_code = row
    print(f"Тестуємо з page_code: {page_code}")
    
    # Тестуємо новий формат ?page=
    print(f"\n1. Тестуємо новий формат ?page={page_code}")
    try:
        response = requests.get(f'http://127.0.0.1:8081/api/event_links?page={page_code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Успішно: {data}")
        else:
            print(f"  ❌ Помилка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ❌ Помилка запиту: {e}")
    
    # Тестуємо старий формат ?e=
    print(f"\n2. Тестуємо старий формат ?e={page_code}")
    try:
        response = requests.get(f'http://127.0.0.1:8081/api/event_links?e={page_code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Успішно: {data}")
        else:
            print(f"  ❌ Помилка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ❌ Помилка запиту: {e}")
    
    # Тестуємо event_address API
    print(f"\n3. Тестуємо event_address API з ?page={page_code}")
    try:
        response = requests.get(f'http://127.0.0.1:8081/api/event_address?page={page_code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Успішно: {data}")
        else:
            print(f"  ❌ Помилка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ❌ Помилка запиту: {e}")
    
    # Тестуємо event_address API з старим форматом
    print(f"\n4. Тестуємо event_address API з ?e={page_code}")
    try:
        response = requests.get(f'http://127.0.0.1:8081/api/event_address?e={page_code}', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Успішно: {data}")
        else:
            print(f"  ❌ Помилка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"  ❌ Помилка запиту: {e}")
    
    conn.close()

def test_url_generation():
    """Тестує генерацію URL"""
    print("\n=== ТЕСТ ГЕНЕРАЦІЇ URL ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Отримуємо останній запис
    c.execute('SELECT id, page_code FROM site_users ORDER BY created_at DESC LIMIT 1')
    row = c.fetchone()
    
    if row:
        user_id, page_code = row
        print(f"Останній користувач: ID={user_id}, Page Code={page_code}")
        
        # Генеруємо URL в новому форматі
        main_url_new = f"http://artpullse.com/?page={page_code}"
        event_url_new = f"http://artpullse.com/terroir-and-traditions/?page={page_code}"
        
        # Генеруємо URL в старому форматі (для порівняння)
        main_url_old = f"http://artpullse.com/?e={page_code}"
        event_url_old = f"http://artpullse.com/terroir-and-traditions/?e={page_code}&page={page_code}&price=45&currency=EUR"
        
        print(f"\nНовий формат:")
        print(f"  - Головна сторінка: {main_url_new}")
        print(f"  - Сторінка івенту: {event_url_new}")
        
        print(f"\nСтарий формат (для порівняння):")
        print(f"  - Головна сторінка: {main_url_old}")
        print(f"  - Сторінка івенту: {event_url_old}")
        
        print(f"\n✅ Новий формат значно чистіший!")
    
    conn.close()

def main():
    test_both_url_formats()
    test_url_generation()
    print("\n✅ Тестування завершено!")

if __name__ == "__main__":
    main() 