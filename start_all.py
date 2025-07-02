#!/usr/bin/env python3
import subprocess
import sys
import time
import threading
import os

def run_bot():
    """Запускає Telegram бота"""
    print("🤖 Запуск Telegram бота...")
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("⏹️ Бот зупинений")
    except Exception as e:
        print(f"❌ Помилка запуску бота: {e}")

def run_server(port=8080):
    """Запускає веб-сервер"""
    print(f"🌐 Запуск веб-сервера на порту {port}...")
    try:
        if port == 80:
            subprocess.run([sys.executable, "server.py"], check=True)
        else:
            subprocess.run([sys.executable, "server_8080.py"], check=True)
    except KeyboardInterrupt:
        print("⏹️ Сервер зупинений")
    except Exception as e:
        print(f"❌ Помилка запуску сервера: {e}")

def check_dependencies():
    """Перевіряє наявність необхідних файлів"""
    required_files = [
        "main.py",
        "server_8080.py", 
        "server.py",
        "events-art.com/index.html"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Відсутні файли:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ Всі необхідні файли знайдено")
    return True

def main():
    print("🚀 Запуск всіх сервісів")
    print("=" * 50)
    
    # Перевіряємо залежності
    if not check_dependencies():
        print("\n❌ Неможливо запустити сервіси")
        return
    
    print("\n📋 Доступні опції:")
    print("1. Запустити тільки бота")
    print("2. Запустити тільки сервер (порт 8080)")
    print("3. Запустити тільки сервер (порт 80 - потребує адмін прав)")
    print("4. Запустити бота + сервер (порт 8080)")
    print("5. Тестувати сервер")
    
    try:
        choice = input("\nВиберіть опцію (1-5): ").strip()
        
        if choice == "1":
            run_bot()
        elif choice == "2":
            run_server(8080)
        elif choice == "3":
            run_server(80)
        elif choice == "4":
            print("🔄 Запуск бота та сервера...")
            # Запускаємо сервер в окремому потоці
            server_thread = threading.Thread(target=run_server, args=(8080,))
            server_thread.daemon = True
            server_thread.start()
            
            # Даємо серверу час на запуск
            time.sleep(2)
            
            # Запускаємо бота
            run_bot()
        elif choice == "5":
            subprocess.run([sys.executable, "test_server.py"])
        else:
            print("❌ Невірний вибір")
            
    except KeyboardInterrupt:
        print("\n⏹️ Всі сервіси зупинені")
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    main() 