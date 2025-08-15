#!/usr/bin/env python3

import requests
import time

def test_logging():
    """Тестує логування переходів на сторінки"""
    
    base_url = "http://127.0.0.1:8080"
    
    # Тестуємо різні сторінки
    test_pages = [
        "/",
        "/jacek-adamas/",
        "/terroir-and-traditions/",
        "/anna-konik/",
        "/gotong-royong/",
        "/snucie/",
        "/uncensored/",
        "/collection-co–selection/"
    ]
    
    print("🧪 Тестуємо логування переходів на сторінки...")
    
    for page in test_pages:
        try:
            print(f"\n📄 Тестуємо сторінку: {page}")
            
            # Робимо запит на сторінку
            response = requests.get(f"{base_url}{page}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Сторінка {page} завантажена успішно")
                print(f"📊 Розмір відповіді: {len(response.content)} байт")
            else:
                print(f"❌ Помилка завантаження {page}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Помилка при тестуванні {page}: {e}")
        
        # Затримка між запитами
        time.sleep(1)
    
    print("\n🧪 Тестуємо сторінки з page_code...")
    
    # Тестуємо сторінки з page_code (замість реальних кодів використовуємо тестові)
    test_page_codes = [
        "test-page-1",
        "test-page-2", 
        "test-page-3"
    ]
    
    for page_code in test_page_codes:
        try:
            print(f"\n🔗 Тестуємо сторінку з page_code: {page_code}")
            
            # Робимо запит на головну сторінку з page_code
            response = requests.get(f"{base_url}/?page={page_code}", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Сторінка з page_code {page_code} завантажена успішно")
            else:
                print(f"❌ Помилка завантаження з page_code {page_code}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Помилка при тестуванні з page_code {page_code}: {e}")
        
        # Затримка між запитами
        time.sleep(1)
    
    print("\n✅ Тестування завершено!")
    print("📱 Перевірте Telegram бота для логів")

if __name__ == "__main__":
    test_logging()
