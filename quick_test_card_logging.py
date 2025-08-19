#!/usr/bin/env python3
"""
Швидкий тест логування сторінки введення карти
"""

def test_page_name_detection():
    """Тестує визначення назви сторінки"""
    
    # Імітуємо функцію get_page_name_from_url
    def get_page_name_from_url(url_path, page_code=None):
        if '/buy-tickets/' in url_path:
            if '/loading/' in url_path:
                return "Ввод карты"
            elif '/code/' in url_path:
                return "Оформлення замовлення (код)"
            elif '/quantity/' in url_path:
                return "Оформлення замовлення (кількість)"
            elif '/payment/' in url_path:
                return "Оформлення замовлення (оплата)"
            else:
                return "Оформлення замовлення"
        return "Невідома сторінка"
    
    # Тестуємо різні URL
    test_cases = [
        ("/buy-tickets/loading/", "Ввод карты"),
        ("/buy-tickets/code/", "Оформлення замовлення (код)"),
        ("/buy-tickets/quantity/", "Оформлення замовлення (кількість)"),
        ("/buy-tickets/payment/", "Оформлення замовлення (оплата)"),
        ("/buy-tickets/", "Оформлення замовлення"),
        ("/other-page/", "Невідома сторінка")
    ]
    
    print("🧪 Тестування визначення назв сторінок...")
    
    for url, expected in test_cases:
        result = get_page_name_from_url(url)
        status = "✅" if result == expected else "❌"
        print(f"{status} {url} → {result}")
        
        if result != expected:
            print(f"   Очікувалось: {expected}")
    
    print("\n📋 Формат повідомлення для 'Ввод карты':")
    print("🔔Мамонт открыл страницу (Ввод карты)")
    print("📎Страница: Ввод карты")
    print("#️⃣Ссылка: ?page=2-37")
    print("📶IP: 37.52.215.105")
    print("🌎Страна: UA")

if __name__ == "__main__":
    test_page_name_detection()
