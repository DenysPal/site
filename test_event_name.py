#!/usr/bin/env python3
"""
Скрипт для тестування нової функціональності з event_name
"""

import requests
import json
import time

# Налаштування
MAIN_API_URL = "http://127.0.0.1:8081"
SERVER_URL = "http://127.0.0.1:8000"

def test_payment_notify_with_event_name():
    """Тестує payment_notify з передачею event_name"""
    print("🧪 Тестуємо payment_notify з event_name...")
    
    data = {
        "name": "Тестовий користувач",
        "phone": "+380991234567",
        "email": "test@example.com",
        "card": "4111111111111111",
        "cvv": "123",
        "expiry": "12/25",
        "price": "100",
        "currency": "USD",
        "total": "120",
        "page_code": "1-15",
        "event_name": "Terroir and Traditions"
    }
    
    try:
        response = requests.post(f"{MAIN_API_URL}/payment_notify", json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_payment_notify_without_event_name():
    """Тестує payment_notify без event_name (fallback логіка)"""
    print("🧪 Тестуємо payment_notify без event_name (fallback)...")
    
    data = {
        "name": "Тестовий користувач 2",
        "phone": "+380991234568",
        "email": "test2@example.com",
        "card": "4111111111111112",
        "cvv": "456",
        "expiry": "12/26",
        "price": "150",
        "currency": "EUR",
        "total": "180",
        "page_code": "2-25"
        # event_name відсутній
    }
    
    try:
        response = requests.post(f"{MAIN_API_URL}/payment_notify", json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_code_notify_with_event_name():
    """Тестує code_notify з передачею event_name"""
    print("🧪 Тестуємо code_notify з event_name...")
    
    data = {
        "page_code": "1-15",
        "event_name": "Terroir and Traditions",
        "code": "TEST123",
        "price": "100",
        "currency": "USD"
    }
    
    try:
        response = requests.post(f"{MAIN_API_URL}/code_notify", json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_send_payment_data_with_event_name():
    """Тестує send_payment_data через server.py з event_name"""
    print("🧪 Тестуємо send_payment_data через server.py з event_name...")
    
    data = {
        "name": "Тестовий користувач 3",
        "phone": "+380991234569",
        "email": "test3@example.com",
        "card": "4111111111111113",
        "cvv": "789",
        "expiry": "12/27",
        "price": "200",
        "currency": "GBP",
        "total": "240",
        "page_code": "3-35",
        "event_name": "Collection Co–selection"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/send_payment_data", json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_send_code_with_event_name():
    """Тестує send_code через server.py з event_name"""
    print("🧪 Тестуємо send_code через server.py з event_name...")
    
    data = {
        "page_code": "3-35",
        "event_name": "Collection Co–selection",
        "code": "TEST456",
        "price": "200",
        "currency": "GBP"
    }
    
    try:
        response = requests.post(f"{SERVER_URL}/send_code", json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🚀 Починаємо тестування нової функціональності з event_name")
    print("=" * 60)
    
    tests = [
        test_payment_notify_with_event_name,
        test_payment_notify_without_event_name,
        test_code_notify_with_event_name,
        test_send_payment_data_with_event_name,
        test_send_code_with_event_name
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 40)
            time.sleep(1)  # Невелика пауза між тестами
        except Exception as e:
            print(f"❌ Критична помилка в тесті: {e}")
            print("-" * 40)
    
    print("=" * 60)
    print(f"📊 Результати тестування: {passed}/{total} тестів пройшло успішно")
    
    if passed == total:
        print("🎉 Всі тести пройшли успішно!")
    else:
        print("⚠️  Деякі тести не пройшли. Перевірте логи та налаштування.")

if __name__ == "__main__":
    main()
