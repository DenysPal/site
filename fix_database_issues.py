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
        c.execute('ALTER TABLE site_users ADD COLUMN page_code TEXT UNIQUE')
        conn.commit()
        print("✅ Колонка page_code додана")
    else:
        print("✅ Колонка page_code вже існує")
    
    # Заповнюємо page_code для існуючих записів
    c.execute('SELECT COUNT(*) FROM site_users WHERE page_code IS NULL')
    null_count = c.fetchone()[0]
    
    if null_count > 0:
        print(f"Заповнюю page_code для {null_count} записів...")
        
        c.execute('SELECT id FROM site_users ORDER BY created_at')
        users = c.fetchall()
        
        for idx, (user_id,) in enumerate(users):
            series = idx // 100 + 1
            number = idx % 100 + 1
            page_code = f"{series}-{number}"
            
            c.execute('UPDATE site_users SET page_code=? WHERE id=?', (page_code, user_id))
            print(f"  {user_id} -> {page_code}")
        
        conn.commit()
        print("✅ Всі page_code заповнені")
    else:
        print("✅ Всі page_code вже заповнені")
    
    conn.close()

def fix_event_links():
    """Виправляє неіснуючі user_id в event_links"""
    print("\n=== ВИПРАВЛЕННЯ EVENT_LINKS ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Знаходимо неіснуючі user_id
    c.execute("""
        SELECT el.event_code, el.user_id 
        FROM event_links el 
        LEFT JOIN site_users su ON el.user_id = su.id 
        WHERE su.id IS NULL
    """)
    missing = c.fetchall()
    
    if not missing:
        print("✅ Всі event_links мають валідні user_id")
        conn.close()
        return
    
    print(f"Знайдено {len(missing)} неіснуючих user_id:")
    for event_code, user_id in missing:
        print(f"  {event_code} -> {user_id}")
    
    # Отримуємо всі доступні site_user_id
    c.execute('SELECT id FROM site_users ORDER BY created_at DESC')
    available_site_users = [row[0] for row in c.fetchall()]
    
    if not available_site_users:
        print("❌ Немає доступних site_users для виправлення")
        conn.close()
        return
    
    print(f"Доступні site_user_id: {available_site_users}")
    
    # Виправляємо записи
    for event_code, wrong_user_id in missing:
        if available_site_users:
            correct_user_id = available_site_users.pop(0)  # Беремо перший доступний
            c.execute('UPDATE event_links SET user_id=? WHERE event_code=?', 
                     (correct_user_id, event_code))
            print(f"✅ Виправлено: {event_code} -> {correct_user_id}")
        else:
            print(f"❌ Немає більше доступних site_user_id для {event_code}")
    
    conn.commit()
    conn.close()

def verify_fixes():
    """Перевіряє, чи виправлення працюють"""
    print("\n=== ПЕРЕВІРКА ВИПРАВЛЕНЬ ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо page_code
    c.execute("PRAGMA table_info(site_users)")
    columns = [row[1] for row in c.fetchall()]
    
    if 'page_code' in columns:
        c.execute('SELECT COUNT(*) FROM site_users WHERE page_code IS NULL')
        null_count = c.fetchone()[0]
        if null_count == 0:
            print("✅ page_code: всі записи мають значення")
        else:
            print(f"❌ page_code: {null_count} записів без значення")
    else:
        print("❌ page_code: колонка відсутня")
    
    # Перевіряємо event_links
    c.execute("""
        SELECT COUNT(*) 
        FROM event_links el 
        LEFT JOIN site_users su ON el.user_id = su.id 
        WHERE su.id IS NULL
    """)
    invalid_count = c.fetchone()[0]
    
    if invalid_count == 0:
        print("✅ event_links: всі user_id валідні")
    else:
        print(f"❌ event_links: {invalid_count} неіснуючих user_id")
    
    conn.close()

def main():
    """Головна функція"""
    print("🔧 ПОЧАТОК ВИПРАВЛЕННЯ ПРОБЛЕМ БАЗИ ДАНИХ")
    
    try:
        fix_page_code_column()
        fix_event_links()
        verify_fixes()
        print("\n🎉 Виправлення завершено!")
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 