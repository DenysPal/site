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
    
    # Проверяем пользователя с ID -4791617937
    c.execute('SELECT * FROM users WHERE user_id = ?', (-4791617937,))
    user = c.fetchone()
    
    if user:
        print(f"\nПользователь найден: {user}")
        # Убеждаемся что он админ
        c.execute('UPDATE users SET is_admin=1 WHERE user_id=?', (-4791617937,))
        conn.commit()
        print("Пользователь установлен как админ")
    else:
        print("\nПользователь не найден, создаем...")
        c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                 (-4791617937, "special_admin", "approved"))
        conn.commit()
        print("Пользователь создан как админ")
    
    # Показываем всех админов
    c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
    admins = c.fetchall()
    print(f"\nВсего админов: {len(admins)}")
    for admin in admins:
        print(f"  ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
    
    conn.close()

if __name__ == "__main__":
    test_special_admin()
