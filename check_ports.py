#!/usr/bin/env python3
"""
Скрипт для перевірки та очищення зайнятих портів
Корисно при помилці "address already in use"
"""

import socket
import subprocess
import sys
import os

def check_port(port):
    """Перевіряє, чи порт зайнятий"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            return False
    except OSError:
        return True

def find_process_on_port(port):
    """Знаходить процес, який використовує порт"""
    try:
        # Використовуємо netstat для пошуку процесу
        result = subprocess.run(
            ['netstat', '-tlnp'], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        process_info = parts[6]
                        return process_info
        return None
    except Exception:
        return None

def kill_process_by_pid(pid):
    """Завершує процес за PID"""
    try:
        subprocess.run(['kill', '-9', str(pid)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("🔍 Перевірка портів для Telegram бота")
    print("=" * 50)
    
    # Перевіряємо основні порти
    ports_to_check = [8081, 8080, 8082, 8083]
    
    for port in ports_to_check:
        if check_port(port):
            print(f"❌ Порт {port} зайнятий")
            
            # Спробуємо знайти процес
            process_info = find_process_on_port(port)
            if process_info:
                print(f"   📋 Процес: {process_info}")
                
                # Пропонуємо завершити
                choice = input(f"   🔄 Завершити процес на порту {port}? (y/n): ").lower().strip()
                if choice == 'y':
                    try:
                        pid = int(process_info.split('/')[0])
                        if kill_process_by_pid(pid):
                            print(f"   ✅ Процес {pid} завершено")
                        else:
                            print(f"   ❌ Не вдалося завершити процес {pid}")
                    except ValueError:
                        print(f"   ⚠️  Не вдалося отримати PID з {process_info}")
            else:
                print(f"   ⚠️  Не вдалося знайти процес")
        else:
            print(f"✅ Порт {port} вільний")
    
    print("\n" + "=" * 50)
    
    # Рекомендації
    if any(check_port(port) for port in ports_to_check):
        print("⚠️  Деякі порти зайняті")
        print("💡 Рекомендації:")
        print("   1. Використовуйте quick_start.py для автоматичного пошуку вільного порту")
        print("   2. Або завершіть процеси, які використовують потрібні порти")
        print("   3. Перезапустіть систему, якщо потрібно")
    else:
        print("🎉 Всі порти вільні!")
        print("✅ Можна запускати бота командою: python main.py")
    
    print("\n🚀 Для запуску бота використовуйте:")
    print("   python quick_start.py    # Автоматичний пошук порту")
    print("   python start_bot.py      # Розширений запуск")

if __name__ == "__main__":
    main()
