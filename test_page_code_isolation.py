#!/usr/bin/env python3
"""
Тест для перевірки ізоляції даних між різними page_code
"""

import requests
import sqlite3
import random
import string
from datetime import datetime, timedelta

def generate_test_data():
    """Генерує тестові дані для двох різних page_code"""
    
    # Підключаємося до бази даних
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Генеруємо два унікальні page_code
    page_code_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    page_code_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Генеруємо різні дати для подій
    base_date = datetime.now()
    
    # Дані для першого page_code
    dates_1 = [
        (base_date + timedelta(days=1)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=2)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=3)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=4)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=5)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=6)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=7)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=8)).strftime('%d.%m.%Y')
    ]
    
    # Дані для другого page_code
    dates_2 = [
        (base_date + timedelta(days=10)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=11)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=12)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=13)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=14)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=15)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=16)).strftime('%d.%m.%Y'),
        (base_date + timedelta(days=17)).strftime('%d.%m.%Y')
    ]
    
    # Додаємо записи до бази даних
    cursor.execute('''
        INSERT INTO site_users (page_code, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, 
                               currency, street, price, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (page_code_1, dates_1[0], dates_1[1], dates_1[2], dates_1[3], dates_1[4], dates_1[5], dates_1[6], dates_1[7],
          'EUR', 'Test Street 1', '50', datetime.now().isoformat()))
    
    cursor.execute('''
        INSERT INTO site_users (page_code, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, 
                               currency, street, price, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (page_code_2, dates_2[0], dates_2[1], dates_2[2], dates_2[3], dates_2[4], dates_2[5], dates_2[6], dates_2[7],
          'USD', 'Test Street 2', '75', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return page_code_1, page_code_2, dates_1, dates_2

def test_api_isolation():
    """Тестує ізоляцію даних між різними page_code"""
    
    print("🔧 Генеруємо тестові дані...")
    page_code_1, page_code_2, dates_1, dates_2 = generate_test_data()
    
    print(f"📋 Page Code 1: {page_code_1}")
    print(f"📋 Page Code 2: {page_code_2}")
    
    base_url = "http://artpullse.com:8081"
    
    print("\n🧪 Тестуємо API latest_event_data...")
    
    # Тест 1: Отримуємо дані для першого page_code
    print(f"\n1️⃣ Запит даних для {page_code_1}:")
    response1 = requests.get(f"{base_url}/api/latest_event_data?page={page_code_1}")
    print(f"   Статус: {response1.status_code}")
    
    if response1.status_code == 200:
        data1 = response1.json()
        print(f"   Отримані дати: {data1.get('dates', [])}")
        print(f"   Валюта: {data1.get('currency')}")
        print(f"   Ціна: {data1.get('price')}")
    else:
        print(f"   Помилка: {response1.text}")
    
    # Тест 2: Отримуємо дані для другого page_code
    print(f"\n2️⃣ Запит даних для {page_code_2}:")
    response2 = requests.get(f"{base_url}/api/latest_event_data?page={page_code_2}")
    print(f"   Статус: {response2.status_code}")
    
    if response2.status_code == 200:
        data2 = response2.json()
        print(f"   Отримані дати: {data2.get('dates', [])}")
        print(f"   Валюта: {data2.get('currency')}")
        print(f"   Ціна: {data2.get('price')}")
    else:
        print(f"   Помилка: {response2.text}")
    
    # Тест 3: Перевіряємо, що дані різні
    print(f"\n3️⃣ Перевірка ізоляції даних:")
    if response1.status_code == 200 and response2.status_code == 200:
        data1 = response1.json()
        data2 = response2.json()
        
        dates_different = data1.get('dates') != data2.get('dates')
        currency_different = data1.get('currency') != data2.get('currency')
        price_different = data1.get('price') != data2.get('price')
        
        print(f"   Дати різні: {'✅' if dates_different else '❌'}")
        print(f"   Валюти різні: {'✅' if currency_different else '❌'}")
        print(f"   Ціни різні: {'✅' if price_different else '❌'}")
        
        if dates_different and currency_different and price_different:
            print("   🎉 Ізоляція даних працює коректно!")
        else:
            print("   ⚠️ Проблема з ізоляцією даних!")
    else:
        print("   ❌ Не вдалося отримати дані для порівняння")
    
    # Тест 4: Перевіряємо кешування
    print(f"\n4️⃣ Тест кешування (другий запит для {page_code_1}):")
    response1_2 = requests.get(f"{base_url}/api/latest_event_data?page={page_code_1}&_t={datetime.now().timestamp()}")
    print(f"   Статус: {response1_2.status_code}")
    
    if response1_2.status_code == 200:
        data1_2 = response1_2.json()
        print(f"   Отримані дати: {data1_2.get('dates', [])}")
        
        # Перевіряємо, що дані однакові (не змінились через кеш)
        if response1.status_code == 200:
            data1 = response1.json()
            same_data = data1.get('dates') == data1_2.get('dates')
            print(f"   Дані однакові: {'✅' if same_data else '❌'}")
    
    # Очищення тестових даних
    print(f"\n🧹 Очищення тестових даних...")
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM site_users WHERE page_code IN (?, ?)', (page_code_1, page_code_2))
    conn.commit()
    conn.close()
    
    print("✅ Тест завершено!")

if __name__ == "__main__":
    test_api_isolation() 