#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки функціональності кнопки Request again
"""

import requests
import json
import time

def test_request_again():
    """Тестує функціональність Request again"""
    print("🧪 Тестування функціональності Request again...")
    
    # Тест 1: Встановлення флага для повторного запиту коду
    print("\n1. Тест встановлення флага Request again...")
    try:
        data = {
            'code': 'test-page-123'  # page_code для тестування
        }
        response = requests.post('http://127.0.0.1:8080/set_request_again', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Флаг Request again встановлено успішно")
        else:
            print("   ❌ Помилка встановлення флага")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    time.sleep(1)
    
    # Тест 2: Перевірка флага Request again
    print("\n2. Тест перевірки флага Request again...")
    try:
        response = requests.get('http://127.0.0.1:8080/check_request_again?code=test-page-123', timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            if response.text == 'true':
                print("   ✅ Флаг Request again активний - код запитується знову")
            else:
                print("   ❌ Флаг Request again не активний")
        else:
            print("   ❌ Помилка перевірки флага")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    time.sleep(1)
    
    # Тест 3: Перевірка після скидання флага
    print("\n3. Тест перевірки після скидання флага...")
    try:
        response = requests.get('http://127.0.0.1:8080/check_request_again?code=test-page-123', timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            if response.text == 'false':
                print("   ✅ Флаг Request again скинуто - код більше не запитується")
            else:
                print("   ❌ Флаг Request again все ще активний")
        else:
            print("   ❌ Помилка перевірки флага")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_code_notify_with_request_again():
    """Тестує code_notify з кнопкою Request again"""
    print("\n🧪 Тестування code_notify з кнопкою Request again...")
    
    try:
        data = {
            'page_code': 'test-request-again',
            'ip': '127.0.0.1',
            'code': 'TEST123'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Повідомлення про код надіслано з кнопкою Request again")
            print("   📱 Перевірте, чи з'явилося повідомлення в PAYMENT_GROUP_ID")
        else:
            print("   ❌ Помилка надсилання повідомлення")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестування функціональності Request again...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080 та бот на порту 8081!")
    print("=" * 60)
    
    test_request_again()
    test_code_notify_with_request_again()
    
    print("\n" + "=" * 60)
    print("✅ Тестування завершено!")
    print("\n📋 Що перевірити:")
    print("1. Чи правильно встановлюється флаг Request again")
    print("2. Чи правильно перевіряється флаг Request again")
    print("3. Чи правильно скидається флаг після перевірки")
    print("4. Чи з'являється повідомлення про код з кнопкою Request again")
    print("5. Чи працює кнопка Request again в Telegram")
    
    print("\n🔧 Як працює Request again:")
    print("1. Коли натискається кнопка Request again, встановлюється флаг")
    print("2. Фронтенд перевіряє цей флаг через /check_request_again?code=PAGE_CODE")
    print("3. Якщо флаг активний, показується вікно запиту коду")
    print("4. Після показу флаг автоматично скидається")
