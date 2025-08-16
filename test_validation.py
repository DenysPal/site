#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки валідації даних квитка
"""

def validate_ticket_data(name, time, date, price, address):
    """Валідація даних квитка - гнучка версія"""
    errors = []
    
    # Перевіряємо тільки базові речі
    if not name or len(name.strip()) < 1:
        errors.append("❌ Ім'я не може бути порожнім")
    
    if not time or len(time.strip()) < 1:
        errors.append("❌ Час не може бути порожнім")
    
    if not date or len(date.strip()) < 1:
        errors.append("❌ Дата не може бути порожньою")
    
    if not price or len(price.strip()) < 1:
        errors.append("❌ Ціна не може бути порожньою")
    
    if not address or len(address.strip()) < 1:
        errors.append("❌ Адрес не може бути порожнім")
    
    return errors

def test_validation():
    """Тестує різні варіанти даних"""
    print("🔍 Тестування валідації даних квитка")
    print("=" * 50)
    
    # Тест 1: Правильні дані
    print("\n✅ Тест 1: Правильні дані")
    test_data = {
        'name': 'LEL',
        'time': '20:20',
        'date': '20.20',
        'price': '40 €',
        'address': 'ddd'
    }
    
    errors = validate_ticket_data(**test_data)
    if not errors:
        print("✅ Валідація пройшла успішно")
    else:
        print("❌ Помилки валідації:")
        for error in errors:
            print(f"   {error}")
    
    # Тест 2: Дані як у скріншоті
    print("\n✅ Тест 2: Дані як у скріншоті")
    test_data = {
        'name': 'LEL',
        'time': '20.20',  # Неправильний формат, але тепер приймається
        'date': '20.20',
        'price': '54sdd',  # Неправильний формат, але тепер приймається
        'address': 'ddd'
    }
    
    errors = validate_ticket_data(**test_data)
    if not errors:
        print("✅ Валідація пройшла успішно")
    else:
        print("❌ Помилки валідації:")
        for error in errors:
            print(f"   {error}")
    
    # Тест 3: Порожні дані
    print("\n❌ Тест 3: Порожні дані")
    test_data = {
        'name': '',
        'time': '',
        'date': '',
        'price': '',
        'address': ''
    }
    
    errors = validate_ticket_data(**test_data)
    if errors:
        print("✅ Валідація правильно знайшла помилки:")
        for error in errors:
            print(f"   {error}")
    else:
        print("❌ Валідація не знайшла помилки в порожніх даних")
    
    # Тест 4: Різні формати
    print("\n✅ Тест 4: Різні формати даних")
    test_cases = [
        {
            'name': 'John Doe',
            'time': '21:30',
            'date': '25.12',
            'price': '100$',
            'address': 'New York'
        },
        {
            'name': 'Test',
            'time': '15.45',  # Неправильний формат, але тепер приймається
            'date': '01.01',
            'price': '50₴',
            'address': 'Kyiv'
        },
        {
            'name': 'User',
            'time': '12:00',
            'date': '31.12',
            'price': '200₽',
            'address': 'Moscow'
        }
    ]
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n   Підтест {i}:")
        errors = validate_ticket_data(**test_data)
        if not errors:
            print("   ✅ Валідація пройшла")
        else:
            print("   ❌ Помилки:")
            for error in errors:
                print(f"      {error}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестування завершено!")

def main():
    """Головна функція"""
    test_validation()

if __name__ == "__main__":
    main()
