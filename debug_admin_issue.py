#!/usr/bin/env python3
"""
Скрипт для діагностики проблеми з додаванням адміністраторів
"""

import sqlite3
import json

def check_database_structure():
    """Перевіряє структуру бази даних"""
    print("=== ПЕРЕВІРКА СТРУКТУРИ БАЗИ ДАНИХ ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо структуру таблиці users
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    print("Структура таблиці users:")
    for col in columns:
        print(f"  {col[1]} {col[2]}")
    
    # Перевіряємо індекси
    c.execute("PRAGMA index_list(users)")
    indexes = c.fetchall()
    print(f"\nІндекси таблиці users: {indexes}")
    
    conn.close()

def check_current_admins():
    """Перевіряє поточних адміністраторів"""
    print("\n=== ПОТОЧНІ АДМІНІСТРАТОРИ ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо всіх адміністраторів
    c.execute('SELECT user_id, username, is_admin, status FROM users WHERE is_admin=1')
    admins = c.fetchall()
    
    if not admins:
        print("Адміністраторів не знайдено!")
    else:
        print(f"Знайдено {len(admins)} адміністраторів:")
        for admin in admins:
            print(f"  ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}, status: {admin[3]}")
    
    # Перевіряємо всіх користувачів
    c.execute('SELECT user_id, username, is_admin, status FROM users ORDER BY user_id')
    all_users = c.fetchall()
    print(f"\nВсього користувачів: {len(all_users)}")
    for user in all_users[:10]:  # Показуємо перших 10
        print(f"  ID: {user[0]}, Username: {user[1]}, is_admin: {user[2]}, status: {user[3]}")
    
    if len(all_users) > 10:
        print(f"  ... та ще {len(all_users) - 10} користувачів")
    
    conn.close()

def test_add_admin():
    """Тестує додавання адміністратора"""
    print("\n=== ТЕСТ ДОДАВАННЯ АДМІНІСТРАТОРА ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Тестовий ID адміністратора
    test_admin_id = 999999999
    test_username = "test_admin_debug"
    
    print(f"Тестуємо додавання адміністратора: ID={test_admin_id}, username={test_username}")
    
    try:
        # Перевіряємо, чи існує користувач
        c.execute('SELECT * FROM users WHERE user_id=?', (test_admin_id,))
        existing_user = c.fetchone()
        
        if existing_user:
            print(f"Користувач вже існує: {existing_user}")
            # Оновлюємо існуючого користувача
            c.execute('UPDATE users SET is_admin=1, username=? WHERE user_id=?', (test_username, test_admin_id))
            print("Користувача оновлено")
        else:
            print("Користувача не знайдено, створюємо нового")
            # Створюємо нового користувача
            c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                     (test_admin_id, test_username, 'approved'))
            print("Нового користувача створено")
        
        conn.commit()
        
        # Перевіряємо результат
        c.execute('SELECT user_id, username, is_admin, status FROM users WHERE user_id=?', (test_admin_id,))
        result = c.fetchone()
        print(f"Результат після додавання: {result}")
        
        # Перевіряємо функцію is_admin
        c.execute('SELECT is_admin FROM users WHERE user_id=?', (test_admin_id,))
        is_admin_result = c.fetchone()
        if is_admin_result:
            print(f"is_admin значення в базі: {is_admin_result[0]}")
            print(f"is_admin == 1: {is_admin_result[0] == 1}")
        else:
            print("Користувача не знайдено після додавання!")
        
        # Очищаємо тестові дані
        c.execute('DELETE FROM users WHERE user_id=?', (test_admin_id,))
        conn.commit()
        print("Тестові дані очищено")
        
    except Exception as e:
        print(f"Помилка при тестуванні: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()

def check_special_admin_ids():
    """Перевіряє спеціальні ID адміністраторів"""
    print("\n=== СПЕЦІАЛЬНІ ID АДМІНІСТРАТОРІВ ===")
    
    try:
        # Імпортуємо конфігурацію
        import config
        special_admin_ids = getattr(config, 'SPECIAL_ADMIN_IDS', [])
        print(f"SPECIAL_ADMIN_IDS з config.py: {special_admin_ids}")
        
        # Перевіряємо кожного спеціального адміністратора
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        for admin_id in special_admin_ids:
            c.execute('SELECT user_id, username, is_admin, status FROM users WHERE user_id=?', (admin_id,))
            user = c.fetchone()
            if user:
                print(f"  ID {admin_id}: {user}")
            else:
                print(f"  ID {admin_id}: НЕ ЗНАЙДЕНО в базі!")
        
        conn.close()
        
    except Exception as e:
        print(f"Помилка при перевірці конфігурації: {e}")

def main():
    """Головна функція"""
    print("ДІАГНОСТИКА ПРОБЛЕМИ З ДОДАВАННЯМ АДМІНІСТРАТОРІВ")
    print("=" * 60)
    
    check_database_structure()
    check_current_admins()
    check_special_admin_ids()
    test_add_admin()
    
    print("\n=== ДІАГНОСТИКА ЗАВЕРШЕНО ===")

if __name__ == "__main__":
    main()
