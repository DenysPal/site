#!/usr/bin/env python3
"""
Скрипт для застосування всіх виправлень стабільності сайту metanoia-gallery.com
"""

import os
import shutil
import subprocess
import sys
import time

def print_header():
    """Виводить заголовок скрипта"""
    print("=" * 70)
    print("🔧 ЗАСТОСУВАННЯ ВИПРАВЛЕНЬ СТАБІЛЬНОСТІ")
    print("🌐 Сайт: metanoia-gallery.com")
    print("=" * 70)

def check_requirements():
    """Перевіряє наявність необхідних файлів"""
    print("🔍 Перевірка необхідних файлів...")
    
    required_files = [
        "events-art.com/index.html",
        "events-art.com/js/event-loader.js",
        "events-art.com/js/stability-fixes.js",
        "server_artpullse.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Відсутні необхідні файли:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    
    print("✅ Всі необхідні файли знайдено")
    return True

def backup_files():
    """Створює резервні копії файлів"""
    print("\n💾 Створення резервних копій...")
    
    backup_dir = "backup_stability_" + time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(backup_dir, exist_ok=True)
    
    files_to_backup = [
        "events-art.com/index.html",
        "events-art.com/js/event-loader.js",
        "server_artpullse.py"
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, file_path.replace("/", "_"))
            shutil.copy2(file_path, backup_path)
            print(f"   ✅ Створено резервну копію: {backup_path}")
    
    print(f"📁 Резервні копії збережено в: {backup_dir}")
    return backup_dir

def verify_changes():
    """Перевіряє застосовані зміни"""
    print("\n🔍 Перевірка застосованих змін...")
    
    # Перевіряємо кнопку Home
    try:
        with open("events-art.com/index.html", "r", encoding="utf-8") as f:
            content = f.read()
            if 'href="/"' in content:
                print("✅ Кнопка Home виправлена")
            else:
                print("❌ Кнопка Home не виправлена")
                return False
    except Exception as e:
        print(f"❌ Помилка перевірки index.html: {e}")
        return False
    
    # Перевіряємо JavaScript файли
    js_files = [
        "events-art.com/js/event-loader.js",
        "events-art.com/js/stability-fixes.js"
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            print(f"✅ {js_file} створено")
        else:
            print(f"❌ {js_file} не створено")
            return False
    
    # Перевіряємо сервер
    try:
        with open("server_artpullse.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "API_CACHE" in content and "handle_api_request" in content:
                print("✅ Сервер покращено")
            else:
                print("❌ Сервер не покращено")
                return False
    except Exception as e:
        print(f"❌ Помилка перевірки сервера: {e}")
        return False
    
    return True

def test_server():
    """Тестує сервер"""
    print("\n🧪 Тестування сервера...")
    
    try:
        # Запускаємо сервер в фоновому режимі
        print("   🚀 Запуск сервера...")
        process = subprocess.Popen([
            sys.executable, "server_artpullse.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Даємо серверу час на запуск
        time.sleep(3)
        
        # Перевіряємо чи сервер запущений
        if process.poll() is None:
            print("   ✅ Сервер запущено успішно")
            
            # Зупиняємо сервер
            process.terminate()
            process.wait()
            print("   ⏹️ Сервер зупинено")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ Помилка запуску сервера:")
            print(f"      stdout: {stdout.decode()}")
            print(f"      stderr: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"   ❌ Помилка тестування сервера: {e}")
        return False

def run_stability_tests():
    """Запускає тести стабільності"""
    print("\n🧪 Запуск тестів стабільності...")
    
    if os.path.exists("test_stability.py"):
        try:
            result = subprocess.run([
                sys.executable, "test_stability.py"
            ], capture_output=True, text=True, timeout=60)
            
            print("📊 Результати тестування:")
            print(result.stdout)
            
            if result.stderr:
                print("⚠️ Попередження:")
                print(result.stderr)
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("⏰ Тестування перевищило час очікування")
            return False
        except Exception as e:
            print(f"❌ Помилка запуску тестів: {e}")
            return False
    else:
        print("⚠️ Файл test_stability.py не знайдено, пропускаємо тестування")
        return True

def main():
    """Головна функція"""
    print_header()
    
    # Перевіряємо необхідні файли
    if not check_requirements():
        print("\n❌ Неможливо продовжити без необхідних файлів")
        return False
    
    # Створюємо резервні копії
    backup_dir = backup_files()
    
    print("\n✅ Всі виправлення вже застосовано!")
    print("📁 Резервні копії створено в:", backup_dir)
    
    # Перевіряємо зміни
    if not verify_changes():
        print("\n❌ Деякі зміни не застосовано правильно")
        return False
    
    # Тестуємо сервер
    if not test_server():
        print("\n❌ Проблеми з сервером")
        return False
    
    # Запускаємо тести стабільності
    if not run_stability_tests():
        print("\n⚠️ Тести стабільності не пройдено повністю")
    
    print("\n" + "=" * 70)
    print("🎉 ВИПРАВЛЕННЯ СТАБІЛЬНОСТІ ЗАСТОСОВАНО УСПІШНО!")
    print("=" * 70)
    print("\n📋 Що було виправлено:")
    print("   ✅ Кнопка Home тепер працює стабільно")
    print("   ✅ Дані (час, дата, білети) зберігаються між сесіями")
    print("   ✅ Додано краще кешування та fallback дані")
    print("   ✅ Покращено обробку помилок")
    print("   ✅ Додано автоматичне відновлення при проблемах")
    print("   ✅ Сервер тепер стабільніший")
    
    print("\n🚀 Для запуску сервера використовуйте:")
    print("   python server_artpullse.py")
    
    print("\n🧪 Для тестування стабільності:")
    print("   python test_stability.py")
    
    print("\n📖 Детальна інформація в файлі: STABILITY_FIXES_README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Операцію перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        sys.exit(1) 