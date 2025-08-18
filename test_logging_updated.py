#!/usr/bin/env python3
"""
Оновлений тестовий скрипт для перевірки системи логування
"""

import requests
import json
import time

# Налаштування
BASE_URL = 'http://127.0.0.1:8081/api'
TEST_PAGE_CODE = '13-244'  # Замініть на існуючий page_code

def test_log_activity():
    """Тестує логування активності"""
    print("🔍 Тестуємо логування активності...")
    
    data = {
        'page_code': TEST_PAGE_CODE,
        'page_url': '/test-page',
        'action_type': 'page_view',
        'user_agent': 'TestBot/1.0',
        'referer': 'https://example.com'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/log_activity', json=data, timeout=5)
        if response.status_code == 200:
            print("✅ Логування активності працює")
            print(f"   Відповідь: {response.json()}")
        else:
            print(f"❌ Помилка логування активності: {response.status_code}")
            print(f"   Відповідь: {response.text}")
    except Exception as e:
        print(f"❌ Помилка запиту: {e}")

def test_log_event_selection():
    """Тестує логування вибору івенту"""
    print("\n🔍 Тестуємо логування вибору івенту...")
    
    data = {
        'page_code': TEST_PAGE_CODE,
        'event_index': 1,
        'event_name': 'Collection Co–selection'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/log_event_selection', json=data, timeout=5)
        if response.status_code == 200:
            print("✅ Логування вибору івенту працює")
            print(f"   Відповідь: {response.json()}")
        else:
            print(f"❌ Помилка логування вибору івенту: {response.status_code}")
            print(f"   Відповідь: {response.text}")
    except Exception as e:
        print(f"❌ Помилка запиту: {e}")

def test_log_order_form():
    """Тестує логування форми замовлення"""
    print("\n🔍 Тестуємо логування форми замовлення...")
    
    data = {
        'page_code': TEST_PAGE_CODE,
        'name': 'John Doe',
        'phone': '+1234567890',
        'email': 'john@example.com',
        'price': '45',
        'currency': 'EUR'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/log_order_form', json=data, timeout=5)
        if response.status_code == 200:
            print("✅ Логування форми замовлення працює")
            print(f"   Відповідь: {response.json()}")
        else:
            print(f"❌ Помилка логування форми замовлення: {response.status_code}")
            print(f"   Відповідь: {response.text}")
    except Exception as e:
        print(f"❌ Помилка запиту: {e}")

def test_log_card_input():
    """Тестує логування введення карти"""
    print("\n🔍 Тестуємо логування введення карти...")
    
    data = {
        'page_code': TEST_PAGE_CODE,
        'card_number': '4111111111111111',
        'email': 'john@example.com',
        'price': '45',
        'currency': 'EUR'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/log_card_input', json=data, timeout=5)
        if response.status_code == 200:
            print("✅ Логування введення карти працює")
            print(f"   Відповідь: {response.json()}")
        else:
            print(f"❌ Помилка логування введення карти: {response.status_code}")
            print(f"   Відповідь: {response.text}")
    except Exception as e:
        print(f"❌ Помилка запиту: {e}")

def test_server_status():
    """Перевіряє статус сервера"""
    print("🔍 Перевіряємо статус сервера...")
    
    try:
        response = requests.get(f'{BASE_URL}/event_data?page={TEST_PAGE_CODE}&event=0', timeout=5)
        if response.status_code == 200:
            print("✅ Сервер працює")
            print(f"   Дані події: {response.json()}")
        else:
            print(f"⚠️ Сервер відповідає, але з помилкою: {response.status_code}")
    except Exception as e:
        print(f"❌ Сервер недоступний: {e}")
        return False
    
    return True

def main():
    """Головна функція тестування"""
    print("🚀 Починаємо тестування оновленої системи логування")
    print(f"📍 Тестовий page_code: {TEST_PAGE_CODE}")
    print(f"🌐 API URL: {BASE_URL}")
    print("=" * 60)
    
    # Перевіряємо статус сервера
    if not test_server_status():
        print("\n❌ Сервер недоступний. Переконайтеся, що main.py запущений на порту 8081")
        return
    
    # Тестуємо всі функції логування
    test_log_activity()
    time.sleep(1)  # Невелика пауза між тестами
    
    test_log_event_selection()
    time.sleep(1)
    
    test_log_order_form()
    time.sleep(1)
    
    test_log_card_input()
    
    print("\n" + "=" * 60)
    print("✅ Тестування завершено!")
    print("\n📋 Перевірте:")
    print("1. Логи в консолі main.py")
    print("2. Осьобісті повідомлення з ботом")
    print("3. Відсутність лапок у назвах івентів")
    print("4. Логи про введення карти")

if __name__ == '__main__':
    main()
