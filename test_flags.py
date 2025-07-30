#!/usr/bin/env python3
import requests
import time
import json

def test_flags():
    base_url = "http://127.0.0.1:8080"
    
    print("🧪 Тестирование системы флагов...")
    
    # Тест 1: Установка push флага
    print("\n1. Тестируем push флаг...")
    response = requests.post(f"{base_url}/set_push_flag", 
                           json={'page_code': 'test123', 'type': 'push'})
    print(f"   set_push_flag response: {response.status_code} - {response.text}")
    
    # Тест 2: Проверка push флага
    response = requests.get(f"{base_url}/check_push?page_code=test123")
    print(f"   check_push response: {response.status_code} - {response.text}")
    
    # Тест 3: Повторная проверка (должна быть false)
    response = requests.get(f"{base_url}/check_push?page_code=test123")
    print(f"   check_push повторно: {response.status_code} - {response.text}")
    
    # Тест 4: Установка support флага
    print("\n2. Тестируем support флаг...")
    response = requests.post(f"{base_url}/set_support_flag", 
                           json={'ip': '192.168.1.1', 'type': 'support'})
    print(f"   set_support_flag response: {response.status_code} - {response.text}")
    
    # Тест 5: Проверка support флага
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.1")
    print(f"   check_support response: {response.status_code} - {response.text}")
    
    # Тест 6: Установка text флага
    print("\n3. Тестируем text флаг...")
    response = requests.post(f"{base_url}/set_custom_text", 
                           json={'text_id': 'test_text_123', 'text': 'Тестовое сообщение'})
    print(f"   set_custom_text response: {response.status_code} - {response.text}")
    
    response = requests.post(f"{base_url}/set_support_flag", 
                           json={'ip': '192.168.1.2', 'type': 'text', 'text_id': 'test_text_123'})
    print(f"   set_support_flag (text) response: {response.status_code} - {response.text}")
    
    # Тест 7: Проверка text флага
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.2")
    print(f"   check_support (text) response: {response.status_code} - {response.text}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_flags() 