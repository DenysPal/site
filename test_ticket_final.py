#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from main import validate_ticket_data

async def test_ticket_creation():
    """Тест створення квитка"""
    print("🧪 Тестування створення квитка...")
    
    # Тестові дані
    name = "Test User"
    time = "21:00"
    date = "23.05"
    price = "40 €"
    address = "Test Address"
    
    # Тестуємо валідацію
    print("📋 Тестуємо валідацію...")
    errors = validate_ticket_data(name, time, date, price, address)
    if errors:
        print(f"❌ Помилки валідації: {errors}")
        return False
    else:
        print("✅ Валідація пройшла")
    
    # Перевіряємо наявність папок
    print("📁 Перевіряємо папки...")
    required_dirs = ['tickets', 'metanoia-gallery.com/file/ticket', 'events-art.com/image']
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Папка існує: {dir_path}")
        else:
            print(f"❌ Папка не існує: {dir_path}")
            return False
    
    # Перевіряємо зображення
    print("🖼️ Перевіряємо зображення...")
    img_path = os.path.join('events-art.com', 'image', '_dsf0493_ko_lekcja_3000px_auto_1400x800.webp')
    if os.path.exists(img_path):
        print(f"✅ Основне зображення знайдено: {img_path}")
    else:
        print(f"⚠️ Основне зображення не знайдено: {img_path}")
        # Шукаємо запасні
        backup_images = [
            'events-art.com/image/vine.webp',
            'events-art.com/image/news_5_1.jpg',
            'events-art.com/image/header-image.jpg'
        ]
        found = False
        for backup in backup_images:
            if os.path.exists(backup):
                print(f"✅ Запасне зображення знайдено: {backup}")
                found = True
                break
        if not found:
            print("❌ Не знайдено жодного зображення")
            return False
    
    print("✅ Всі перевірки пройшли успішно!")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_ticket_creation())
    if success:
        print("\n🎉 Система готова до створення квитків!")
    else:
        print("\n💥 Є проблеми з системою!")
