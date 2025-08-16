#!/usr/bin/env python3
"""
Використання існуючого штрих-коду в квитках
"""

import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def create_ticket_with_existing_barcode():
    """Створює квиток з існуючим штрих-кодом"""
    print("🔍 Створення квитка з існуючим штрих-коду")
    print("=" * 50)
    
    # Шлях до існуючого штрих-коду
    existing_barcode = 'existing_barcode.png'  # Тут має бути ваш штрих-код
    
    if not os.path.exists(existing_barcode):
        print(f"❌ Файл штрих-коду не знайдено: {existing_barcode}")
        print("💡 Збережіть ваш штрих-код як 'existing_barcode.png' в поточній папці")
        return False
    
    # Створюємо тестовий PDF
    pdf_path = 'ticket_with_existing_barcode.pdf'
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Додаємо тестовий контент
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 100, "TICKET WITH EXISTING BARCODE")
    
    # Додаємо домен
    c.setFont("Helvetica-Bold", 20)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(width / 2, height - 150, "artpullse.com")
    
    # Додаємо зображення (якщо є)
    image_path = os.path.join('events-art.com', 'image', 'vine.webp')
    if os.path.exists(image_path):
        try:
            from reportlab.platypus import Image
            img = Image(image_path, width=200, height=100)
            img.drawOn(c, (width - 200) // 2, height - 250)
            print(f"✅ Додано зображення: {image_path}")
        except Exception as e:
            print(f"⚠️  Помилка завантаження зображення: {e}")
    
    # Додаємо інформацію про квиток
    info_y = height - 350
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, info_y, "PRICE: 54sdd")
    c.drawCentredString(width / 2, info_y - 25, "DATE: 20.20")
    c.drawCentredString(width / 2, info_y - 50, "TIME: 20.20")
    c.drawCentredString(width / 2, info_y - 75, "Location: ddd")
    
    # Пунктирна лінія
    line_y = info_y - 100
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(1)
    c.line(50, line_y, width - 50, line_y)
    
    # Малюємо існуючий штрих-код
    barcode_y = line_y - 100
    print(f"🔍 Малюємо існуючий штрих-код на позиції y={barcode_y}")
    
    try:
        # Малюємо існуючий штрих-код
        c.drawImage(existing_barcode, (width - 360) // 2, barcode_y, width=360, height=70)
        print(f"✅ Штрих-код додано з файлу: {existing_barcode}")
    except Exception as e:
        print(f"❌ Помилка малювання штрих-коду: {e}")
        # Fallback на простий прямокутник
        c.setFillColorRGB(0, 0, 0)
        c.rect((width - 360) // 2, barcode_y, 360, 70, fill=1)
    
    # Номер штрих-коду (можна змінити на будь-який)
    barcode_value = "1234567890123456"
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, barcode_y - 18, barcode_value)
    
    c.save()
    
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✅ PDF створено: {pdf_path} (розмір: {file_size} байт)")
        
        # Копіюємо у веб-папку для тестування
        web_path = 'artpullse.com/file/ticket/ticket_with_existing_barcode.pdf'
        try:
            os.makedirs('artpullse.com/file/ticket', exist_ok=True)
            shutil.copy2(pdf_path, web_path)
            print(f"✅ PDF скопійовано у веб-папку: {web_path}")
        except Exception as e:
            print(f"⚠️  Помилка копіювання: {e}")
        
        print(f"\n🎯 Квиток з існуючим штрих-кодом створено!")
        print(f"📁 Локальний файл: {pdf_path}")
        print(f"🌐 Веб-файл: {web_path}")
        print(f"🔢 Номер: {barcode_value}")
        
        return True
    else:
        print("❌ PDF не створено")
        return False

def main():
    """Головна функція"""
    print("🚀 Використання існуючого штрих-коду в квитках")
    print("=" * 50)
    
    if create_ticket_with_existing_barcode():
        print("\n✅ Квиток створено успішно!")
        print("🔍 Перевірте файл ticket_with_existing_barcode.pdf")
    else:
        print("\n❌ Квиток не створено")

if __name__ == "__main__":
    main()
