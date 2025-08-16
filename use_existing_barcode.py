#!/usr/bin/env python3
"""
Використання існуючого штрих-коду в квитках
"""

import os
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import ImageReader

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
    
    # Генерируем PDF
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
            # Малюємо повністю сірий прямокутник для всього білета
        c.setFillColorRGB(0.9, 0.9, 0.9)  # Сірий колір
        c.rect(0, 0, width, height, fill=1)
        
        # Білий прямокутник всередині сірого
        c.setFillColorRGB(1, 1, 1)  # Білий колір
        c.rect(20, 20, width - 40, height - 40, fill=1)
    
            # Верхний домен по центру, серым (опускаємо нижче для рамки)
        top_y = height - 60
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(0.7, 0.7, 0.7)
        c.drawCentredString(width / 2, top_y, "artpullse.com")
    
    # Имя крупно по центру
    name_y = top_y - 35
    c.setFont("Helvetica-Bold", 24)
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(width / 2, name_y, "TICKET WITH EXISTING BARCODE")
    
    # Картинка по центру
    img_bottom_y = name_y - 40
            image_path = os.path.join('afisha-events.com', 'image', '_dsf0493_ko_lekcja_3000px_auto_1400x800.webp')
    if os.path.exists(image_path):
        try:
            img = ImageReader(image_path)
            max_w = int(width - 140)
            max_h = 280
            img.thumbnail((max_w, max_h))
            img_w, img_h = img.size
            img_x = (width - img_w) / 2
            img_y = img_bottom_y - img_h
            img_io = ImageReader(img)
            c.drawImage(img_io, img_x, img_y, width=img_w, height=img_h)
            print(f"✅ Додано зображення: {os.path.basename(image_path)}")
        except Exception as e:
            print(f"⚠️  Помилка завантаження зображення: {e}")
            img_y = img_bottom_y
            img_h = 0
    else:
        img_y = img_bottom_y
        img_h = 0
    
    # Блок с тремя колонками PRICE / DATE / TIME
    row_top_y = (img_y if img_h == 0 else img_y) - 20
    label_y = row_top_y
    value_y = label_y - 16
    col_centers = [width * (1/6), width * (3/6), width * (5/6)]
    labels = ["PRICE", "DATE", "TIME"]
    values = ["40 €", "23.05", "21:00"]
    
    c.setFont("Helvetica", 10)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    for i, x in enumerate(col_centers):
        c.drawCentredString(x, label_y, labels[i])
    
    c.setFont("Helvetica-Bold", 14)
    c.setFillColorRGB(0, 0, 0)
    for i, x in enumerate(col_centers):
        c.drawCentredString(x, value_y, values[i])
    
    # Location по центру (як на другому скріншоті)
    loc_y = value_y - 28
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, loc_y, "Location: ?????")
    
    # Пунктирна лінія
    line_y = loc_y - 30
    c.setStrokeColor(colors.grey)
    c.setLineWidth(1)
    try:
        c.setDash(1, 3)
    except Exception:
        pass
    c.line(50, line_y, width - 50, line_y)
    
    # Штрих-код (як на першому скріншоті - з сірою рамкою)
    barcode_y = line_y - 20
    print(f"🔍 Малюємо існуючий штрих-код на позиції y={barcode_y}")
    
    try:
        # Малюємо сіру рамку для штрих-коду (як на першому скріншоті)
        c.setFillColorRGB(0.9, 0.9, 0.9)  # Сірий колір
        c.rect((width - 600) // 2, barcode_y - 10, 600, 160, fill=1)
        
        # Малюємо існуючий штрих-код
        c.drawImage(existing_barcode, (width - 600) // 2, barcode_y, width=600, height=160)
        print(f"✅ Штрих-код додано з файлу: {existing_barcode}")
    except Exception as e:
        print(f"❌ Помилка малювання штрих-коду: {e}")
    
    # Номер штрих-коду (як на другому скріншоті)
    barcode_value = "1234567890123456"
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, barcode_y - 18, barcode_value)
    
    # Додаємо фото image.png знизу (замість QR-коду)
    bottom_image_path = os.path.join('events-art.com', 'image', 'image.png')
    bottom_image_y = barcode_y - 200  # Розташовуємо фото вище штрих-коду
    
    if os.path.exists(bottom_image_path):
        try:
            # Малюємо фото image.png (розмір 150x150)
            c.drawImage(bottom_image_path, (width - 150) // 2, bottom_image_y, width=150, height=150)
            print(f"✅ Фото image.png додано з файлу: {bottom_image_path}")
        except Exception as e:
            print(f"❌ Помилка малювання фото image.png: {e}")
    else:
        print(f"⚠️ Фото image.png не знайдено: {bottom_image_path}")
    
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
