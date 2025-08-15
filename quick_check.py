#!/usr/bin/env python3
"""
Быстрая проверка пользователя в базе данных
"""

import sqlite3
from config import SPECIAL_ADMIN_IDS

def quick_check():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print("=== ПРОВЕРКА СПЕЦИАЛЬНЫХ АДМИНОВ ===")
    print(f"SPECIAL_ADMIN_IDS из конфига: {SPECIAL_ADMIN_IDS}")
    
    for admin_id in SPECIAL_ADMIN_IDS:
        print(f"\n--- Проверяем пользователя {admin_id} ---")
        
        # Проверяем, существует ли пользователь
        c.execute('SELECT * FROM users WHERE user_id=?', (admin_id,))
        user = c.fetchone()
        
        if user:
            print(f"✅ Пользователь найден: {user}")
            
            # Проверяем структуру таблицы
            c.execute("PRAGMA table_info(users)")
            columns = c.fetchall()
            column_names = [col[1] for col in columns]
            
            # Ищем колонку is_admin
            if 'is_admin' in column_names:
                admin_index = column_names.index('is_admin')
                is_admin = user[admin_index] if admin_index < len(user) else None
                print(f"is_admin: {is_admin}")
                
                if is_admin == 1:
                    print("✅ Пользователь является админом")
                else:
                    print("❌ Пользователь НЕ является админом")
            else:
                print("❌ Колонка 'is_admin' не найдена в таблице")
                
            # Проверяем статус
            if 'status' in column_names:
                status_index = column_names.index('status')
                status = user[status_index] if status_index < len(user) else None
                print(f"status: {status}")
            else:
                print("❌ Колонка 'status' не найдена в таблице")
                
        else:
            print(f"❌ Пользователь {admin_id} НЕ найден в базе")
            print("Создаем пользователя...")
            
            try:
                c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                         (admin_id, f"special_admin_{admin_id}", 'approved'))
                conn.commit()
                print(f"✅ Пользователь {admin_id} создан как специальный админ")
            except Exception as e:
                print(f"❌ Ошибка при создании: {e}")
    
    # Показываем всех админов
    print(f"\n=== ВСЕ АДМИНЫ В БАЗЕ ===")
    c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
    admins = c.fetchall()
    print(f"Всего админов: {len(admins)}")
    for admin in admins:
        print(f"  ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
    
    conn.close()

if __name__ == "__main__":
    quick_check()
