#!/usr/bin/env python3
"""
Тест справжнього штрих-коду
"""

import os
import random
import string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def test_real_barcode():
    """Тестує справжній штрих-код"""
    print("🔍 Тестування справжнього штрих-коду")
    print("=" * 50)
    
    # Створюємо тестовий PDF
    pdf_path = 'test_real_barcode.pdf'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Додаємо тестовий контент
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "TEST REAL BARCODE")
    
    # Додаємо домен
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(width / 2, height - 150, "artpullse.com")
    
    # Генеруємо номер штрих-коду
    barcode_value = ''.join(random.choices(string.digits, k=16))
    print(f"🔍 Генеруємо штрих-код: {barcode_value}")
    
    # Створюємо справжній штрих-код
    barcode_path = None
    try:
        import barcode
        from barcode.writer import ImageWriter
        
        # Створюємо штрих-код
        barcode_img = barcode.get('code128', barcode_value, writer=ImageWriter())
        barcode_path = 'test_barcode.png'
        barcode_img.save(barcode_path)
        print(f"✅ Штрих-код створено: {barcode_path}")
        
    except Exception as e:
        print(f"❌ Помилка створення штрих-коду: {e}")
        barcode_path = None
    
    # Малюємо штрих-код
    barcode_y = height - 300
    print(f"🔍 Малюємо штрих-код на позиції y={barcode_y}")
    
    if barcode_path and os.path.exists(barcode_path):
        try:
            # Малюємо згенерований штрих-код
            c.drawImage(barcode_path, (width - 360) // 2, barcode_y, width=360, height=70)
            print(f"✅ Штрих-код додано з файлу: {barcode_path}")
        except Exception as e:
            print(f"❌ Помилка малювання штрих-коду: {e}")
            # Fallback на простий прямокутник
            c.setFillColorRGB(0, 0, 0)
            c.rect((width - 360) // 2, barcode_y, 360, 70, fill=1)
    else:
        print(f"⚠️  Файл штрих-коду не знайдено, малюємо простий прямокутник")
        # Fallback на простий прямокутник
        c.setFillColorRGB(0, 0, 0)
        c.rect((width - 360) // 2, barcode_y, 360, 70, fill=1)
    
    # Повертаємо чорний колір для тексту
    c.setFillColorRGB(0, 0, 0)
    
    # Номер штрих-коду
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, barcode_y - 18, barcode_value)
    
    c.save()
    
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✅ PDF створено: {pdf_path} (розмір: {file_size} байт)")
        
        # Копіюємо у веб-папку для тестування
        web_path = 'artpullse.com/file/ticket/test_real_barcode.pdf'
        try:
            import shutil
            os.makedirs('artpullse.com/file/ticket', exist_ok=True)
            shutil.copy2(pdf_path, web_path)
            print(f"✅ PDF скопійовано у веб-папку: {web_path}")
        except Exception as e:
            print(f"⚠️  Помилка копіювання: {e}")
        
        # Видаляємо тимчасовий штрих-код
        try:
            if barcode_path and os.path.exists(barcode_path):
                os.remove(barcode_path)
                print("🧹 Тимчасовий штрих-код видалено")
        except Exception as e:
            print(f"⚠️  Помилка видалення штрих-коду: {e}")
        
        print(f"\n🎯 Тестовий штрих-код створено!")
        print(f"📁 Локальний файл: {pdf_path}")
        print(f"🌐 Веб-файл: {web_path}")
        print(f"🔢 Номер: {barcode_value}")
        
        return True
    else:
        print("❌ PDF не створено")
        return False

def main():
    """Головна функція"""
    print("🚀 Тест справжнього штрих-коду")
    print("=" * 50)
    
    if test_real_barcode():
        print("\n✅ Тест пройдено успішно!")
        print("🎯 Тепер штрих-код має виглядати як справжній!")
        print("🔍 Перевірте файл test_real_barcode.pdf")
    else:
        print("\n❌ Тест не вдався")

if __name__ == "__main__":
    main()
