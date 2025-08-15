#!/usr/bin/env python3
"""
Простий тест API для перевірки роботи latest_event_data
"""

import requests
import sqlite3
from datetime import datetime

def test_api():
    """Тестує API latest_event_data"""
    
    # Підключаємося до бази даних
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Знаходимо існуючий page_code
    cursor.execute('SELECT page_code FROM site_users LIMIT 1')
    row = cursor.fetchone()
    
    if not row:
        print("❌ Немає записів у базі даних")
        return
    
    page_code = row[0]
    print(f"📋 Тестуємо з page_code: {page_code}")
    
    # Тестуємо API
    base_url = "http://artpullse.com:8081"
    api_url = f"{base_url}/api/latest_event_data?page={page_code}"
    
    print(f"🔗 API URL: {api_url}")
    
    try:
        response = requests.get(api_url)
        print(f"📊 Статус відповіді: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Отримані дані:")
            print(f"   Дати: {data.get('dates', [])}")
            print(f"   Валюта: {data.get('currency')}")
            print(f"   Ціна: {data.get('price')}")
            print(f"   Адреса: {data.get('street')}")
        else:
            print(f"❌ Помилка: {response.text}")
            
    except Exception as e:
        print(f"❌ Помилка запиту: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_api() 