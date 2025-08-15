#!/usr/bin/env python3
"""
Тестовый скрипт для проверки добавления админа в базу данных
"""

import sqlite3

def test_add_admin():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Проверяем структуру таблицы
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    print("Структура таблицы users:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
    # Тестируем добавление админа
    test_admin_id = 123456789
    test_username = "test_admin"
    
    print(f"\nТестируем добавление админа: ID={test_admin_id}, username={test_username}")
    
    try:
        # Проверяем, существует ли пользователь
        c.execute('SELECT * FROM users WHERE user_id=?', (test_admin_id,))
        existing_user = c.fetchone()
        
        if existing_user:
            print(f"Пользователь существует: {existing_user}")
            # Обновляем существующего пользователя
            c.execute('UPDATE users SET is_admin=1, username=? WHERE user_id=?', (test_username, test_admin_id))
            print("Пользователь обновлен")
        else:
            print("Пользователь не существует, создаем нового")
            # Создаем нового пользователя
            c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                     (test_admin_id, test_username, 'approved'))
            print("Новый пользователь создан")
        
        conn.commit()
        
        # Проверяем результат
        c.execute('SELECT user_id, username, is_admin FROM users WHERE user_id=?', (test_admin_id,))
        result = c.fetchone()
        print(f"Результат после добавления: {result}")
        
        # Показываем всех админов
        c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
        admins = c.fetchall()
        print(f"\nВсего админов: {len(admins)}")
        for admin in admins:
            print(f"  ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
        
        # Удаляем тестового админа
        c.execute('DELETE FROM users WHERE user_id=?', (test_admin_id,))
        conn.commit()
        print(f"\nТестовый админ {test_admin_id} удален")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    
    conn.close()

if __name__ == "__main__":
    test_add_admin()
