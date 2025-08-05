#!/usr/bin/env python3
"""
Скрипт для тестування завантаження даних в браузері
"""

import webbrowser
import time

def test_browser():
    """Відкриває тестові сторінки в браузері"""
    
    base_url = "http://localhost:8080"
    page_code = "1-1"  # Використовуємо існуючий page_code
    
    print("🌐 Відкриваю тестові сторінки в браузері...")
    
    # Тест 1: Тестова сторінка з page_code
    test_url_1 = f"{base_url}/test_with_page_code.html?page={page_code}"
    print(f"1️⃣ Тестова сторінка: {test_url_1}")
    webbrowser.open(test_url_1)
    
    time.sleep(2)
    
    # Тест 2: Головна сторінка з page_code
    test_url_2 = f"{base_url}/events-art.com/index.html?page={page_code}"
    print(f"2️⃣ Головна сторінка: {test_url_2}")
    webbrowser.open(test_url_2)
    
    print("\n📋 Інструкції для тестування:")
    print("1. Відкрийте Developer Tools (F12)")
    print("2. Перейдіть на вкладку Console")
    print("3. Перевірте, чи є повідомлення про завантаження даних")
    print("4. Перевірте, чи оновилися дати та час на сторінці")
    
    print(f"\n🔍 Очікувані повідомлення в консолі:")
    print(f"   - 'Loading event data with page_code: {page_code}'")
    print(f"   - 'Received data: {...}'")
    print(f"   - 'Found event blocks: 8'")
    print(f"   - 'Block 0: date=\"28.06.2025\", time=\"10:00-22:20\"'")

if __name__ == "__main__":
    test_browser() 