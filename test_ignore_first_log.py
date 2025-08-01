#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы системы игнорирования первого лога
"""

import requests
import sqlite3
import time

def test_ignore_first_log():
    """Тестирует систему игнорирования первого лога"""
    
    print("=== ТЕСТ СИСТЕМЫ ИГНОРИРОВАНИЯ ПЕРВОГО ЛОГА ===")
    
    # Получаем существующий page_code из базы данных
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT page_code FROM site_users WHERE page_code IS NOT NULL LIMIT 1')
    row = c.fetchone()
    conn.close()
    
    if not row:
        print("❌ Нет page_code в базе данных для тестирования")
        return
    
    page_code = row[0]
    print(f"Тестируем с page_code: {page_code}")
    
    # Тестируем добавление в список игнорирования
    print("\n1. Тестируем добавление в список игнорирования:")
    servers = [
        'http://127.0.0.1:8080/ignore_first_visit',
        'http://127.0.0.1:8081/ignore_first_visit'
    ]
    
    for server_url in servers:
        try:
            response = requests.post(server_url, json={'page_code': page_code}, timeout=2)
            if response.status_code == 200:
                print(f"✅ {server_url}: успешно добавлен")
            else:
                print(f"❌ {server_url}: ошибка {response.status_code}")
        except Exception as e:
            print(f"❌ {server_url}: {e}")
    
    # Тестируем посещение страницы (первый раз - лог не должен отправляться)
    print(f"\n2. Тестируем посещение страницы с ?page={page_code}")
    print("   Первый раз - лог НЕ должен отправляться")
    
    test_urls = [
        f'http://127.0.0.1:8080/?page={page_code}',
        f'http://127.0.0.1:8081/?page={page_code}'
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url}: страница загружена")
            else:
                print(f"❌ {url}: ошибка {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")
    
    print("\n3. Тестируем повторное посещение страницы")
    print("   Второй раз - лог ДОЛЖЕН отправляться")
    
    time.sleep(2)  # Небольшая пауза
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {url}: страница загружена")
            else:
                print(f"❌ {url}: ошибка {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")
    print("Проверьте логи серверов и Telegram для подтверждения работы")

if __name__ == "__main__":
    test_ignore_first_log() 