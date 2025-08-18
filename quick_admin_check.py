import sqlite3

# Швидка перевірка проблеми з адміністраторами
print("=== ШВИДКА ПЕРЕВІРКА ПРОБЛЕМИ З АДМІНІСТРАТОРАМИ ===")

try:
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # 1. Перевіряємо структуру таблиці
    print("\n1. Структура таблиці users:")
    c.execute("PRAGMA table_info(users)")
    columns = c.fetchall()
    for col in columns:
        print(f"   {col[1]} {col[2]}")
    
    # 2. Перевіряємо поточних адміністраторів
    print("\n2. Поточні адміністратори:")
    c.execute('SELECT user_id, username, is_admin FROM users WHERE is_admin=1')
    admins = c.fetchall()
    if admins:
        for admin in admins:
            print(f"   ID: {admin[0]}, Username: {admin[1]}, is_admin: {admin[2]}")
    else:
        print("   Адміністраторів не знайдено!")
    
    # 3. Перевіряємо всіх користувачів (перших 5)
    print("\n3. Перші 5 користувачів:")
    c.execute('SELECT user_id, username, is_admin FROM users ORDER BY user_id LIMIT 5')
    users = c.fetchall()
    for user in users:
        print(f"   ID: {user[0]}, Username: {user[1]}, is_admin: {user[2]}")
    
    # 4. Тестуємо додавання адміністратора
    print("\n4. Тест додавання адміністратора:")
    test_id = 123456789
    test_username = "test_admin"
    
    # Додаємо тестового адміністратора
    c.execute('INSERT OR IGNORE INTO users (user_id, is_admin, username) VALUES (?, 1, ?)', (test_id, test_username))
    c.execute('UPDATE users SET is_admin=1, username=? WHERE user_id=?', (test_id, test_username))
    conn.commit()
    
    # Перевіряємо результат
    c.execute('SELECT user_id, username, is_admin FROM users WHERE user_id=?', (test_id,))
    result = c.fetchone()
    print(f"   Результат додавання: {result}")
    
    # Очищаємо тест
    c.execute('DELETE FROM users WHERE user_id=?', (test_id,))
    conn.commit()
    print("   Тестовий адміністратор видалено")
    
    conn.close()
    print("\n✅ Перевірка завершена успішно!")
    
except Exception as e:
    print(f"\n❌ Помилка: {e}")
    import traceback
    traceback.print_exc()
