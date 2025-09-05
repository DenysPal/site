#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Швидкий тест QR-коду без чорного квадрата
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def test_qr_code_only():
    """Тест тільки QR-коду"""
    print("🔍 Тестуємо QR-код без чорного квадрата...")
    
    # Шлях до QR-коду
    qr_code_path = os.path.join('events-art.com', 'image', 'image.png')
    
    if not os.path.exists(qr_code_path):
        print(f"❌ QR-код не знайдено: {qr_code_path}")
        return False
    
    # Створюємо PDF
    pdf_path = "test_qr_only.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Центр сторінки
    center_x = width / 2
    center_y = height / 2
    
    # Малюємо QR-код по центру
    qr_size = 100
    qr_x = center_x - qr_size / 2
    qr_y = center_y - qr_size / 2
    
    try:
        c.drawImage(qr_code_path, qr_x, qr_y, width=qr_size, height=qr_size)
        print(f"✅ QR-код додано: {qr_code_path}")
        print(f"📍 Позиція: x={qr_x}, y={qr_y}, розмір={qr_size}x{qr_size}")
    except Exception as e:
        print(f"❌ Помилка малювання QR-коду: {e}")
        c.save()
        return False
    
    # Додаємо текст
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(center_x, center_y + 80, "Тест QR-коду")
    c.drawCentredString(center_x, center_y - 80, "Без чорного квадрата")
    
    c.save()
    
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"✅ PDF створено: {pdf_path} (розмір: {file_size} байт)")
        
        # Копіюємо у веб-папку
        web_path = 'metanoia-gallery.com/file/ticket/test_qr_only.pdf'
        try:
            os.makedirs('metanoia-gallery.com/file/ticket', exist_ok=True)
            import shutil
            shutil.copy2(pdf_path, web_path)
            print(f"✅ PDF скопійовано у веб-папку: {web_path}")
        except Exception as e:
            print(f"⚠️  Помилка копіювання: {e}")
        
        return True
    else:
        print("❌ PDF не створено")
        return False

if __name__ == "__main__":
    print("🚀 Швидкий тест QR-коду")
    print("=" * 30)
    
    if test_qr_code_only():
        print("\n✅ Тест пройшов успішно!")
        print("🔍 Перевірте файл test_qr_only.pdf")
    else:
        print("\n❌ Тест не пройшов")
