#!/usr/bin/env python3
"""
Тест виправлення головної сторінки
"""

import sqlite3
import requests
import json

def test_main_page_fix():
    """Тестує виправлення головної сторінки"""
    
    print("=== Тест виправлення головної сторінки ===")
    
    # Підключаємося до бази даних
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Отримуємо всі event_id з таблиці site_users
        c.execute('SELECT id, page_code FROM site_users ORDER BY id DESC LIMIT 5')
        rows = c.fetchall()
        
        if not rows:
            print("❌ Немає даних в таблиці site_users")
            return
        
        print(f"✅ Знайдено {len(rows)} записів в site_users")
        
        for event_id, page_code in rows:
            print(f"\n--- Тестуємо event_id: {event_id}, page_code: {page_code} ---")
            
            # Тестуємо новий API для головної сторінки
            try:
                response = requests.get(f'http://localhost:8081/api/events_data_for_main_page?event={event_id}', timeout=5)
                print(f"API статус: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Отримано дані для event_id {event_id}:")
                    print(f"   Ціна: {data.get('price', 'N/A')}")
                    print(f"   Валюта: {data.get('currency', 'N/A')}")
                    print(f"   Адреса: {data.get('address', 'N/A')}")
                    
                    if data.get('events'):
                        first_event = data['events'][0]
                        print(f"   Перший івент: {first_event.get('name', 'N/A')} - {first_event.get('date', 'N/A')} {first_event.get('time', 'N/A')}")
                else:
                    print(f"❌ Помилка API: {response.status_code}")
                    print(f"   Відповідь: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Помилка запиту: {e}")
            
            # Тестуємо старий API для порівняння
            try:
                response = requests.get(f'http://localhost:8081/api/latest_event_data?page={page_code}', timeout=5)
                print(f"Старий API статус: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Старий API для page_code {page_code}:")
                    print(f"   Ціна: {data.get('price', 'N/A')}")
                    print(f"   Валюта: {data.get('currency', 'N/A')}")
                    print(f"   Адреса: {data.get('address', 'N/A')}")
                else:
                    print(f"❌ Помилка старого API: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Помилка запиту до старого API: {e}")
    
    except Exception as e:
        print(f"❌ Помилка: {e}")
    
    finally:
        conn.close()
    
    print("\n=== Тест завершено ===")
    print("\nІнструкції:")
    print("1. Переконайтеся, що сервер main.py запущений на порту 8081")
    print("2. Створіть нову силку через бота")
    print("3. Перевірте, чи правильно генерується посилання з ?event= замість ?page=")
    print("4. Перевірте, чи правильно завантажуються дані на головній сторінці")

if __name__ == "__main__":
    test_main_page_fix()
