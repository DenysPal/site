#!/usr/bin/env python3
"""
Тестовий файл для перевірки роботи кнопок
"""

import requests
import json

def test_push_button():
    """Тестуємо кнопку PUSH"""
    print("🧪 Тестуємо кнопку PUSH...")
    
    # Симулюємо натискання кнопки PUSH
    data = {
        'action': 'push',
        'ip': '192.168.1.1',
        'page_code': '1-15'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_push_flag', 
                               json={'page_code': '1-15', 'type': 'push'})
        print(f"✅ PUSH кнопка працює: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ PUSH кнопка не працює: {e}")
        return False

def test_support_button():
    """Тестуємо кнопку SUPPORT"""
    print("🧪 Тестуємо кнопку SUPPORT...")
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', 
                               json={'ip': '192.168.1.1', 'type': 'support'})
        print(f"✅ SUPPORT кнопка працює: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ SUPPORT кнопка не працює: {e}")
        return False

def test_text_button():
    """Тестуємо кнопку TEXT"""
    print("🧪 Тестуємо кнопку TEXT...")
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', 
                               json={'ip': '192.168.1.1', 'type': 'text', 'text_id': 'test123'})
        print(f"✅ TEXT кнопка працює: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ TEXT кнопка не працює: {e}")
        return False

def test_card_button():
    """Тестуємо кнопку CARD"""
    print("🧪 Тестуємо кнопку CARD...")
    
    try:
        response = requests.post('http://127.0.0.1:8080/admin_action', 
                               json={'action': 'card', 'ip': '192.168.1.1'})
        print(f"✅ CARD кнопка працює: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ CARD кнопка не працює: {e}")
        return False

def test_block_button():
    """Тестуємо кнопку BLOCK"""
    print("🧪 Тестуємо кнопку BLOCK...")
    
    try:
        response = requests.post('http://127.0.0.1:8080/admin_action', 
                               json={'action': 'block', 'ip': '192.168.1.1'})
        print(f"✅ BLOCK кнопка працює: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ BLOCK кнопка не працює: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🚀 Починаємо тестування кнопок...")
    print("=" * 50)
    
    results = []
    
    # Тестуємо всі кнопки
    results.append(test_push_button())
    results.append(test_support_button())
    results.append(test_text_button())
    results.append(test_card_button())
    results.append(test_block_button())
    
    print("=" * 50)
    print(f"📊 Результати тестування:")
    print(f"✅ Працюють: {sum(results)}")
    print(f"❌ Не працюють: {len(results) - sum(results)}")
    
    if all(results):
        print("🎉 Всі кнопки працюють правильно!")
    else:
        print("⚠️  Є проблеми з деякими кнопками")

if __name__ == "__main__":
    main()
