#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import random
import string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def test_pdf_creation():
    """Тест створення PDF з перевіркою прав доступу"""
    print("🧪 Тестування створення PDF...")
    
    # Генерируем уникальный order_id
    order_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    pdf_filename = f"order_{order_id}.pdf"
    pdf_path = os.path.join('tickets', pdf_filename)
    
    print(f"📄 Створюємо PDF: {pdf_path}")
    
    try:
        # Перевіряємо, чи можемо створити файл
        if os.path.exists(pdf_path):
            print(f"⚠️ Файл вже існує: {pdf_path}")
            return False
        
        # Створюємо PDF
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        
        # Додаємо простий текст
        c.setFont("Helvetica-Bold", 24)
        c.drawString(100, height - 100, "Test Ticket")
        c.drawString(100, height - 150, f"Order ID: {order_id}")
        
        c.save()
        
        # Перевіряємо, чи файл створився
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path)
            print(f"✅ PDF створено успішно: {pdf_path}")
            print(f"📊 Розмір файлу: {file_size} байт")
            
            # Видаляємо тестовий файл
            os.remove(pdf_path)
            print("🗑️ Тестовий файл видалено")
            return True
        else:
            print("❌ Файл не створився")
            return False
            
    except PermissionError as e:
        print(f"❌ Помилка прав доступу: {e}")
        return False
    except Exception as e:
        print(f"❌ Інша помилка: {e}")
        return False

if __name__ == "__main__":
    success = test_pdf_creation()
    if success:
        print("\n🎉 PDF створення працює!")
    else:
        print("\n💥 Проблема з створенням PDF!")
