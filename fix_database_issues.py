#!/usr/bin/env python3
"""
Скрипт для виправлення проблем з базою даних
"""
import sqlite3
import random
import string

def fix_page_code_column():
    """Додає колонку page_code до таблиці site_users"""
    print("=== ВИПРАВЛЕННЯ КОЛОНКИ PAGE_CODE ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо, чи існує колонка page_code
    c.execute("PRAGMA table_info(site_users)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'page_code' not in columns:
        print("Додаю колонку page_code...")
        
        # Створюємо нову таблицю з колонкою page_code
        c.execute('''
            CREATE TABLE site_users_new (
                id VARCHAR(12) PRIMARY KEY,
                ip VARCHAR(45),
                date_1 VARCHAR(20),
                date_2 VARCHAR(20),
                date_3 VARCHAR(20),
                date_4 VARCHAR(20),
                date_5 VARCHAR(20),
                date_6 VARCHAR(20),
                date_7 VARCHAR(20),
                date_8 VARCHAR(20),
                currency VARCHAR(10),
                street TEXT,
                price DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                page_code TEXT UNIQUE
            )
        ''')
        
        # Копіюємо дані зі старої таблиці
        c.execute('''
            INSERT INTO site_users_new 
            (id, ip, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price, created_at)
            SELECT id, ip, date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, currency, street, price, created_at
            FROM site_users
        ''')
        
        # Видаляємо стару таблицю
        c.execute('DROP TABLE site_users')
        
        # Перейменовуємо нову таблицю
        c.execute('ALTER TABLE site_users_new RENAME TO site_users')
        
        conn.commit()
        print("✅ Колонка page_code додана")
    else:
        print("✅ Колонка page_code вже існує")
    
    # Заповнюємо page_code для існуючих записів
    c.execute('SELECT COUNT(*) FROM site_users WHERE page_code IS NULL')
    null_count = c.fetchone()[0]
    
    if null_count > 0:
        print(f"Заповнюю page_code для {null_count} записів...")
        
        c.execute('SELECT id FROM site_users WHERE page_code IS NULL ORDER BY created_at')
        users = c.fetchall()
        
        for idx, (user_id,) in enumerate(users):
            series = idx // 100 + 1
            number = idx % 100 + 1
            page_code = f"{series}-{number}"
            c.execute('UPDATE site_users SET page_code=? WHERE id=?', (page_code, user_id))
        
        conn.commit()
        print("✅ page_code заповнено")
    else:
        print("✅ Всі записи вже мають page_code")
    
    conn.close()

def fix_event_links_consistency():
    """Виправляє неіснуючі user_id в event_links"""
    print("\n=== ВИПРАВЛЕННЯ EVENT_LINKS ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Знаходимо event_links з неіснуючими user_id
    c.execute('''
        SELECT el.event_code, el.user_id 
        FROM event_links el 
        LEFT JOIN site_users su ON el.user_id = su.id 
        WHERE su.id IS NULL
    ''')
    invalid_links = c.fetchall()
    
    if invalid_links:
        print(f"Знайдено {len(invalid_links)} неіснуючих посилань:")
        for event_code, user_id in invalid_links:
            print(f"  - event_code: {event_code}, user_id: {user_id}")
        
        # Видаляємо неіснуючі посилання
        c.execute('''
            DELETE FROM event_links 
            WHERE user_id NOT IN (SELECT id FROM site_users)
        ''')
        deleted_count = c.rowcount
        conn.commit()
        print(f"✅ Видалено {deleted_count} неіснуючих посилань")
    else:
        print("✅ Всі event_links мають валідні user_id")
    
    conn.close()

def verify_fixes():
    """Перевіряє результат виправлень"""
    print("\n=== ПЕРЕВІРКА РЕЗУЛЬТАТУ ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо колонку page_code
    c.execute("PRAGMA table_info(site_users)")
    columns = [row[1] for row in c.fetchall()]
    if 'page_code' in columns:
        print("✅ Колонка page_code існує")
        
        c.execute('SELECT COUNT(*) FROM site_users WHERE page_code IS NULL')
        null_count = c.fetchone()[0]
        if null_count == 0:
            print("✅ Всі записи мають page_code")
        else:
            print(f"⚠️ {null_count} записів без page_code")
    else:
        print("❌ Колонка page_code відсутня")
    
    # Перевіряємо event_links
    c.execute('''
        SELECT COUNT(*) 
        FROM event_links el 
        LEFT JOIN site_users su ON el.user_id = su.id 
        WHERE su.id IS NULL
    ''')
    invalid_count = c.fetchone()[0]
    if invalid_count == 0:
        print("✅ Всі event_links мають валідні user_id")
    else:
        print(f"❌ {invalid_count} event_links з неіснуючими user_id")
    
    # Загальна статистика
    c.execute('SELECT COUNT(*) FROM site_users')
    site_users_count = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM event_links')
    event_links_count = c.fetchone()[0]
    
    print(f"\n📊 Статистика:")
    print(f"  - site_users: {site_users_count}")
    print(f"  - event_links: {event_links_count}")
    
    conn.close()

def main():
    try:
        fix_page_code_column()
        fix_event_links_consistency()
        verify_fixes()
        print("\n✅ Всі виправлення завершено успішно!")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 