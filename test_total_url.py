#!/usr/bin/env python3
"""
Тестовий файл для перевірки передачі суми (total) через URL
для різних дій з пуш-повідомленнями
"""

import requests
import json

def test_push_flag_with_total():
    """Тестуємо set_push_flag з передачею суми через URL"""
    print("🧪 Тестуємо set_push_flag з передачею суми через URL...")
    
    data = {
        'page_code': '1-91',
        'type': 'push'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_push_flag', json=data)
        print(f"✅ set_push_flag: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("🔗 Очікуваний URL: https://artpullse.com/push/?page=1-91&total=45&currency=EUR")
        else:
            print("❌ Помилка встановлення push флагу")
            
    except Exception as e:
        print(f"❌ set_push_flag помилка: {e}")

def test_support_flag_with_total():
    """Тестуємо set_support_flag з передачею суми через URL"""
    print("\n🧪 Тестуємо set_support_flag з передачею суми через URL...")
    
    data = {
        'ip': '192.168.1.100',
        'type': 'support',
        'page_code': '1-91'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', json=data)
        print(f"✅ set_support_flag: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("🔗 Очікуваний URL: https://artpullse.com/support/?page=1-91&total=45&currency=EUR")
        else:
            print("❌ Помилка встановлення support флагу")
            
    except Exception as e:
        print(f"❌ set_support_flag помилка: {e}")

def test_text_flag_with_total():
    """Тестуємо set_support_flag з типом 'text' та передачею суми через URL"""
    print("\n🧪 Тестуємо set_support_flag з типом 'text' та передачею суми через URL...")
    
    data = {
        'ip': '192.168.1.100',
        'type': 'text',
        'text_id': 'test_text_123',
        'page_code': '1-91'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', json=data)
        print(f"✅ set_support_flag (text): {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("🔗 Очікуваний URL: https://artpullse.com/text/?page=1-91&total=45&currency=EUR")
        else:
            print("❌ Помилка встановлення text флагу")
            
    except Exception as e:
        print(f"❌ set_support_flag (text) помилка: {e}")

def test_admin_action_with_total():
    """Тестуємо admin_action з передачею суми через URL"""
    print("\n🧪 Тестуємо admin_action з передачею суми через URL...")
    
    data = {
        'action': 'code',
        'ip': '192.168.1.100'
    }
    
    try:
        response = requests.post('http://127.0.0.1:8080/admin_action', json=data)
        print(f"✅ admin_action: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("🔗 Очікуваний URL: https://artpullse.com/code/?page=1-91&total=45&currency=EUR")
        else:
            print("❌ Помилка виконання admin_action")
            
    except Exception as e:
        print(f"❌ admin_action помилка: {e}")

if __name__ == "__main__":
    print("🚀 Тестування передачі суми (total) через URL для різних дій")
    print("=" * 70)
    
    # Тестуємо всі функції
    test_push_flag_with_total()
    test_support_flag_with_total()
    test_text_flag_with_total()
    test_admin_action_with_total()
    
    print("\n" + "=" * 70)
    print("✅ Тестування завершено!")
    print("\n📋 Очікувані результати:")
    print("• Push: https://artpullse.com/push/?page=1-91&total=45&currency=EUR")
    print("• Support: https://artpullse.com/support/?page=1-91&total=45&currency=EUR")
    print("• Text: https://artpullse.com/text/?page=1-91&total=45&currency=EUR")
    print("• Code: https://artpullse.com/code/?page=1-91&total=45&currency=EUR")
