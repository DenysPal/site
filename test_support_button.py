#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест кнопки "Тех поддержка"
"""

import requests
import json

def test_support_button():
    """Тестуємо кнопку Тех поддержка"""
    
    print("🧪 Тестуємо кнопку Тех поддержка...")
    
    # Тестуємо set_support_flag endpoint
    print("\n1️⃣ Тестуємо set_support_flag endpoint...")
    
    data = {
        'ip': '127.0.0.1',
        'type': 'support',
        'page_code': 'test123'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', 
                               json=data, 
                               timeout=5)
        print(f"✅ set_support_flag: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Помилка: Сервер на порту 8080 не запущений!")
        print("💡 Запустіть server.py на порту 8080")
        return False
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False
    
    # Тестуємо check_support endpoint
    print("\n2️⃣ Тестуємо check_support endpoint...")
    
    try:
        response = requests.get('http://127.0.0.1:8080/check_support?ip=127.0.0.1', 
                               timeout=5)
        print(f"✅ check_support: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False
    
    # Тестуємо ще раз check_support (флаг має бути використаний)
    print("\n3️⃣ Тестуємо check_support ще раз (флаг має бути використаний)...")
    
    try:
        response = requests.get('http://127.0.0.1:8080/check_support?ip=127.0.0.1', 
                               timeout=5)
        print(f"✅ check_support (другий раз): {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False
    
    print("\n🎯 Тест завершено!")
    return True

if __name__ == "__main__":
    test_support_button()
