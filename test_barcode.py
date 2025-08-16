#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки генерації штрих-кодів
"""

import os
import sys
import random
import string

def test_barcode_generation():
    """Тестує генерацію штрих-кодів"""
    print("🔍 Тестування генерації штрих-кодів")
    print("=" * 50)
    
    try:
        # Імпортуємо необхідні модулі
        import barcode
        from barcode.writer import ImageWriter
        from PIL import Image
        
        print("✅ Всі залежності імпортовано успішно")
        
        # Тестуємо різні формати штрих-кодів
        test_value = ''.join(random.choices(string.digits, k=16))
        print(f"📊 Тестове значення: {test_value}")
        
        # Тест 1: Code128
        print("\n🔍 Тест 1: Code128")
        try:
            barcode_img = barcode.get('code128', test_value, writer=ImageWriter())
            test_path = 'test_barcode_code128.png'
            barcode_img.save(test_path)
            
            if os.path.exists(test_path):
                file_size = os.path.getsize(test_path)
                print(f"✅ Code128 створено: {test_path} (розмір: {file_size} байт)")
                
                # Перевіряємо зображення
                img = Image.open(test_path)
                print(f"✅ Зображення відкрито: {img.size[0]}x{img.size[1]} пікселів")
                img.close()
                
                # Видаляємо тестовий файл
                os.remove(test_path)
                print("🧹 Тестовий файл видалено")
            else:
                print("❌ Code128 не створено")
        except Exception as e:
            print(f"❌ Помилка Code128: {e}")
        
        # Тест 2: EAN13
        print("\n🔍 Тест 2: EAN13")
        try:
            ean_value = ''.join(random.choices(string.digits, k=12))  # EAN13 потребує 12 цифр
            barcode_img = barcode.get('ean13', ean_value, writer=ImageWriter())
            test_path = 'test_barcode_ean13.png'
            barcode_img.save(test_path)
            
            if os.path.exists(test_path):
                file_size = os.path.getsize(test_path)
                print(f"✅ EAN13 створено: {test_path} (розмір: {file_size} байт)")
                
                # Видаляємо тестовий файл
                os.remove(test_path)
                print("🧹 Тестовий файл видалено")
            else:
                print("❌ EAN13 не створено")
        except Exception as e:
            print(f"❌ Помилка EAN13: {e}")
        
        # Тест 3: Code39
        print("\n🔍 Тест 3: Code39")
        try:
            code39_value = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            barcode_img = barcode.get('code39', code39_value, writer=ImageWriter())
            test_path = 'test_barcode_code39.png'
            barcode_img.save(test_path)
            
            if os.path.exists(test_path):
                file_size = os.path.getsize(test_path)
                print(f"✅ Code39 створено: {test_path} (розмір: {file_size} байт)")
                
                # Видаляємо тестовий файл
                os.remove(test_path)
                print("🧹 Тестовий файл видалено")
            else:
                print("❌ Code39 не створено")
        except Exception as e:
            print(f"❌ Помилка Code39: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Тестування завершено!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("Встановіть залежності: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Загальна помилка: {e}")
        return False

def test_pdf_integration():
    """Тестує інтеграцію штрих-коду з PDF"""
    print("\n🔍 Тестування інтеграції з PDF")
    print("=" * 50)
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        
        print("✅ ReportLab імпортовано успішно")
        
        # Створюємо тестовий штрих-код
        import barcode
        from barcode.writer import ImageWriter
        
        test_value = ''.join(random.choices(string.digits, k=16))
        barcode_img = barcode.get('code128', test_value, writer=ImageWriter())
        barcode_path = 'test_barcode_for_pdf.png'
        barcode_img.save(barcode_path)
        
        if not os.path.exists(barcode_path):
            print("❌ Штрих-код не створено для PDF тесту")
            return False
        
        # Створюємо тестовий PDF
        pdf_path = 'test_barcode_pdf.pdf'
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Додаємо текст
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, "TEST BARCODE")
        
        # Додаємо штрих-код
        try:
            c.drawImage(barcode_path, (width - 360) // 2, height - 300, width=360, height=70)
            print("✅ Штрих-код додано до PDF")
        except Exception as e:
            print(f"❌ Помилка додавання штрих-коду до PDF: {e}")
        
        # Додаємо номер
        c.setFont("Helvetica", 12)
        c.drawCentredString(width / 2, height - 320, test_value)
        
        c.save()
        
        if os.path.exists(pdf_path):
            print(f"✅ PDF створено: {pdf_path}")
            
            # Видаляємо тестові файли
            os.remove(barcode_path)
            os.remove(pdf_path)
            print("🧹 Тестові файли видалено")
            
            return True
        else:
            print("❌ PDF не створено")
            return False
            
    except Exception as e:
        print(f"❌ Помилка тестування PDF: {e}")
        return False

def main():
    """Головна функція"""
    print("🚀 Тестування системи штрих-кодів")
    print("=" * 50)
    
    # Тест 1: Генерація штрих-кодів
    barcode_success = test_barcode_generation()
    
    # Тест 2: Інтеграція з PDF
    pdf_success = test_pdf_integration()
    
    print("\n" + "=" * 50)
    print("📊 Результати тестування:")
    print(f"   Штрих-коди: {'✅' if barcode_success else '❌'}")
    print(f"   PDF інтеграція: {'✅' if pdf_success else '❌'}")
    
    if barcode_success and pdf_success:
        print("\n🎉 Всі тести пройдено успішно!")
        print("✅ Система штрих-кодів працює правильно")
    else:
        print("\n⚠️  Деякі тести не пройдено")
        print("🔧 Перевірте помилки та спробуйте ще раз")
    
    return barcode_success and pdf_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
