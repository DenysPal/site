#!/usr/bin/env python3
"""
Швидке виправлення проблеми з адміністраторами
"""

import sqlite3
import json

def fix_admin_issue():
    """Виправляє основні проблеми з адміністраторами"""
    print("=== ШВИДКЕ ВИПРАВЛЕННЯ ПРОБЛЕМИ З АДМІНІСТРАТОРАМИ ===")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # 1. Перевіряємо структуру таблиці
        print("\n1. Перевірка структури таблиці users:")
        c.execute("PRAGMA table_info(users)")
        columns = c.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'is_admin' not in column_names:
            print("   ❌ Колонка 'is_admin' відсутня! Додаємо...")
            c.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
            conn.commit()
            print("   ✅ Колонка 'is_admin' додана")
        else:
            print("   ✅ Колонка 'is_admin' існує")
        
        # 2. Перевіряємо поточних адміністраторів
        print("\n2. Поточні адміністратори:")
        c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
        admins = c.fetchall()
        if admins:
            for admin in admins:
                print(f"   ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
        else:
            print("   Адміністраторів не знайдено!")
        
        # 3. Перевіряємо спеціальних адміністраторів
        print("\n3. Перевірка спеціальних адміністраторів:")
        try:
            import config
            special_admin_ids = getattr(config, 'SPECIAL_ADMIN_IDS', [])
            print(f"   SPECIAL_ADMIN_IDS: {special_admin_ids}")
            
            for admin_id in special_admin_ids:
                c.execute('SELECT user_id, username, is_admin FROM users WHERE user_id=?', (admin_id,))
                user = c.fetchone()
                if user:
                    if user[2] != 1:
                        print(f"   Виправляємо права адміністратора для ID {admin_id}")
                        c.execute('UPDATE users SET is_admin=1 WHERE user_id=?', (admin_id,))
                    else:
                        print(f"   ID {admin_id} вже є адміністратором")
                else:
                    print(f"   Створюємо спеціального адміністратора ID {admin_id}")
                    c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                             (admin_id, f"special_admin_{admin_id}", "approved"))
            
            conn.commit()
            
        except Exception as e:
            print(f"   Помилка при перевірці конфігурації: {e}")
        
        # 4. Перевіряємо головного адміністратора
        print("\n4. Перевірка головного адміністратора:")
        try:
            main_admin_id = getattr(config, 'ADMIN_ID', 7973971109)
            print(f"   Головний адміністратор ID: {main_admin_id}")
            
            c.execute('SELECT user_id, username, is_admin FROM users WHERE user_id=?', (main_admin_id,))
            user = c.fetchone()
            if user:
                if user[2] != 1:
                    print(f"   Виправляємо права адміністратора для головного адміністратора")
                    c.execute('UPDATE users SET is_admin=1 WHERE user_id=?', (main_admin_id,))
                else:
                    print(f"   Головний адміністратор вже має права")
            else:
                print(f"   Створюємо головного адміністратора")
                c.execute('INSERT INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                         (main_admin_id, "main_admin", "approved"))
            
            conn.commit()
            
        except Exception as e:
            print(f"   Помилка при перевірці головного адміністратора: {e}")
        
        # 5. Фінальна перевірка
        print("\n5. Фінальна перевірка:")
        c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
        final_admins = c.fetchall()
        print(f"   Всього адміністраторів: {len(final_admins)}")
        for admin in final_admins:
            print(f"     ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
        
        conn.close()
        print("\n✅ Виправлення завершено!")
        
    except Exception as e:
        print(f"\n❌ Помилка при виправленні: {e}")
        import traceback
        traceback.print_exc()

def test_admin_functionality():
    """Тестує функціональність адміністраторів після виправлення"""
    print("\n=== ТЕСТУВАННЯ ФУНКЦІОНАЛЬНОСТІ ===")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Тестуємо додавання нового адміністратора
        test_id = 111111111
        test_username = "test_admin_fix"
        
        print(f"   Тестуємо додавання адміністратора ID: {test_id}")
        
        # Додаємо тестового адміністратора
        c.execute('INSERT OR IGNORE INTO users (user_id, is_admin, username, status) VALUES (?, 1, ?, ?)', 
                 (test_id, test_username, 'approved'))
        conn.commit()
        
        # Перевіряємо результат
        c.execute('SELECT user_id, username, is_admin FROM users WHERE user_id=?', (test_id,))
        result = c.fetchone()
        if result and result[2] == 1:
            print("   ✅ Тест додавання адміністратора пройшов успішно!")
        else:
            print("   ❌ Тест додавання адміністратора не пройшов!")
        
        # Очищаємо тест
        c.execute('DELETE FROM users WHERE user_id=?', (test_id,))
        conn.commit()
        
        conn.close()
        
    except Exception as e:
        print(f"   ❌ Помилка при тестуванні: {e}")

if __name__ == "__main__":
    fix_admin_issue()
    test_admin_functionality()
