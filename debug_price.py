#!/usr/bin/env python3
"""
Скрипт для дебагу ціни в базі даних
"""

import sqlite3

def debug_price_for_page_code(page_code):
    """Дебагує ціну для конкретного page_code"""
    print(f"🔍 Дебаг ціни для page_code: {page_code}")
    
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        print("\n📊 Структура таблиці event_links:")
        cursor.execute("PRAGMA table_info(event_links)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        print("\n📊 Структура таблиці site_users:")
        cursor.execute("PRAGMA table_info(site_users)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        print(f"\n📊 Записи в event_links для {page_code}:")
        cursor.execute("SELECT * FROM event_links WHERE event_code=?", (page_code,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"   {row}")
        
        print(f"\n📊 Записи в site_users для {page_code}:")
        cursor.execute("SELECT * FROM site_users WHERE page_code=?", (page_code,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"   {row}")
        
        print("\n📊 Пошук записів з ціною 90:")
        cursor.execute("SELECT page_code, price, currency FROM site_users WHERE price=90 OR price='90'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   page_code: {row[0]}, price: {row[1]}, currency: {row[2]}")
        
        print("\n📊 Пошук записів з ціною 45:")
        cursor.execute("SELECT page_code, price, currency FROM site_users WHERE price=45 OR price='45'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   page_code: {row[0]}, price: {row[1]}, currency: {row[2]}")
        
        print("\n📊 Всі записи з event_links:")
        cursor.execute("SELECT * FROM event_links ORDER BY event_code LIMIT 10")
        rows = cursor.fetchall()
        for row in rows:
            print(f"   {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Помилка: {e}")

if __name__ == "__main__":
    print("🚀 Запуск дебагу ціни...")
    print("=" * 50)
    
    # Дебагуємо ваш page_code
    debug_price_for_page_code('1-98')
    
    print("\n" + "=" * 50)
    print("✅ Дебаг завершено!")
    print("\n🔍 Що шукати:")
    print("1. Які колонки є в event_links")
    print("2. Які колонки є в site_users")
    print("3. Де зберігається ціна")
    print("4. Яка ціна вказана для 1-98")
    print("5. Чи є записи з ціною 90")
    print("6. Чи є записи з ціною 45")
