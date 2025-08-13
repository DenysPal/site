#!/usr/bin/env python3
"""
Тест стабільності сайту artpullse.com
Перевіряє всі основні функції та API endpoints
"""

import requests
import json
import time
import sqlite3
from urllib.parse import urlparse

# Налаштування тестування
BASE_URL = "http://localhost:8080"
TEST_PAGE_CODE = "test-stability-123"

def test_home_button():
    """Тестує роботу кнопки Home"""
    print("🔍 Тестування кнопки Home...")
    
    try:
        # Запит головної сторінки
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            # Перевіряємо наявність правильної кнопки Home
            if 'href="/"' in response.text:
                print("✅ Кнопка Home працює правильно")
                return True
            else:
                print("❌ Кнопка Home має неправильне посилання")
                return False
        else:
            print(f"❌ Помилка завантаження головної сторінки: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Помилка тестування кнопки Home: {e}")
        return False

def test_api_endpoints():
    """Тестує API endpoints"""
    print("\n🔍 Тестування API endpoints...")
    
    # Тест 1: events_data_for_main_page
    print("  📊 Тест events_data_for_main_page...")
    try:
        response = requests.get(f"{BASE_URL}/api/events_data_for_main_page?page={TEST_PAGE_CODE}")
        if response.status_code == 200:
            data = response.json()
            if 'price' in data and 'currency' in data and 'dates' in data:
                print(f"    ✅ Отримано дані: ціна={data['price']}, валюта={data['currency']}, дат={len(data['dates'])}")
            else:
                print(f"    ⚠️ Неповні дані: {data}")
        else:
            print(f"    ❌ Помилка API: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Помилка запиту: {e}")
    
    # Тест 2: data_by_ip
    print("  🌐 Тест data_by_ip...")
    try:
        response = requests.get(f"{BASE_URL}/api/data_by_ip?page={TEST_PAGE_CODE}")
        if response.status_code == 200:
            data = response.json()
            if 'price' in data and 'currency' in data and 'ip' in data:
                print(f"    ✅ Отримано дані: ціна={data['price']}, валюта={data['currency']}, IP={data['ip']}")
            else:
                print(f"    ⚠️ Неповні дані: {data}")
        else:
            print(f"    ❌ Помилка API: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Помилка запиту: {e}")

def test_database_connection():
    """Тестує підключення до бази даних"""
    print("\n🔍 Тестування підключення до бази даних...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Перевіряємо структуру таблиці
        c.execute("PRAGMA table_info(site_users)")
        columns = c.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"  📋 Колонки таблиці site_users: {column_names}")
        
        # Перевіряємо наявність даних
        c.execute("SELECT COUNT(*) FROM site_users")
        count = c.fetchone()[0]
        print(f"  📊 Кількість записів: {count}")
        
        # Перевіряємо наявність page_code
        c.execute("SELECT COUNT(*) FROM site_users WHERE page_code IS NOT NULL")
        page_code_count = c.fetchone()[0]
        print(f"  🔑 Записи з page_code: {page_code_count}")
        
        conn.close()
        print("  ✅ Підключення до бази даних успішне")
        return True
        
    except Exception as e:
        print(f"  ❌ Помилка підключення до бази даних: {e}")
        return False

def test_page_navigation():
    """Тестує навігацію між сторінками"""
    print("\n🔍 Тестування навігації між сторінками...")
    
    try:
        # Тест переходу на головну сторінку з page_code
        response = requests.get(f"{BASE_URL}/?page={TEST_PAGE_CODE}")
        if response.status_code == 200:
            print("  ✅ Головна сторінка з page_code завантажена")
            
            # Перевіряємо наявність page_code в посиланнях
            if f'page={TEST_PAGE_CODE}' in response.text:
                print("  ✅ page_code додано до посилань")
            else:
                print("  ⚠️ page_code не додано до посилань")
        else:
            print(f"  ❌ Помилка завантаження сторінки: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Помилка тестування навігації: {e}")

def test_error_handling():
    """Тестує обробку помилок"""
    print("\n🔍 Тестування обробки помилок...")
    
    # Тест 1: Неправильний page_code
    print("  🚫 Тест неправильного page_code...")
    try:
        response = requests.get(f"{BASE_URL}/api/events_data_for_main_page?page=invalid")
        if response.status_code == 200:
            data = response.json()
            if 'price' in data and 'currency' in data:
                print(f"    ✅ Fallback дані працюють: ціна={data['price']}, валюта={data['currency']}")
            else:
                print(f"    ⚠️ Fallback дані неповні: {data}")
        else:
            print(f"    ❌ Помилка API: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Помилка запиту: {e}")
    
    # Тест 2: Відсутній page_code
    print("  🚫 Тест відсутності page_code...")
    try:
        response = requests.get(f"{BASE_URL}/api/events_data_for_main_page")
        if response.status_code == 400:
            print("    ✅ Правильна обробка відсутності page_code")
        else:
            print(f"    ⚠️ Неочікуваний статус: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Помилка запиту: {e}")

def test_performance():
    """Тестує продуктивність"""
    print("\n🔍 Тестування продуктивності...")
    
    # Тест швидкості API
    print("  ⚡ Тест швидкості API...")
    
    start_time = time.time()
    try:
        response = requests.get(f"{BASE_URL}/api/events_data_for_main_page?page={TEST_PAGE_CODE}")
        end_time = time.time()
        
        if response.status_code == 200:
            response_time = (end_time - start_time) * 1000  # в мілісекундах
            print(f"    ⏱️ Час відповіді API: {response_time:.2f}ms")
            
            if response_time < 100:
                print("    ✅ Швидкість API відмінна")
            elif response_time < 500:
                print("    ✅ Швидкість API хороша")
            else:
                print("    ⚠️ Швидкість API може бути кращою")
        else:
            print(f"    ❌ Помилка API: {response.status_code}")
            
    except Exception as e:
        print(f"    ❌ Помилка тестування швидкості: {e}")

def run_all_tests():
    """Запускає всі тести"""
    print("🚀 Запуск тестів стабільності сайту artpullse.com")
    print("=" * 60)
    
    results = []
    
    # Запускаємо всі тести
    results.append(("Кнопка Home", test_home_button()))
    test_api_endpoints()
    results.append(("База даних", test_database_connection()))
    test_page_navigation()
    test_error_handling()
    test_performance()
    
    # Підсумок
    print("\n" + "=" * 60)
    print("📊 ПІДСУМОК ТЕСТУВАННЯ")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ПРОВАЛЕНО"
        print(f"{test_name}: {status}")
    
    print(f"\nЗагальний результат: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("🎉 Всі тести пройдено успішно! Сайт стабільний.")
    else:
        print("⚠️ Деякі тести не пройдено. Перевірте проблеми.")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n⏹️ Тестування перервано користувачем")
    except Exception as e:
        print(f"\n❌ Критична помилка тестування: {e}") 