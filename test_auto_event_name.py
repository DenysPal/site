#!/usr/bin/env python3
"""
Тест автоматичного отримання event_name з бази даних
"""

import requests
import json

def test_auto_event_name_payment():
    """Тестує автоматичне отримання event_name в payment_notify"""
    print("🧪 Тестуємо автоматичне отримання event_name в payment_notify...")
    
    # НЕ передаємо event_name - система має отримати його автоматично
    data = {
        "name": "Тестовий користувач",
        "page_code": "1-15",  # Це має автоматично дати "Terroir and Traditions"
        "price": "90",
        "currency": "EUR"
        # event_name відсутній - має бути отримано з бази
    }
    
    try:
        response = requests.post('http://127.0.0.1:8081/payment_notify', json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code}")
        print(f"📝 Текст відповіді: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_auto_event_name_code():
    """Тестує автоматичне отримання event_name в code_notify"""
    print("🧪 Тестуємо автоматичне отримання event_name в code_notify...")
    
    # НЕ передаємо event_name - система має отримати його автоматично
    data = {
        "page_code": "2-25",  # Це має автоматично дати "Collection Co–selection"
        "code": "TEST123",
        "price": "100",
        "currency": "USD"
        # event_name відсутній - має бути отримано з бази
    }
    
    try:
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code}")
        print(f"📝 Текст відповіді: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_auto_event_name_via_server():
    """Тестує автоматичне отримання event_name через server.py"""
    print("🧪 Тестуємо автоматичне отримання event_name через server.py...")
    
    # НЕ передаємо event_name - server.py має отримати його автоматично
    data = {
        "name": "Тестовий користувач 3",
        "page_code": "3-35",  # Це має автоматично дати "Snucie"
        "price": "200",
        "currency": "GBP"
        # event_name відсутній - має бути отримано з бази
    }
    
    try:
        response = requests.post('http://127.0.0.1:8000/send_payment_data', json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code}")
        print(f"📝 Текст відповіді: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тест автоматичного отримання event_name")
    print("=" * 60)
    print("📋 Цей тест перевіряє, чи система автоматично отримує")
    print("   назву події з бази даних, якщо event_name не передано")
    print("=" * 60)
    
    test_auto_event_name_payment()
    print("-" * 40)
    
    test_auto_event_name_code()
    print("-" * 40)
    
    test_auto_event_name_via_server()
    
    print("\n📋 Перевірте логи main.py та server.py")
    print("🔍 Шукайте рядки з 'Got event_name from database'")
    print("🎯 Очікуваний результат: правильні назви подій замість 'Выставка'")
