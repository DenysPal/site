#!/usr/bin/env python3
"""
Скрипт для дебагу проблеми з Total
"""

import requests
import json

def debug_total_issue():
    """Дебагує проблему з Total"""
    print("🔍 Дебаг проблеми з Total...")
    
    # Тест 1: Перевіряємо, чи приймає /send_code total
    print("\n1. Тест /send_code з total...")
    try:
        data = {
            'page': '1-96',
            'total': '90',
            'currency': 'EUR',
            'ip': '127.0.0.1',
            'code': 'DEBUG90'
        }
        print(f"   Відправляємо: {data}")
        
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ /send_code прийняв total")
        else:
            print("   ❌ /send_code не прийняв total")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # Тест 2: Перевіряємо, чи приймає code_notify price
    print("\n2. Тест code_notify з price...")
    try:
        data = {
            'page_code': '1-96',
            'price': '90',
            'currency': 'EUR',
            'ip': '127.0.0.2',
            'code': 'DEBUG90'
        }
        print(f"   Відправляємо: {data}")
        
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ code_notify прийняв price")
        else:
            print("   ❌ code_notify не прийняв price")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    # Тест 3: Перевіряємо, чи правильно працює конвертація
    print("\n3. Тест конвертації total -> price...")
    try:
        # Спочатку надсилаємо через /send_code
        data1 = {
            'page': '1-96',
            'total': '180',
            'currency': 'USD',
            'ip': '127.0.0.3',
            'code': 'CONVERT180'
        }
        print(f"   Відправляємо через /send_code: {data1}")
        
        response1 = requests.post('http://127.0.0.1:8080/send_code', json=data1, timeout=5)
        print(f"   Відповідь /send_code: {response1.status_code}")
        
        if response1.status_code == 200:
            print("   ✅ /send_code успішний")
            print("   📱 Перевірте Telegram - має бути сума 180 USD")
        else:
            print("   ❌ /send_code не успішний")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def check_server_logs():
    """Перевіряє логи сервера"""
    print("\n📋 Перевірте логи сервера:")
    print("1. В терміналі з server.py має бути:")
    print("   [send_code] Перетворено 'total' на 'price': 90")
    print("2. В терміналі з main.py має бути:")
    print("   [code_notify] Використовуємо ціну: 90 EUR")

if __name__ == "__main__":
    print("🚀 Запуск дебагу проблеми з Total...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080 та бот на порту 8081!")
    print("=" * 60)
    
    debug_total_issue()
    check_server_logs()
    
    print("\n" + "=" * 60)
    print("✅ Дебаг завершено!")
    print("\n🔍 Що перевірити:")
    print("1. Чи показує server.py лог про конвертацію total -> price")
    print("2. Чи показує main.py лог про використання ціни")
    print("3. Чи правильно відображається сума в Telegram")
    print("4. Чи працює кнопка Request again")
