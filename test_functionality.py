#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки функціоналу
"""
import sqlite3
import json
import os

def test_database():
    """Тестує структуру бази даних"""
    print("=== ТЕСТ БАЗИ ДАНИХ ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо таблиці
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    print(f"Знайдені таблиці: {tables}")
    
    # Перевіряємо структуру users
    c.execute("PRAGMA table_info(users)")
    users_columns = [row[1] for row in c.fetchall()]
    print(f"Колонки users: {users_columns}")
    
    # Перевіряємо структуру site_users
    c.execute("PRAGMA table_info(site_users)")
    site_users_columns = [row[1] for row in c.fetchall()]
    print(f"Колонки site_users: {site_users_columns}")
    
    # Перевіряємо структуру event_links
    c.execute("PRAGMA table_info(event_links)")
    event_links_columns = [row[1] for row in c.fetchall()]
    print(f"Колонки event_links: {event_links_columns}")
    
    # Перевіряємо дані
    c.execute("SELECT COUNT(*) FROM users")
    users_count = c.fetchone()[0]
    print(f"Кількість користувачів: {users_count}")
    
    c.execute("SELECT COUNT(*) FROM site_users")
    site_users_count = c.fetchone()[0]
    print(f"Кількість site_users: {site_users_count}")
    
    c.execute("SELECT COUNT(*) FROM event_links")
    event_links_count = c.fetchone()[0]
    print(f"Кількість event_links: {event_links_count}")
    
    conn.close()
    return True

def test_page_code_system():
    """Тестує систему page_code"""
    print("\n=== ТЕСТ СИСТЕМИ PAGE_CODE ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо, чи є page_code у всіх записах
    c.execute("SELECT COUNT(*) FROM site_users WHERE page_code IS NULL")
    null_count = c.fetchone()[0]
    print(f"Записів без page_code: {null_count}")
    
    if null_count > 0:
        print("❌ Є записи без page_code!")
        return False
    
    # Перевіряємо унікальність page_code
    c.execute("SELECT page_code, COUNT(*) FROM site_users GROUP BY page_code HAVING COUNT(*) > 1")
    duplicates = c.fetchall()
    if duplicates:
        print(f"❌ Знайдені дублікати page_code: {duplicates}")
        return False
    
    print("✅ Система page_code працює коректно")
    conn.close()
    return True

def test_event_links_consistency():
    """Тестує консистентність event_links"""
    print("\n=== ТЕСТ КОНСИСТЕНТНОСТІ EVENT_LINKS ===")
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Перевіряємо, чи всі user_id з event_links існують в site_users
    c.execute("""
        SELECT el.event_code, el.user_id 
        FROM event_links el 
        LEFT JOIN site_users su ON el.user_id = su.id 
        WHERE su.id IS NULL
    """)
    missing = c.fetchall()
    
    if missing:
        print(f"❌ Знайдені event_links з неіснуючими user_id: {missing}")
        return False
    
    print("✅ Всі event_links мають валідні user_id")
    conn.close()
    return True

def test_file_structure():
    """Тестує структуру файлів"""
    print("\n=== ТЕСТ СТРУКТУРИ ФАЙЛІВ ===")
    
    required_files = [
        'main.py',
        'server.py',
        'config.py',
        'users.db'
    ]
    
    required_dirs = [
        'events-art.com',
        'tickets'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} існує")
        else:
            print(f"❌ {file} відсутній")
            return False
    
    for dir in required_dirs:
        if os.path.exists(dir):
            print(f"✅ {dir}/ існує")
        else:
            print(f"❌ {dir}/ відсутній")
            return False
    
    return True

def test_events_json():
    """Тестує файл events.json"""
    print("\n=== ТЕСТ EVENTS.JSON ===")
    
    events_file = os.path.join('events-art.com', 'events.json')
    if not os.path.exists(events_file):
        print("❌ events.json не існує")
        return False
    
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
        print(f"✅ events.json завантажено, {len(events)} подій")
        return True
    except Exception as e:
        print(f"❌ Помилка завантаження events.json: {e}")
        return False

def main():
    """Головна функція тестування"""
    print("🔍 ПОЧАТОК ТЕСТУВАННЯ ФУНКЦІОНАЛУ")
    
    tests = [
        test_database,
        test_page_code_system,
        test_event_links_consistency,
        test_file_structure,
        test_events_json
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Тест {test.__name__} не пройшов")
        except Exception as e:
            print(f"❌ Помилка в тесті {test.__name__}: {e}")
    
    print(f"\n=== РЕЗУЛЬТАТ ===")
    print(f"Пройдено: {passed}/{total} тестів")
    
    if passed == total:
        print("🎉 Всі тести пройшли успішно!")
        return True
    else:
        print("⚠️ Є проблеми, які потрібно виправити")
        return False

if __name__ == "__main__":
    main() 