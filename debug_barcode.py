#!/usr/bin/env python3
"""
Діагностика штрих-коду
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def debug_barcode():
    """Діагностика штрих-коду"""
    print("🔍 Діагностика штрих-коду")
    print("=" * 50)
    
    # Створюємо тестовий PDF
    pdf_path = 'debug_barcode.pdf'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    print(f"📏 Розмір сторінки: {width} x {height}")
    
    # Додаємо заголовок
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "DEBUG BARCODE")
    
    # Тестуємо різні варіанти штрих-коду
    test_positions = [
        (height - 200, "Тест 1: Простий прямокутник"),
        (height - 300, "Тест 2: Прямокутник з смужками"),
        (height - 400, "Тест 3: Тільки смужки"),
        (height - 500, "Тест 4: Малий штрих-код")
    ]
    
    for i, (y_pos, description) in enumerate(test_positions):
        print(f"🔍 {description} на позиції y={y_pos}")
        
        # Тест 1: Простий прямокутник
        if i == 0:
            c.setFillColorRGB(0, 0, 0)  # Чорний
            c.rect(100, y_pos, 200, 50, fill=1)
            print(f"   ✅ Намальовано чорний прямокутник 200x50")
        
        # Тест 2: Прямокутник з смужками
        elif i == 1:
            c.setFillColorRGB(0, 0, 0)  # Чорний
            c.rect(100, y_pos, 200, 50, fill=1)
            c.setFillColorRGB(1, 1, 1)  # Білий
            for j in range(10):
                x = 110 + j * 18
                c.rect(x, y_pos + 5, 10, 40, fill=1)
            print(f"   ✅ Намальовано прямокутник з 10 білими смужками")
        
        # Тест 3: Тільки смужки
        elif i == 2:
            c.setFillColorRGB(0, 0, 0)  # Чорний
            for j in range(15):
                x = 100 + j * 15
                c.rect(x, y_pos, 8, 50, fill=1)
            print(f"   ✅ Намальовано 15 чорних смужок")
        
        # Тест 4: Малий штрих-код
        elif i == 3:
            c.setFillColorRGB(0, 0, 0)  # Чорний
            c.rect(100, y_pos, 150, 30, fill=1)
            c.setFillColorRGB(1, 1, 1)  # Білий
            for j in range(8):
                x = 110 + j * 16
                c.rect(x, y_pos + 5, 8, 20, fill=1)
            print(f"   ✅ Намальовано малий штрих-код 150x30")
        
        # Додаємо опис
        c.setFillColorRGB(0, 0, 0)  # Повертаємо чорний для тексту
        c.setFont("Helvetica", 10)
        c.drawString(320, y_pos + 20, description)
    
    # Зберігаємо PDF
    c.save()
    
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"\n✅ PDF створено: {pdf_path} (розмір: {file_size} байт)")
        print(f"📁 Шлях: {os.path.abspath(pdf_path)}")
        print(f"\n🎯 Відкрийте файл {pdf_path} та перевірте:")
        print(f"   - Чи є чорні прямокутники")
        print(f"   - Чи є білі смужки")
        print(f"   - Чи правильно розташовані елементи")
        return True
    else:
        print("❌ PDF не створено")
        return False

def main():
    """Головна функція"""
    print("🚀 Діагностика штрих-коду")
    print("=" * 50)
    
    if debug_barcode():
        print("\n✅ Діагностика завершена!")
        print("🔍 Перевірте файл debug_barcode.pdf")
    else:
        print("\n❌ Діагностика не вдалася")

if __name__ == "__main__":
    main()
