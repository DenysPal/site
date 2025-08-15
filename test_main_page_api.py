#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки API головної сторінки
"""

import requests
import json
import sqlite3

# Базовий URL для тестування
BASE_URL = "http://localhost:8080"

def test_main_page_api():
    """Тестує API для головної сторінки"""
    print("🧪 ТЕСТУВАННЯ API ГОЛОВНОЇ СТОРІНКИ")
    print("=" * 50)
    
    # Підключаємося до бази даних
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Отримуємо всі event_id з бази
    c.execute('SELECT id, page_code FROM site_users WHERE page_code IS NOT NULL LIMIT 3')
    rows = c.fetchall()
    
    if not rows:
        print("❌ Немає даних в базі для тестування")
        return
    
    print(f"✅ Знайдено {len(rows)} записів для тестування")
    
    for i, (event_id, page_code) in enumerate(rows, 1):
        print(f"\n🔍 Тест {i}: event_id={event_id}, page_code={page_code}")
        
        # Тестуємо API
        url = f"{BASE_URL}/api/events_data_for_main_page"
        params = {'event': event_id}
        
        try:
            response = requests.get(url, params=params)
            print(f"URL: {url}")
            print(f"Параметри: {params}")
            print(f"Статус: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ УСПІХ")
                print(f"Отримано {len(data.get('events', []))} подій")
                
                # Перевіряємо перші кілька подій
                for j, event in enumerate(data.get('events', [])[:3]):
                    print(f"  Подія {j+1}: {event.get('name')} - {event.get('date')} {event.get('time')}")
                    
            else:
                print("❌ ПОМИЛКА")
                print(f"Відповідь: {response.text}")
                
        except Exception as e:
            print(f"❌ ПОМИЛКА: {e}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")

if __name__ == "__main__":
    test_main_page_api()
