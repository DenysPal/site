#!/usr/bin/env python3
"""
Тестовий скрипт для системи генерації квитків
Перевіряє основні функції без запуску Telegram бота
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Додаємо поточну директорію до шляху для імпорту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dependencies():
    """Перевіряє наявність необхідних залежностей"""
    print("🔍 Перевірка залежностей...")
    
    required_packages = [
        'reportlab',
        'PIL',  # Pillow
        'barcode',
        'aiogram'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - відсутній")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Відсутні пакети: {', '.join(missing_packages)}")
        print("Встановіть їх командою: pip install -r requirements.txt")
        return False
    
    print("✅ Всі залежності встановлені")
    return True

def test_directories():
    """Перевіряє наявність необхідних папок"""
    print("\n📁 Перевірка папок...")
    
    required_dirs = [
        'tickets',
        'events-art.com/file/ticket',
        'events-art.com/image'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - відсутня")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n📂 Створення відсутніх папок...")
        for dir_path in missing_dirs:
            try:
                os.makedirs(dir_path, exist_ok=True)
                print(f"✅ Створено: {dir_path}")
            except Exception as e:
                print(f"❌ Помилка створення {dir_path}: {e}")
                return False
    
    return True

def test_image_files():
    """Перевіряє наявність зображень для квитків"""
    print("\n🖼️  Перевірка зображень...")
    
    image_dir = 'events-art.com/image'
    if not os.path.exists(image_dir):
        print(f"❌ Папка {image_dir} не існує")
        return False
    
    # Шукаємо будь-які зображення
    image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
    images = []
    
    for ext in image_extensions:
        images.extend(Path(image_dir).glob(f'*{ext}'))
        images.extend(Path(image_dir).glob(f'*{ext.upper()}'))
    
    if images:
        print(f"✅ Знайдено {len(images)} зображень:")
        for img in images[:5]:  # Показуємо перші 5
            print(f"   📷 {img.name}")
        if len(images) > 5:
            print(f"   ... та ще {len(images) - 5} зображень")
    else:
        print("⚠️  Зображення не знайдено")
        print("   Додайте зображення в папку events-art.com/image/")
    
    return True

def test_pdf_generation():
    """Тестує генерацію PDF квитка"""
    print("\n📄 Тест генерації PDF...")
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        # Створюємо тестовий PDF
        test_pdf = 'test_ticket.pdf'
        c = canvas.Canvas(test_pdf, pagesize=A4)
        width, height = A4
        
        # Простий тестовий квиток
        c.setFont("Helvetica-Bold", 24)
        c.drawCentredString(width / 2, height - 100, "TEST TICKET")
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2, height - 150, "Тестова генерація PDF")
        c.save()
        
        if os.path.exists(test_pdf):
            print("✅ PDF створено успішно")
            # Видаляємо тестовий файл
            os.remove(test_pdf)
            return True
        else:
            print("❌ PDF не створено")
            return False
            
    except Exception as e:
        print(f"❌ Помилка генерації PDF: {e}")
        return False

def test_barcode_generation():
    """Тестує генерацію штрих-кодів"""
    print("\n📊 Тест генерації штрих-кодів...")
    
    try:
        import barcode
        from barcode.writer import ImageWriter
        
        # Створюємо тестовий штрих-код
        test_barcode = 'test_barcode.png'
        barcode_value = '123456789'
        
        barcode_img = barcode.get('code128', barcode_value, writer=ImageWriter())
        barcode_img.save(test_barcode)
        
        if os.path.exists(test_barcode):
            print("✅ Штрих-код створено успішно")
            # Видаляємо тестовий файл
            os.remove(test_barcode)
            return True
        else:
            print("❌ Штрих-код не створено")
            return False
            
    except Exception as e:
        print(f"❌ Помилка генерації штрих-коду: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🎫 Тестування системи генерації квитків")
    print("=" * 50)
    
    tests = [
        ("Залежності", test_dependencies),
        ("Папки", test_directories),
        ("Зображення", test_image_files),
        ("PDF генерація", test_pdf_generation),
        ("Штрих-коди", test_barcode_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ Тест '{test_name}' не пройдено")
        except Exception as e:
            print(f"❌ Помилка в тесті '{test_name}': {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результати тестування: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("🎉 Всі тести пройдено успішно!")
        print("✅ Система генерації квитків готова до роботи")
    else:
        print("⚠️  Деякі тести не пройдено")
        print("🔧 Виправіть помилки перед використанням")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
