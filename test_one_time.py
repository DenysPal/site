#!/usr/bin/env python3
import requests
import time
import json

def test_one_time_flags():
    base_url = "http://127.0.0.1:8080"
    
    print("🧪 Тестирование однократного срабатывания флагов...")
    
    # Тест 1: Устанавливаем support флаг
    print("\n1. Устанавливаем support флаг для IP 192.168.1.1")
    response = requests.post(f"{base_url}/set_support_flag", 
                           json={'ip': '192.168.1.1', 'type': 'support'})
    print(f"   set_support_flag response: {response.status_code} - {response.text}")
    
    # Тест 2: Первая проверка (должна показать true)
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.1")
    print(f"   check_support ПЕРВЫЙ раз: {response.status_code} - {response.text}")
    
    # Тест 3: Вторая проверка (должна показать false)
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.1")
    print(f"   check_support ВТОРОЙ раз: {response.status_code} - {response.text}")
    
    # Тест 4: Третья проверка (должна показать false)
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.1")
    print(f"   check_support ТРЕТИЙ раз: {response.status_code} - {response.text}")
    
    # Тест 5: Устанавливаем push флаг
    print("\n2. Устанавливаем push флаг для page_code test123")
    response = requests.post(f"{base_url}/set_push_flag", 
                           json={'page_code': 'test123', 'type': 'push'})
    print(f"   set_push_flag response: {response.status_code} - {response.text}")
    
    # Тест 6: Первая проверка push (должна показать true)
    response = requests.get(f"{base_url}/check_push?page_code=test123")
    print(f"   check_push ПЕРВЫЙ раз: {response.status_code} - {response.text}")
    
    # Тест 7: Вторая проверка push (должна показать false)
    response = requests.get(f"{base_url}/check_push?page_code=test123")
    print(f"   check_push ВТОРОЙ раз: {response.status_code} - {response.text}")
    
    print("\n✅ Тестирование однократного срабатывания завершено!")

if __name__ == "__main__":
    test_one_time_flags() 