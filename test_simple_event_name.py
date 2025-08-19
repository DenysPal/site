#!/usr/bin/env python3
"""
Простий тест для перевірки передачі event_name
"""

import requests
import json

def test_event_name_direct():
    """Тестує пряму передачу event_name в payment_notify"""
    print("🧪 Тестуємо пряму передачу event_name...")
    
    data = {
        "name": "Тестовий користувач",
        "page_code": "1-15",
        "event_name": "Terroir and Traditions",  # ← Це має показатися в лозі
        "price": "90",
        "currency": "EUR"
    }
    
    try:
        response = requests.post('http://127.0.0.1:8081/payment_notify', json=data, timeout=5)
        print(f"✅ Відповідь: {response.status_code}")
        print(f"📝 Текст відповіді: {response.text}")
        return True
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_event_name_via_server():
    """Тестує передачу event_name через server.py"""
    print("🧪 Тестуємо передачу event_name через server.py...")
    
    data = {
        "name": "Тестовий користувач 2",
        "page_code": "2-25",
        "event_name": "Collection Co–selection",  # ← Це має показатися в лозі
        "price": "100",
        "currency": "USD"
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
    print("🚀 Простий тест event_name")
    print("=" * 50)
    
    test_event_name_direct()
    print("-" * 30)
    test_event_name_via_server()
    
    print("\n📋 Перевірте логи main.py та server.py")
    print("🔍 Шукайте рядки з 'Using provided event_name'")
