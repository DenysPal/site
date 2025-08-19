#!/usr/bin/env python3
"""
Скрипт для створення page_code для конкретного користувача
"""

import sqlite3

def create_page_code_for_user():
    """Створює page_code для конкретного користувача"""
    
    print("🔧 Створення page_code для конкретного користувача...")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Показуємо доступних користувачів
        print("\n👥 Доступні користувачі:")
        c.execute('SELECT tg_id, username, first_name, last_name FROM site_users ORDER BY tg_id')
        users = c.fetchall()
        
        for i, user in enumerate(users, 1):
            print(f"{i}. ID: {user[0]} | @{user[1]} | {user[2]} {user[3]}")
        
        # Показуємо існуючі page_code
        print(f"\n📋 Існуючі page_code в event_links:")
        c.execute('SELECT event_code, user_id FROM event_links ORDER BY event_code LIMIT 10')
        existing = c.fetchall()
        for code, user_id in existing:
            print(f"   {code} → user_id: {user_id}")
        
        # Запитуємо користувача
        print(f"\n📝 Введіть дані для створення page_code:")
        
        try:
            user_choice = int(input("Виберіть номер користувача: ")) - 1
            if 0 <= user_choice < len(users):
                selected_user = users[user_choice]
                print(f"✅ Обрано: {selected_user[2]} {selected_user[3]} (@{selected_user[1]})")
            else:
                print("❌ Невірний номер користувача")
                return
        except ValueError:
            print("❌ Введіть число")
            return
        
        # Запитуємо page_code
        page_code = input("Введіть page_code (наприклад: 2-39): ").strip()
        if not page_code:
            print("❌ page_code не може бути порожнім")
            return
        
        # Перевіряємо, чи не існує вже
        c.execute('SELECT user_id FROM event_links WHERE event_code=?', (page_code,))
        if c.fetchone():
            print(f"❌ page_code {page_code} вже існує!")
            return
        
        # Створюємо page_code
        user_id = selected_user[0]
        c.execute('INSERT INTO event_links (event_code, user_id) VALUES (?, ?)', 
                 (page_code, user_id))
        conn.commit()
        
        print(f"✅ Створено page_code {page_code} для користувача {user_id}")
        print(f"   Тепер логи для {page_code} будуть йти користувачу {selected_user[2]} {selected_user[3]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_page_code_for_user()
