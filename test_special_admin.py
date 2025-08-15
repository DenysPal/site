#!/usr/bin/env python3
"""
Тестовый скрипт для проверки специальной админки
"""

import sqlite3

def test_special_admin():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Проверяем структуру таблицы
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    print("Структура таблицы users:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
    # Импортируем список специальных админов из конфига
    try:
        from config import SPECIAL_ADMIN_IDS
        special_admin_ids = SPECIAL_ADMIN_IDS
        print(f"Загружены специальные админы из конфига: {special_admin_ids}")
    except ImportError:
        # Fallback если конфиг недоступен
        special_admin_ids = [-4791617937, 7855499159]
        print(f"Конфиг недоступен, используем fallback: {special_admin_ids}")
    
    for admin_id in special_admin_ids:
        # Проверяем пользователя
        c.execute('SELECT * FROM users WHERE user_id = ?', (admin_id,))
        user = c.fetchone()
        
        if user:
            print(f"\nПользователь {admin_id} найден: {user}")
            # Убеждаемся что он админ
            c.execute('UPDATE users SET is_admin=1 WHERE user_id=?', (admin_id,))
            conn.commit()
            print(f"Пользователь {admin_id} установлен как админ")
        else:
            print(f"\nПользователь {admin_id} не найден, создаем...")
            username = f"special_admin_{admin_id}"
            c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                     (admin_id, username, "approved"))
            conn.commit()
            print(f"Пользователь {admin_id} создан как админ")
    
    # Показываем всех админов
    c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
    admins = c.fetchall()
    print(f"\nВсего админов: {len(admins)}")
    for admin in admins:
        print(f"  ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
    
    conn.close()

if __name__ == "__main__":
    test_special_admin()
