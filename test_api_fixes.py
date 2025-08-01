#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки API-виправлень
Перевіряє, чи всі API-ендпоінти правильно обробляють page_code
"""

import requests
import json

# Базовий URL для тестування
BASE_URL = "http://localhost:8080"

def test_api_endpoint(endpoint, params, expected_status=200, description=""):
    """Тестує API-ендпоінт"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🔍 Тестуємо: {description}")
    print(f"URL: {url}")
    print(f"Параметри: {params}")
    
    try:
        response = requests.get(url, params=params)
        print(f"Статус: {response.status_code}")
        
        if response.status_code == expected_status:
            print("✅ УСПІХ")
            if response.content:
                try:
                    data = response.json()
                    print(f"Відповідь: {json.dumps(data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"Відповідь: {response.text}")
        else:
            print("❌ ПОМИЛКА - неочікуваний статус")
            print(f"Очікував: {expected_status}, отримав: {response.status_code}")
            if response.content:
                print(f"Відповідь: {response.text}")
                
    except Exception as e:
        print(f"❌ ПОМИЛКА: {e}")

def main():
    print("🧪 ТЕСТУВАННЯ API-ВИПРАВЛЕНЬ")
    print("=" * 50)
    
    # Тест 1: latest_event_data без page_code (має повернути 400)
    test_api_endpoint(
        "/api/latest_event_data",
        {},
        expected_status=400,
        description="latest_event_data без page_code (має повернути помилку)"
    )
    
    # Тест 2: latest_event_data з page_code (має повернути 404 для неіснуючого коду)
    test_api_endpoint(
        "/api/latest_event_data",
        {"page": "non-existent-code"},
        expected_status=404,
        description="latest_event_data з неіснуючим page_code"
    )
    
    # Тест 3: event_places_api без page_code (має повернути 400)
    test_api_endpoint(
        "/api/event_places",
        {"event": "0"},
        expected_status=400,
        description="event_places_api без page_code"
    )
    
    # Тест 4: event_date_api без page_code (має повернути 400)
    test_api_endpoint(
        "/api/event_date",
        {"event": "0"},
        expected_status=400,
        description="event_date_api без page_code"
    )
    
    # Тест 5: event_time_api без page_code (має повернути 400)
    test_api_endpoint(
        "/api/event_time",
        {"event": "0"},
        expected_status=400,
        description="event_time_api без page_code"
    )
    
    # Тест 6: payment_data без page_code (має повернути 400)
    test_api_endpoint(
        "/api/payment_data",
        {},
        expected_status=400,
        description="payment_data без page_code"
    )
    
    # Тест 7: event_address без page_code (має повернути 400)
    test_api_endpoint(
        "/api/event_address",
        {},
        expected_status=400,
        description="event_address без page_code"
    )
    
    print("\n" + "=" * 50)
    print("✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print("\nЯкщо всі тести пройшли успішно, то:")
    print("- ✅ API-ендпоінти завжди вимагають page_code")
    print("- ✅ Немає fallback до останнього запису")
    print("- ✅ Кожна силка буде показувати свої дані")

if __name__ == "__main__":
    main() 