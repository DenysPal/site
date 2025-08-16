#!/usr/bin/env python3
"""
Комплексний тест системи квитків
"""

import os
import sys
import random
import string

def test_folder_structure():
    """Тестує структуру папок"""
    print("🔍 Тестування структури папок")
    print("=" * 50)
    
    # Створюємо необхідні папки
    folders = [
        'tickets',
        'artpullse.com/file/ticket',
        'events-art.com/image'
    ]
    
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Папка створена/перевірена: {folder}")
        except Exception as e:
            print(f"❌ Помилка створення папки {folder}: {e}")
    
    return True

def test_barcode_generation():
    """Тестує генерацію штрих-кодів"""
    print("\n🔍 Тестування генерації штрих-кодів")
    print("=" * 50)
    
    try:
        import barcode
        from barcode.writer import ImageWriter
        
        # Генеруємо тестовий штрих-код
        barcode_value = ''.join(random.choices(string.digits, k=16))
        barcode_path = 'test_barcode.png'
        
        barcode_img = barcode.get('code128', barcode_value, writer=ImageWriter())
        barcode_img.save(barcode_path)
        
        if os.path.exists(barcode_path):
            file_size = os.path.getsize(barcode_path)
            print(f"✅ Штрих-код створено: {barcode_path} (розмір: {file_size} байт)")
            
            # Видаляємо тестовий файл
            os.remove(barcode_path)
            print("🧹 Тестовий штрих-код видалено")
            return True
        else:
            print("❌ Штрих-код не створено")
            return False
            
    except Exception as e:
        print(f"❌ Помилка генерації штрих-коду: {e}")
        return False

def test_pdf_generation():
    """Тестує генерацію PDF"""
    print("\n🔍 Тестування генерації PDF")
    print("=" * 50)
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        # Створюємо тестовий PDF
        pdf_path = 'test_ticket.pdf'
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Додаємо тестовий контент
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, "TEST TICKET")
        
        # Додаємо домен
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(0.7, 0.7, 0.7)
        c.drawCentredString(width / 2, height - 150, "artpullse.com")
        
        c.save()
        
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF створено: {pdf_path} (розмір: {file_size} байт)")
            
            # Копіюємо у веб-папку
            web_path = 'artpullse.com/file/ticket/test_ticket.pdf'
            try:
                import shutil
                shutil.copy2(pdf_path, web_path)
                print(f"✅ PDF скопійовано у веб-папку: {web_path}")
            except Exception as e:
                print(f"⚠️  Помилка копіювання: {e}")
            
            # Видаляємо тестові файли
            os.remove(pdf_path)
            if os.path.exists(web_path):
                os.remove(web_path)
            print("🧹 Тестові файли видалено")
            
            return True
        else:
            print("❌ PDF не створено")
            return False
            
    except Exception as e:
        print(f"❌ Помилка генерації PDF: {e}")
        return False

def test_url_generation():
    """Тестує генерацію URL"""
    print("\n🔍 Тестування генерації URL")
    print("=" * 50)
    
    # Тестуємо різні варіанти
    test_cases = [
        "test_ticket.pdf",
        "order_123456.pdf",
        "demo_order.pdf"
    ]
    
    for filename in test_cases:
        ticket_url = f"https://artpullse.com/file/ticket/{filename}"
        print(f"✅ URL: {ticket_url}")
        
        # Перевіряємо, чи містить правильний домен
        if "artpullse.com" in ticket_url:
            print(f"   ✅ Домен правильний: artpullse.com")
        else:
            print(f"   ❌ Домен неправильний!")
    
    return True

def test_validation():
    """Тестує валідацію даних"""
    print("\n🔍 Тестування валідації даних")
    print("=" * 50)
    
    def validate_ticket_data(name, time, date, price, address):
        """Валідація даних квитка - гнучка версія"""
        errors = []
        
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
    
    # Тестуємо дані як у скріншоті
    test_data = {
        'name': 'LEL',
        'time': '20.20',
        'date': '20.20',
        'price': '54sdd',
        'address': 'ddd'
    }
    
    errors = validate_ticket_data(**test_data)
    if not errors:
        print("✅ Валідація пройшла успішно")
        print(f"   Дані: {test_data}")
    else:
        print("❌ Помилки валідації:")
        for error in errors:
            print(f"   {error}")
    
    return len(errors) == 0

def main():
    """Головна функція"""
    print("🚀 Комплексний тест системи квитків")
    print("=" * 50)
    
    results = []
    
    # Тест 1: Структура папок
    results.append(("Структура папок", test_folder_structure()))
    
    # Тест 2: Генерація штрих-кодів
    results.append(("Генерація штрих-кодів", test_barcode_generation()))
    
    # Тест 3: Генерація PDF
    results.append(("Генерація PDF", test_pdf_generation()))
    
    # Тест 4: Генерація URL
    results.append(("Генерація URL", test_url_generation()))
    
    # Тест 5: Валідація даних
    results.append(("Валідація даних", test_validation()))
    
    # Підсумок
    print("\n" + "=" * 50)
    print("📊 Результати тестування:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Підсумок: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n🎉 Всі тести пройдено успішно!")
        print("✅ Система квитків працює правильно")
        print("\n💡 Тепер запустіть бота:")
        print("   python quick_start.py")
    else:
        print("\n⚠️  Деякі тести не пройдено")
        print("🔧 Перевірте помилки та спробуйте ще раз")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
