#!/usr/bin/env python3
"""
Демонстраційний скрипт генерації квитка
Показує, як працює система без запуску Telegram бота
"""

import os
import sys
import random
import string
import shutil
from pathlib import Path

# Додаємо поточну директорію до шляху для імпорту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_demo_ticket():
    """Створює демонстраційний квиток"""
    print("🎫 Демонстрація генерації квитка")
    print("=" * 40)
    
    # Тестові дані
    demo_data = {
        'name': 'Іван Петренко',
        'time': '21:00',
        'date': '23.05',
        'price': '40 €',
        'address': 'Київ, Музей сучасного мистецтва'
    }
    
    print("📋 Тестові дані:")
    for key, value in demo_data.items():
        print(f"   {key}: {value}")
    
    try:
        # Імпортуємо необхідні модулі
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from reportlab.lib import colors
        from PIL import Image
        import barcode
        from barcode.writer import ImageWriter
        
        # Створюємо папки
        os.makedirs('tickets', exist_ok=True)
        os.makedirs('artpullse.com/file/ticket', exist_ok=True)
        
        # Генерируем унікальний ID
        order_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        pdf_filename = f"demo_order_{order_id}.pdf"
        pdf_path = os.path.join('tickets', pdf_filename)
        
        print(f"\n🆔 Order ID: {order_id}")
        print(f"📄 PDF файл: {pdf_filename}")
        
        # Генерируем штрих-код з покращеною обробкою помилок
        # Використовуємо готовий штрих-код
        barcode_value = ''.join(random.choices(string.digits, k=16))
        print(f"🔍 [DEMO] Використовуємо готовий штрих-код: {barcode_value}")
        
        # Шлях до готового штрих-коду
        barcode_path = os.path.join('events-art.com', 'image', 'existing_barcode.png')
        
        if not os.path.exists(barcode_path):
            print(f"⚠️  Готовий штрих-код не знайдено: {barcode_path}")
            print("💡 Збережіть ваш штрих-код як 'existing_barcode.png' в папці events-art.com/image/")
            barcode_path = None
        else:
            print(f"✅ Готовий штрих-код знайдено: {barcode_path}")
        
        # Шукаємо зображення - використовуємо dried_plant_root.png (висушена рослина/корінь з пурпуровим освітленням)
        image_dir = 'events-art.com/image'
        img_path = os.path.join(image_dir, 'dried_plant_root.png')
        
        if not os.path.exists(img_path):
            print("⚠️  Основне зображення dried_plant_root.png не знайдено, шукаємо запасні варіанти")
            candidate_images = [
                'vine.webp',  # Стара картинка як запасна
                'zdj49_auto_1400x800.webp',
                'zdj36_auto_1400x800.webp',
                'zdj51_auto_1400x800.webp',
                'zdj57_auto_1400x800.webp',
                'strona-csw403_auto_1400x800.webp',
                'news_5_1.jpg',
                'news_6_1.webp'
            ]
            
            for img_name in candidate_images:
                full_path = os.path.join(image_dir, img_name)
                if os.path.exists(full_path):
                    img_path = full_path
                    break
            
            if img_path is None:
                print("⚠️  Зображення не знайдено, створюємо квиток без зображення")
                img_path = None
        
        # Створюємо PDF
        print("\n🔄 Створення PDF...")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Заголовок
        top_y = height - 40
        c.setFont("Helvetica-Bold", 20)
        c.setFillColorRGB(0.7, 0.7, 0.7)
        c.drawCentredString(width / 2, top_y, "artpullse.com")
        
        # Ім'я
        name_y = top_y - 35
        c.setFont("Helvetica-Bold", 24)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(width / 2, name_y, demo_data['name'])
        
        # Зображення (якщо є)
        img_bottom_y = name_y - 40
        if img_path and os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                max_w = int(width - 140)
                max_h = 280
                img.thumbnail((max_w, max_h))
                img_w, img_h = img.size
                img_x = (width - img_w) / 2
                img_y = img_bottom_y - img_h
                img_io = ImageReader(img)
                c.drawImage(img_io, img_x, img_y, width=img_w, height=img_h)
                print(f"✅ Додано зображення: {os.path.basename(img_path)}")
            except Exception as e:
                print(f"⚠️  Помилка завантаження зображення: {e}")
                img_y = img_bottom_y
                img_h = 0
        else:
            img_y = img_bottom_y
            img_h = 0
        
        # Інформація PRICE / DATE / TIME
        row_top_y = (img_y if img_h == 0 else img_y) - 20
        label_y = row_top_y
        value_y = label_y - 16
        col_centers = [width * (1/6), width * (3/6), width * (5/6)]
        labels = ["PRICE", "DATE", "TIME"]
        values = [demo_data['price'], demo_data['date'], demo_data['time']]
        
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.35, 0.35, 0.35)
        for i, x in enumerate(col_centers):
            c.drawCentredString(x, label_y, labels[i])
        
        c.setFont("Helvetica-Bold", 14)
        c.setFillColorRGB(0, 0, 0)
        for i, x in enumerate(col_centers):
            c.drawCentredString(x, value_y, values[i])
        
        # Локація
        loc_y = value_y - 28
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, loc_y, f"Location: {demo_data['address']}")
        
        # Пунктирна лінія
        line_y = loc_y - 30
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        try:
            c.setDash(1, 3)
        except Exception:
            pass
        c.line(50, line_y, width - 50, line_y)
        
        # Штрих-код
        barcode_y = line_y - 80
        try:
            c.setDash()
        except Exception:
            pass
        
        # Малюємо штрих-код
        print(f"🔍 [DEMO] Малюємо штрих-код")
        
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
        
        # Зберігаємо PDF
        c.save()
        print("✅ PDF створено успішно")
        
        # Копіюємо у веб-доступну папку
        public_pdf_path = os.path.join('artpullse.com', 'file', 'ticket', pdf_filename)
        try:
            shutil.copy2(pdf_path, public_pdf_path)
            print("✅ PDF скопійовано у веб-папку")
        except Exception as e:
            print(f"⚠️  Помилка копіювання: {e}")
        
        # Формуємо посилання
        ticket_url = f"https://artpullse.com/file/ticket/{pdf_filename}"
        
        print("\n🎉 Квиток створено успішно!")
        print(f"📁 Локальний файл: {pdf_path}")
        print(f"🌐 Веб-посилання: {ticket_url}")
        
        # Готовий штрих-код не видаляємо, оскільки він постійний
        print(f"🔍 [DEMO] Готовий штрих-код залишається: {barcode_path}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Помилка імпорту: {e}")
        print("Встановіть залежності: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Помилка створення квитка: {e}")
        return False

def main():
    """Головна функція"""
    print("🚀 Демонстрація системи генерації квитків")
    print("=" * 50)
    
    if create_demo_ticket():
        print("\n✅ Демонстрація завершена успішно!")
        print("🎯 Тепер ви можете використовувати систему через Telegram бота")
    else:
        print("\n❌ Демонстрація не вдалася")
        print("🔧 Перевірте помилки та спробуйте ще раз")

if __name__ == "__main__":
    main()
