#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from PIL import Image

def test_ticket_creation():
    """Тест створення квитка"""
    print("🧪 Тестування створення квитка...")
    
    # Тестові дані
    name = "Test User"
    time = "21:00"
    date = "23.05"
    price = "40 €"
    address = "Test Address"
    
    try:
        # Перевіряємо наявність папок
        tickets_dir = "tickets"
        if not os.path.exists(tickets_dir):
            print(f"❌ Папка {tickets_dir} не існує")
            return False
        
        # Генерируем уникальный order_id
        order_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        pdf_filename = f"order_{order_id}.pdf"
        pdf_path = os.path.join(tickets_dir, pdf_filename)
        
        print(f"📄 Створюємо PDF: {pdf_path}")
        
        # Перевіряємо зображення
        img_path = os.path.join('events-art.com', 'image', '_dsf0493_ko_lekcja_3000px_auto_1400x800.webp')
        if not os.path.exists(img_path):
            print(f"⚠️ Основне зображення не знайдено: {img_path}")
            # Шукаємо запасні варіанти
            candidate_images = [
                os.path.join('events-art.com', 'image', 'vine.webp'),
                os.path.join('events-art.com', 'image', 'news_5_1.jpg'),
                os.path.join('events-art.com', 'image', 'header-image.jpg'),
            ]
            
            for p in candidate_images:
                if os.path.exists(p):
                    img_path = p
                    print(f"✅ Використовуємо запасне зображення: {img_path}")
                    break
            else:
                print("❌ Не знайдено жодного зображення")
                return False
        
        # Створюємо PDF
        print("📝 Створюємо PDF...")
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Малюємо фон
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.rect(0, 0, width, height, fill=1)
        
        # Білий прямокутник
        c.setFillColorRGB(1, 1, 1)
        c.rect(80, 100, width - 160, height - 100, fill=1)
        
        # Додаємо текст
        c.setFont("Helvetica-Bold", 24)
        c.setFillColorRGB(0, 0, 0)
        c.drawCentredString(width / 2, height - 100, name)
        
        # Додаємо зображення
        try:
            img = Image.open(img_path)
            max_w = int(width - 200)
            max_h = 240
            img.thumbnail((max_w, max_h))
            img_w, img_h = img.size
            img_x = (width - img_w) / 2
            img_y = height - 200 - img_h
            img_io = ImageReader(img)
            c.drawImage(img_io, img_x, img_y, width=img_w, height=img_h)
            print("✅ Зображення додано")
        except Exception as e:
            print(f"⚠️ Помилка зображення: {e}")
        
        # Додаємо інформацію
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, 200, f"Date: {date}")
        c.drawCentredString(width / 2, 180, f"Time: {time}")
        c.drawCentredString(width / 2, 160, f"Price: {price}")
        c.drawCentredString(width / 2, 140, f"Address: {address}")
        
        c.save()
        print(f"✅ PDF створено: {pdf_path}")
        
        # Перевіряємо розмір файлу
        file_size = os.path.getsize(pdf_path)
        print(f"📊 Розмір файлу: {file_size} байт")
        
        if file_size > 0:
            print("✅ Тест пройшов успішно!")
            return True
        else:
            print("❌ Файл порожній")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ticket_creation()
    if success:
        print("\n🎉 Квиток створено успішно!")
    else:
        print("\n💥 Помилка створення квитка!")
