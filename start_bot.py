#!/usr/bin/env python3
"""
Скрипт для безпечного запуску Telegram бота
Автоматично знаходить вільний порт та запускає бота
"""

import os
import sys
import subprocess
import time
import socket
import psutil

def find_free_port(start_port=8081, max_attempts=20):
    """Знаходить вільний порт"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    return None

def check_port_in_use(port):
    """Перевіряє, чи порт зайнятий"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return False
    except OSError:
        return True

def kill_process_on_port(port):
    """Завершує процес, який використовує порт"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                connections = proc.info['connections']
                if connections:
                    for conn in connections:
                        if conn.laddr.port == port:
                            print(f"🔄 Завершую процес {proc.info['name']} (PID: {proc.info['pid']}) на порту {port}")
                            proc.terminate()
                            time.sleep(2)
                            if proc.is_running():
                                proc.kill()
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        print(f"⚠️  Помилка при завершенні процесу: {e}")
    return False

def start_bot():
    """Запускає бота з автоматичним вибором порту"""
    print("🚀 Запуск Telegram бота...")
    print("=" * 50)
    
    # Перевіряємо наявність main.py
    if not os.path.exists('main.py'):
        print("❌ Файл main.py не знайдено!")
        print("Переконайтеся, що ви знаходитесь в правильній директорії")
        return False
    
    # Перевіряємо залежності
    print("🔍 Перевірка залежностей...")
    try:
        import aiogram
        import reportlab
        import PIL
        import barcode
        print("✅ Всі залежності встановлені")
    except ImportError as e:
        print(f"❌ Відсутня залежність: {e}")
        print("Встановіть залежності: pip install -r requirements.txt")
        return False
    
    # Перевіряємо порт 8081
    print(f"\n🔍 Перевірка порту 8081...")
    if check_port_in_use(8081):
        print("⚠️  Порт 8081 зайнятий")
        choice = input("Спробувати звільнити порт? (y/n): ").lower().strip()
        if choice == 'y':
            if kill_process_on_port(8081):
                print("✅ Порт 8081 звільнено")
                time.sleep(3)
            else:
                print("❌ Не вдалося звільнити порт 8081")
        else:
            print("ℹ️  Пропускаємо звільнення порту")
    
    # Знаходимо вільний порт
    print(f"\n🔍 Пошук вільного порту...")
    port = find_free_port(8081, 20)
    if port is None:
        print("❌ Не вдалося знайти вільний порт")
        return False
    
    print(f"✅ Знайдено вільний порт: {port}")
    
    # Запускаємо бота
    print(f"\n🚀 Запуск бота на порту {port}...")
    try:
        # Встановлюємо змінну середовища для порту
        env = os.environ.copy()
        env['WEBHOOK_PORT'] = str(port)
        
        # Запускаємо процес
        process = subprocess.Popen(
            [sys.executable, 'main.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ Бот запущений з PID: {process.pid}")
        print(f"🌐 Webhook доступний на порту: {port}")
        print(f"📱 Telegram бот активний")
        
        # Очікуємо трохи та перевіряємо статус
        time.sleep(5)
        if process.poll() is None:
            print("\n🎉 Бот успішно запущений!")
            print("=" * 50)
            print("📋 Інформація:")
            print(f"   🆔 PID: {process.pid}")
            print(f"   🌐 Порт: {port}")
            print(f"   📁 Робоча директорія: {os.getcwd()}")
            print(f"   🐍 Python: {sys.executable}")
            print("\n💡 Для зупинки бота натисніть Ctrl+C")
            
            try:
                # Очікуємо завершення процесу
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Отримано сигнал зупинки...")
                process.terminate()
                time.sleep(2)
                if process.poll() is None:
                    process.kill()
                print("✅ Бот зупинено")
            
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Помилка запуску бота:")
            if stdout:
                print(f"STDOUT: {stdout}")
            if stderr:
                print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Помилка запуску бота: {e}")
        return False

def main():
    """Головна функція"""
    print("🎫 Запуск системи генерації квитків")
    print("=" * 50)
    
    try:
        if start_bot():
            print("\n✅ Бот успішно запущений та працює!")
        else:
            print("\n❌ Не вдалося запустити бота")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Завершення роботи...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критична помилка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
