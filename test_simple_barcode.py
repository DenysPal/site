#!/usr/bin/env python3
"""
Простий тест нового штрих-коду
"""

import os
import random
import string
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def test_simple_barcode():
    """Тестує простий штрих-код"""
    print("🔍 Тестування простого штрих-коду")
    print("=" * 50)
    
    # Створюємо тестовий PDF
    pdf_path = 'test_simple_barcode.pdf'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Додаємо тестовий контент
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "TEST SIMPLE BARCODE")
    
    # Додаємо домен
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(width / 2, height - 150, "artpullse.com")
    
    # Генеруємо номер штрих-коду
    barcode_value = ''.join(random.choices(string.digits, k=16))
    print(f"🔍 Штрих-код (текст): {barcode_value}")
    
    # Малюємо простий штрих-код (прямокутник з текстом)
    barcode_y = height - 300
    print(f"🔍 Малюємо простий штрих-код на позиції y={barcode_y}")
    
    # Малюємо прямокутник як штрих-код
    c.setFillColorRGB(0, 0, 0)  # Чорний колір
    c.rect((width - 360) // 2, barcode_y, 360, 70, fill=1)
    
    # Малюємо білі смужки всередині (як штрих-код)
    c.setFillColorRGB(1, 1, 1)  # Білий колір
    stripe_width = 8
    stripe_spacing = 12
    start_x = (width - 360) // 2 + 20
    
    for i in range(20):  # 20 смужок
        x = start_x + i * stripe_spacing
        c.rect(x, barcode_y + 10, stripe_width, 50, fill=1)
    
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
        web_path = 'artpullse.com/file/ticket/test_simple_barcode.pdf'
        try:
            import shutil
            os.makedirs('artpullse.com/file/ticket', exist_ok=True)
            shutil.copy2(pdf_path, web_path)
            print(f"✅ PDF скопійовано у веб-папку: {web_path}")
        except Exception as e:
            print(f"⚠️  Помилка копіювання: {e}")
        
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
    print("🚀 Тест простого штрих-коду")
    print("=" * 50)
    
    if test_simple_barcode():
        print("\n✅ Тест пройдено успішно!")
        print("🎯 Тепер штрих-код має відображатися як чорний прямокутник з білими смужками")
    else:
        print("\n❌ Тест не вдався")

if __name__ == "__main__":
    main()
