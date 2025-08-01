#!/usr/bin/env python3
"""
Тест API endpoints для перевірки правильності даних івентів
"""
import requests
import json

def test_api_endpoints():
    base_url = "http://artpullse.com:8081"
    page_code = "1-12"  # Останній створений page_code з правильними даними
    
    print(f"=== ТЕСТУВАННЯ API ENDPOINTS ДЛЯ PAGE_CODE: {page_code} ===\n")
    
    # Тестуємо latest_event_data
    print("1. Тестуємо /api/latest_event_data")
    try:
        response = requests.get(f"{base_url}/api/latest_event_data?page={page_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Успішно отримано дані:")
            print(f"   Валюта: {data.get('currency')}")
            print(f"   Адреса: {data.get('street')}")
            print(f"   Ціна: {data.get('price')}")
            print("   Дати:")
            for i, date in enumerate(data.get('dates', [])):
                event_names = [
                    'Terroir and Traditions',
                    'Collection Co–selection', 
                    'Snucie',
                    'Art that saves lives',
                    'Gotong Royong',
                    'Anna Konik',
                    'Uncensored',
                    'Jacek Adamas'
                ]
                event_name = event_names[i] if i < len(event_names) else f"Event {i}"
                print(f"     {i}: {event_name} → {date}")
        else:
            print(f"   ❌ Помилка: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Помилка: {e}")
    
    print()
    
    # Тестуємо окремі event endpoints
    event_names = [
        'Terroir and Traditions',
        'Collection Co–selection', 
        'Snucie',
        'Art that saves lives',
        'Gotong Royong',
        'Anna Konik',
        'Uncensored',
        'Jacek Adamas'
    ]
    
    print("2. Тестуємо окремі event endpoints:")
    for i, event_name in enumerate(event_names):
        print(f"   {event_name} (event_index={i}):")
        
        # Тестуємо event_date
        try:
            response = requests.get(f"{base_url}/api/event_date?page={page_code}&event={i}")
            if response.status_code == 200:
                data = response.json()
                print(f"     Дата: {data.get('date', 'ПУСТО')}")
            else:
                print(f"     Дата: ❌ Помилка {response.status_code}")
        except Exception as e:
            print(f"     Дата: ❌ {e}")
        
        # Тестуємо event_time
        try:
            response = requests.get(f"{base_url}/api/event_time?page={page_code}&event={i}")
            if response.status_code == 200:
                data = response.json()
                print(f"     Час: {data.get('time', 'ПУСТО')}")
            else:
                print(f"     Час: ❌ Помилка {response.status_code}")
        except Exception as e:
            print(f"     Час: ❌ {e}")
        
        print()

if __name__ == '__main__':
    test_api_endpoints()
