#!/usr/bin/env python3
"""
Простий скрипт для швидкого запуску бота
Автоматично знаходить вільний порт
"""

import os
import sys
import subprocess
import socket
import time

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

def main():
    print("🚀 Швидкий запуск Telegram бота")
    print("=" * 40)
    
    # Перевіряємо main.py
    if not os.path.exists('main.py'):
        print("❌ main.py не знайдено!")
        return
    
    # Знаходимо вільний порт
    print("🔍 Пошук вільного порту...")
    port = find_free_port(8081, 20)
    
    if port is None:
        print("❌ Не вдалося знайти вільний порт")
        return
    
    print(f"✅ Порт {port} вільний")
    
    # Запускаємо бота
    print(f"\n🚀 Запуск бота на порту {port}...")
    print("💡 Для зупинки натисніть Ctrl+C")
    print("-" * 40)
    
    try:
        # Встановлюємо змінну середовища
        env = os.environ.copy()
        env['WEBHOOK_PORT'] = str(port)
        
        # Запускаємо
        process = subprocess.run(
            [sys.executable, 'main.py'],
            env=env,
            check=False
        )
        
        if process.returncode == 0:
            print("✅ Бот завершив роботу успішно")
        else:
            print(f"⚠️  Бот завершився з кодом: {process.returncode}")
            
    except KeyboardInterrupt:
        print("\n🛑 Завершення роботи...")
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    main()
