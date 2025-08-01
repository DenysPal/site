#!/usr/bin/env python3
"""
Скрипт для добавления всех существующих page_code в список игнорирования первого лога
"""

import sqlite3
import requests
import time

def add_existing_page_codes_to_ignore():
    """Добавляет все существующие page_code в список игнорирования первого лога"""
    
    # Подключаемся к базе данных
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Получаем все page_code из базы данных
        c.execute('SELECT page_code FROM site_users WHERE page_code IS NOT NULL')
        page_codes = [row[0] for row in c.fetchall()]
        
        print(f"Найдено {len(page_codes)} page_code для добавления в список игнорирования")
        
        # Добавляем каждый page_code в список игнорирования
        success_count = 0
        for page_code in page_codes:
            try:
                response = requests.post(
                    'http://127.0.0.1:8080/ignore_first_visit', 
                    json={'page_code': page_code}, 
                    timeout=2
                )
                if response.status_code == 200:
                    print(f"✅ Добавлен {page_code}")
                    success_count += 1
                else:
                    print(f"❌ Ошибка для {page_code}: {response.status_code}")
                
                # Небольшая задержка между запросами
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Ошибка для {page_code}: {e}")
        
        print(f"\nРезультат: {success_count}/{len(page_codes)} page_code успешно добавлены")
        
    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("Добавление существующих page_code в список игнорирования первого лога...")
    add_existing_page_codes_to_ignore()
    print("Готово!") 