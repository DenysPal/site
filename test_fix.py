#!/usr/bin/env python3
import requests
import time
import json

def test_flag_isolation():
    base_url = "http://127.0.0.1:8080"
    
    print("🧪 Тестирование изоляции флагов...")
    
    # Тест 1: Устанавливаем флаг для IP 1
    print("\n1. Устанавливаем support флаг для IP 192.168.1.1")
    response = requests.post(f"{base_url}/set_support_flag", 
                           json={'ip': '192.168.1.1', 'type': 'support'})
    print(f"   set_support_flag response: {response.status_code} - {response.text}")
    
    # Тест 2: Проверяем флаг для IP 1
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.1")
    print(f"   check_support для IP 1: {response.status_code} - {response.text}")
    
    # Тест 3: Проверяем флаг для IP 2 (должен быть пустым)
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.2")
    print(f"   check_support для IP 2: {response.status_code} - {response.text}")
    
    # Тест 4: Устанавливаем флаг для IP 2
    print("\n2. Устанавливаем support флаг для IP 192.168.1.2")
    response = requests.post(f"{base_url}/set_support_flag", 
                           json={'ip': '192.168.1.2', 'type': 'support'})
    print(f"   set_support_flag response: {response.status_code} - {response.text}")
    
    # Тест 5: Проверяем флаг для IP 1 (должен быть сброшен)
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.1")
    print(f"   check_support для IP 1 после установки для IP 2: {response.status_code} - {response.text}")
    
    # Тест 6: Проверяем флаг для IP 2
    response = requests.get(f"{base_url}/check_support?ip=192.168.1.2")
    print(f"   check_support для IP 2: {response.status_code} - {response.text}")
    
    print("\n✅ Тестирование изоляции завершено!")

if __name__ == "__main__":
    test_flag_isolation() 