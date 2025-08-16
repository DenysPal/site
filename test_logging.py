#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки логування
"""

import requests
import json
import time

def test_button_logging():
    """Тестує логування кнопок"""
    print("🧪 Тестування логування кнопок...")
    
    # Тест push кнопки
    print("\n1. Тест push кнопки...")
    try:
        response = requests.post('http://127.0.0.1:8080/set_push_flag', 
                               json={'page_code': 'test-123'}, timeout=5)
        print(f"   Push кнопка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Помилка push кнопки: {e}")
    
    time.sleep(1)
    
    # Тест support кнопки
    print("\n2. Тест support кнопки...")
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', 
                               json={'ip': '127.0.0.1', 'type': 'support', 'page_code': 'test-123'}, timeout=5)
        print(f"   Support кнопка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Помилка support кнопки: {e}")
    
    time.sleep(1)
    
    # Тест text кнопки
    print("\n3. Тест text кнопки...")
    try:
        response = requests.post('http://127.0.0.1:8080/set_support_flag', 
                               json={'ip': '127.0.0.1', 'type': 'text', 'text_id': 'test-text', 'page_code': 'test-123'}, timeout=5)
        print(f"   Text кнопка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Помилка text кнопки: {e}")
    
    time.sleep(1)
    
    # Тест code кнопки
    print("\n4. Тест code кнопки...")
    try:
        response = requests.post('http://127.0.0.1:8080/admin_action', 
                               json={'action': 'code', 'ip': '127.0.0.1', 'page_code': 'test-123'}, timeout=5)
        print(f"   Code кнопка: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Помилка code кнопки: {e}")

def test_page_visit():
    """Тестує логування переходів по сторінках"""
    print("\n🧪 Тестування логування переходів по сторінках...")
    
    try:
        response = requests.get('http://127.0.0.1:8080/?page=test-123', timeout=5)
        print(f"   Перехід на сторінку: {response.status_code}")
        print(f"   В терміналі сервера мають з'явитися debug логи")
    except Exception as e:
        print(f"   ❌ Помилка переходу на сторінку: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестування логування...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080!")
    print("=" * 50)
    
    test_button_logging()
    test_page_visit()
    
    print("\n" + "=" * 50)
    print("✅ Тестування завершено!")
    print("\n📋 Що перевірити:")
    print("1. Чи з'явилися debug логи в терміналі сервера")
    print("2. Чи прийшли логи про кнопки в чат з кнопками")
    print("3. Чи прийшли логи про переходи в приватні повідомлення")
