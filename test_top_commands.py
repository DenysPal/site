#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест нових команд топ воркерів
"""

import sqlite3
from datetime import datetime

def test_top_commands():
    """Тестує нові команди топ воркерів"""
    
    # Підключаємося до бази даних
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    print("🧪 Тест команд топ воркерів")
    print("=" * 50)
    
    # Тест 1: Перевіряємо чи існує колонка current_day_earned
    try:
        c.execute('SELECT current_day_earned FROM worker_salary LIMIT 1')
        print("✅ Колонка current_day_earned існує")
    except sqlite3.OperationalError as e:
        print(f"❌ Колонка current_day_earned не існує: {e}")
        return
    
    # Тест 2: Перевіряємо загальну кількість воркерів
    c.execute('SELECT COUNT(*) FROM worker_salary')
    total_workers = c.fetchone()[0]
    print(f"📊 Загальна кількість воркерів: {total_workers}")
    
    # Тест 3: Топ за день
    c.execute('''
        SELECT nickname, current_day_earned 
        FROM worker_salary 
        WHERE current_day_earned > 0 
        ORDER BY current_day_earned DESC 
        LIMIT 10
    ''')
    day_workers = c.fetchall()
    print(f"🌅 Воркерів з заробітком за день: {len(day_workers)}")
    for i, (nickname, earned) in enumerate(day_workers[:3], 1):
        print(f"   {i}. #{nickname} - {earned:.1f}$")
    
    # Тест 4: Топ за місяць
    c.execute('''
        SELECT nickname, current_month_earned 
        FROM worker_salary 
        WHERE current_month_earned > 0 
        ORDER BY current_month_earned DESC 
        LIMIT 10
    ''')
    month_workers = c.fetchall()
    print(f"📅 Воркерів з заробітком за місяць: {len(month_workers)}")
    for i, (nickname, earned) in enumerate(month_workers[:3], 1):
        print(f"   {i}. #{nickname} - {earned:.1f}$")
    
    # Тест 5: Топ за весь час
    c.execute('''
        SELECT nickname, total_earned 
        FROM worker_salary 
        WHERE total_earned > 0 
        ORDER BY total_earned DESC 
        LIMIT 10
    ''')
    all_time_workers = c.fetchall()
    print(f"💰 Воркерів з заробітком за весь час: {len(all_time_workers)}")
    for i, (nickname, earned) in enumerate(all_time_workers[:3], 1):
        print(f"   {i}. #{nickname} - {earned:.1f}$")
    
    # Тест 6: Статистика транзакцій
    c.execute('SELECT COUNT(*), SUM(amount) FROM salary_transactions')
    stats = c.fetchone()
    total_profits = stats[0] if stats[0] else 0
    total_amount = stats[1] if stats[1] else 0.0
    print(f"📈 Загальна кількість транзакцій: {total_profits}")
    print(f"💵 Загальна сума виплат: {total_amount:.0f}$")
    
    # Тест 7: Статистика за сьогодні
    c.execute('''
        SELECT COUNT(*), SUM(amount) 
        FROM salary_transactions 
        WHERE DATE(timestamp) = DATE('now')
    ''')
    today_stats = c.fetchone()
    today_profits = today_stats[0] if today_stats[0] else 0
    today_amount = today_stats[1] if today_stats[1] else 0.0
    print(f"📅 Транзакції за сьогодні: {today_profits}")
    print(f"🌅 Сума за сьогодні: {today_amount:.0f}$")
    
    # Тест 8: Статистика за поточний місяць
    current_month = datetime.now().strftime('%Y-%m')
    c.execute('''
        SELECT COUNT(*), SUM(amount) 
        FROM salary_transactions 
        WHERE strftime('%Y-%m', timestamp) = ?
    ''', (current_month,))
    month_stats = c.fetchone()
    month_profits = month_stats[0] if month_stats[0] else 0
    month_amount = month_stats[1] if month_stats[1] else 0.0
    print(f"📆 Транзакції за поточний місяць: {month_profits}")
    print(f"💰 Сума за поточний місяць: {month_amount:.0f}$")
    
    # Тест 9: Дата старту проекту
    c.execute('SELECT MIN(DATE(timestamp)) FROM salary_transactions')
    start_date = c.fetchone()[0]
    if start_date:
        start_date_formatted = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d.%m.%Y')
        print(f"🚀 Дата старту проекту: {start_date_formatted}")
    else:
        print("🚀 Дата старту проекту: 01.09.2025 (за замовчуванням)")
    
    conn.close()
    print("=" * 50)
    print("✅ Тест завершено успішно!")

if __name__ == "__main__":
    test_top_commands()
