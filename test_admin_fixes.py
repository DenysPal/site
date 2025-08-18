#!/usr/bin/env python3
"""
Тестування виправлень функції додавання адміністраторів
"""

import sqlite3
import json

def test_admin_functions():
    """Тестує функції роботи з адміністраторами"""
    print("=== ТЕСТУВАННЯ ВИПРАВЛЕНЬ АДМІНІСТРАТОРІВ ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # 1. Перевіряємо поточну структуру
    print("\n1. Поточна структура таблиці users:")
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    for col in columns:
        print(f"   {col[1]} {col[2]}")
    
    # 2. Перевіряємо поточних адміністраторів
    print("\n2. Поточні адміністратори:")
    c.execute('SELECT user_id, username, is_admin, status FROM users WHERE is_admin=1')
    admins = c.fetchall()
    if admins:
        for admin in admins:
            print(f"   ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}, status: {admin[3]}")
    else:
        print("   Адміністраторів не знайдено!")
    
    # 3. Тестуємо додавання адміністратора (як у виправленому коді)
    print("\n3. Тест додавання адміністратора:")
    test_id = 987654321
    test_username = "test_admin_fixed"
    
    try:
        # Перевіряємо, чи існує користувач
        c.execute('SELECT * FROM users WHERE user_id=?', (test_id,))
        existing_user = c.fetchone()
        
        if existing_user:
            print(f"   Користувач {test_id} вже існує: {existing_user}")
            # Оновлюємо існуючого користувача
            c.execute('UPDATE users SET is_admin=1, username=? WHERE user_id=?', (test_username, test_id))
            print(f"   Користувача {test_id} оновлено")
        else:
            print(f"   Створюємо нового користувача {test_id}")
            # Створюємо нового користувача
            c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                     (test_id, test_username, 'approved'))
            print(f"   Нового користувача {test_id} створено")
        
        conn.commit()
        
        # Перевіряємо результат
        c.execute('SELECT user_id, username, is_admin, status FROM users WHERE user_id=?', (test_id,))
        result = c.fetchone()
        print(f"   Результат після додавання: {result}")
        
        if result and result[2] == 1:
            print("   ✅ Адміністратор успішно додано!")
        else:
            print("   ❌ Помилка: права адміністратора не встановлено!")
        
        # 4. Тестуємо функцію is_admin (як у виправленому коді)
        print("\n4. Тест функції is_admin:")
        c.execute('SELECT is_admin FROM users WHERE user_id=?', (test_id,))
        is_admin_result = c.fetchone()
        if is_admin_result:
            is_admin_value = is_admin_result[0]
            result_bool = is_admin_value == 1
            print(f"   is_admin значення в базі: {is_admin_value}")
            print(f"   is_admin == 1: {result_bool}")
            print(f"   Результат функції is_admin: {result_bool}")
        else:
            print("   Користувача не знайдено після додавання!")
        
        # 5. Очищаємо тестові дані
        print("\n5. Очищення тестових даних:")
        c.execute('DELETE FROM users WHERE user_id=?', (test_id,))
        conn.commit()
        print("   Тестові дані очищено")
        
    except Exception as e:
        print(f"   ❌ Помилка при тестуванні: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. Фінальна перевірка
    print("\n6. Фінальна перевірка:")
    c.execute('SELECT user_id, username, is_admin, status FROM users WHERE is_admin=1')
    final_admins = c.fetchall()
    print(f"   Всього адміністраторів: {len(final_admins)}")
    
    conn.close()
    print("\n✅ Тестування завершено!")

def check_special_admin_ids():
    """Перевіряє спеціальні ID адміністраторів"""
    print("\n=== ПЕРЕВІРКА СПЕЦІАЛЬНИХ ID ===")
    
    try:
        import config
        special_admin_ids = getattr(config, 'SPECIAL_ADMIN_IDS', [])
        print(f"SPECIAL_ADMIN_IDS з config.py: {special_admin_ids}")
        
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

if __name__ == "__main__":
    test_admin_functions()
    check_special_admin_ids()
