#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест нарахування зарплати для воркера hexwizards
"""

import sqlite3
from datetime import datetime

def test_hexwizards_salary():
    """Тестує нарахування зарплати для hexwizards"""
    print("=== ТЕСТ ЗАРПЛАТИ ДЛЯ HEXWIZARDS ===")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Перевіряємо поточний стан
        print("\n1. Поточний стан:")
        c.execute("SELECT * FROM worker_salary WHERE nickname='hexwizards'")
        worker = c.fetchone()
        
        if worker:
            print(f"   ✅ Воркер hexwizards існує:")
            print(f"      ID: {worker[0]}")
            print(f"      Псевдонім: {worker[1]}")
            print(f"      Всього заробив: {worker[2]}$")
            print(f"      За місяць: {worker[3]}$")
            print(f"      Кошелек: {worker[4]}")
        else:
            print("   ❌ Воркер hexwizards не знайдено в таблиці зарплати")
        
        # Перевіряємо користувача в основній таблиці
        c.execute("SELECT user_id, username FROM users WHERE username='hexwizards'")
        user = c.fetchone()
        
        if user:
            print(f"   ✅ Користувач hexwizards знайдено в основній таблиці:")
            print(f"      User ID: {user[0]}")
            print(f"      Username: {user[1]}")
        else:
            print("   ❌ Користувач hexwizards не знайдено")
        
        # Симулюємо нарахування зарплати
        print("\n2. Симуляція нарахування зарплати:")
        
        # Розрахунок: 23$ × 65% × 2 = 29.9$
        original_amount = 23.0
        percentage = 65
        multiplier = 2
        calculated_amount = (original_amount * percentage / 100) * multiplier
        
        print(f"   Оригінальна сума: {original_amount}$")
        print(f"   Відсоток: {percentage}%")
        print(f"   Множник: x{multiplier}")
        print(f"   Розрахункова зарплата: {calculated_amount}$")
        
        # Створюємо або оновлюємо воркера
        if not worker:
            print("   Створюємо запис воркера...")
            c.execute('''
                INSERT INTO worker_salary (nickname, total_earned, current_month_earned, wallet) 
                VALUES (?, ?, ?, ?)
            ''', ('hexwizards', calculated_amount, calculated_amount, '1'))
        else:
            print("   Оновлюємо зарплату воркера...")
            c.execute('''
                UPDATE worker_salary 
                SET total_earned = total_earned + ?, 
                    current_month_earned = current_month_earned + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE nickname = ?
            ''', (calculated_amount, calculated_amount, 'hexwizards'))
        
        # Створюємо транзакцію
        print("   Створюємо транзакцію...")
        c.execute('''
            INSERT INTO salary_transactions 
            (nickname, amount, transaction_type, multiplier, original_amount, percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('hexwizards', calculated_amount, 'Возврат', multiplier, original_amount, percentage))
        
        conn.commit()
        print("   ✅ Зарплата нарахована!")
        
        # Перевіряємо результат
        print("\n3. Результат:")
        c.execute("SELECT * FROM worker_salary WHERE nickname='hexwizards'")
        updated_worker = c.fetchone()
        
        if updated_worker:
            print(f"   Воркер: {updated_worker[1]}")
            print(f"   Всього заробив: {updated_worker[2]}$")
            print(f"   За місяць: {updated_worker[3]}$")
            print(f"   Кошелек: {updated_worker[4]}")
        
        # Перевіряємо транзакції
        c.execute("SELECT * FROM salary_transactions WHERE nickname='hexwizards' ORDER BY timestamp DESC")
        transactions = c.fetchall()
        
        print(f"   Кількість транзакцій: {len(transactions)}")
        for i, trans in enumerate(transactions, 1):
            print(f"   {i}. {trans[3]}: +{trans[2]}$ (x{trans[4]}, {trans[6]}%) - {trans[7]}")
        
        print(f"\n✅ Зарплата для hexwizards успішно нарахована: +{calculated_amount}$")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_hexwizards_salary()
