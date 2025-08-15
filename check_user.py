#!/usr/bin/env python3
"""
Скрипт для проверки пользователя в базе данных
"""

import sqlite3
from config import SPECIAL_ADMIN_IDS

def check_user(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print(f"Проверяем пользователя {user_id}")
    
    # Проверяем, существует ли пользователь
    c.execute('SELECT * FROM users WHERE user_id=?', (user_id,))
    user = c.fetchone()
    
    if user:
        print(f"Пользователь найден: {user}")
        
        # Проверяем структуру
        c.execute("PRAGMA table_info(users)")
        columns = c.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Колонки таблицы: {column_names}")
        
        # Показываем все данные пользователя
        for i, col_name in enumerate(column_names):
            if i < len(user):
                print(f"  {col_name}: {user[i]}")
            else:
                print(f"  {col_name}: <отсутствует>")
        
        # Проверяем права админа
        is_admin = user[column_names.index('is_admin')] if 'is_admin' in column_names else None
        print(f"is_admin: {is_admin}")
        
        if user_id in SPECIAL_ADMIN_IDS:
            print(f"✅ Пользователь {user_id} в списке SPECIAL_ADMIN_IDS")
        else:
            print(f"❌ Пользователь {user_id} НЕ в списке SPECIAL_ADMIN_IDS")
            
    else:
        print(f"Пользователь {user_id} не найден в базе")
        
        # Создаем пользователя
        print("Создаем пользователя...")
        try:
            c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                     (user_id, f"special_admin_{user_id}", 'approved'))
            conn.commit()
            print(f"✅ Пользователь {user_id} создан")
        except Exception as e:
            print(f"❌ Ошибка при создании: {e}")
    
    conn.close()

if __name__ == "__main__":
    # Проверяем всех специальных админов
    for admin_id in SPECIAL_ADMIN_IDS:
        print(f"\n{'='*50}")
        check_user(admin_id)
        print(f"{'='*50}")
