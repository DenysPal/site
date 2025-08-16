#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки логіки квитків
"""

def validate_ticket_data(name, time, date, price, address):
    """Валідація даних квитка - гнучка версія"""
    print(f"🔍 [VALIDATION] Валідація даних: name='{name}', time='{time}', date='{date}', price='{price}', address='{address}'")
    
    errors = []
    
    # Перевіряємо тільки базові речі
    if not name or len(name.strip()) < 1:
        errors.append("❌ Ім'я не може бути порожнім")
        print(f"🔍 [VALIDATION] Помилка імені: '{name}'")
    
    if not time or len(time.strip()) < 1:
        errors.append("❌ Час не може бути порожнім")
        print(f"🔍 [VALIDATION] Помилка часу: '{time}'")
    
    if not date or len(date.strip()) < 1:
        errors.append("❌ Дата не може бути порожньою")
        print(f"🔍 [VALIDATION] Помилка дати: '{date}'")
    
    if not price or len(price.strip()) < 1:
        errors.append("❌ Ціна не може бути порожньою")
        print(f"🔍 [VALIDATION] Помилка ціни: '{price}'")
    
    if not address or len(address.strip()) < 1:
        errors.append("❌ Адрес не може бути порожнім")
        print(f"🔍 [VALIDATION] Помилка адресу: '{address}'")
    
    print(f"🔍 [VALIDATION] Результат: {errors}")
    return errors

def test_ticket_processing():
    """Тестує обробку даних квитка"""
    print("🔍 Тестування обробки даних квитка")
    print("=" * 50)
    
    # Тест 1: Дані як у скріншоті
    print("\n✅ Тест 1: Дані як у скріншоті")
    test_text = """1. LEL
2. 20.20
3. 20.20
4. 54sdd
5. ddd"""
    
    print(f"📝 Вхідний текст:\n{test_text}")
    
    # Обробка тексту як у боті
    lines = [l.strip() for l in test_text.split('\n') if l.strip()]
    print(f"🔍 Рядки: {lines}")
    print(f"🔍 Кількість рядків: {len(lines)}")
    
    if len(lines) < 5:
        print("❌ Недостатньо рядків")
        return False
    
    try:
        name, time, date, price, address = lines[:5]
        print(f"🔍 Розпарсені дані: name='{name}', time='{time}', date='{date}', price='{price}', address='{address}'")
        
        # Валідація
        validation_errors = validate_ticket_data(name, time, date, price, address)
        
        if validation_errors:
            print("❌ Помилки валідації:")
            for error in validation_errors:
                print(f"   {error}")
            return False
        else:
            print("✅ Валідація пройшла успішно!")
            return True
            
    except Exception as e:
        print(f"❌ Помилка обробки: {e}")
        return False

def test_different_formats():
    """Тестує різні формати даних"""
    print("\n✅ Тест 2: Різні формати даних")
    
    test_cases = [
        {
            'name': 'John Doe',
            'time': '21:30',
            'date': '25.12',
            'price': '100 €',
            'address': 'New York'
        },
        {
            'name': 'Test',
            'time': '15.45',
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

def main():
    """Головна функція"""
    print("🚀 Тестування логіки квитків")
    print("=" * 50)
    
    # Тест 1: Обробка даних
    success1 = test_ticket_processing()
    
    # Тест 2: Різні формати
    test_different_formats()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 Тестування завершено успішно!")
        print("✅ Логіка квитків працює правильно")
    else:
        print("❌ Тестування не пройшло")
        print("🔧 Перевірте помилки та спробуйте ще раз")

if __name__ == "__main__":
    main()
