#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Додавання пропущеної зарплати для hexwizards
"""

import sqlite3
from datetime import datetime

def add_missing_salary():
    """Додає пропущену зарплату для hexwizards"""
    print("=== ДОДАВАННЯ ПРОПУЩЕНОЇ ЗАРПЛАТИ ===\n")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Перевіряємо поточний стан
        print("1. Поточний стан hexwizards:")
        c.execute("SELECT * FROM worker_salary WHERE nickname='hexwizards'")
        worker = c.fetchone()
        
        if worker:
            print(f"   Поточна зарплата: {worker[2]}$ (загальна), {worker[3]}$ (за місяць)")
        else:
            print("   Воркер не знайдено!")
            return
        
        # Додаємо першу транзакцію: Возврат с прозвоном x2
        print("\n2. Додаємо 'Возврат с прозвоном x2':")
        amount1 = 1212.0 * 0.55 * 2  # 1212$ × 55% × 2
        print(f"   1212$ × 55% × 2 = {amount1}$")
        
        # Оновлюємо зарплату
        c.execute('''
            UPDATE worker_salary 
            SET total_earned = total_earned + ?, 
                current_month_earned = current_month_earned + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE nickname = ?
        ''', (amount1, amount1, 'hexwizards'))
        
        # Створюємо транзакцію
        c.execute('''
            INSERT INTO salary_transactions 
            (nickname, amount, transaction_type, multiplier, original_amount, percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('hexwizards', amount1, 'Возврат с прозвоном', 2, 1212.0, 55))
        
        print(f"   ✅ Додано: +{amount1}$")
        
        # Додаємо другу транзакцію: Возврат x2
        print("\n3. Додаємо 'Возврат x2':")
        amount2 = 12.0 * 0.65 * 2  # 12$ × 65% × 2
        print(f"   12$ × 65% × 2 = {amount2}$")
        
        # Оновлюємо зарплату
        c.execute('''
            UPDATE worker_salary 
            SET total_earned = total_earned + ?, 
                current_month_earned = current_month_earned + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE nickname = ?
        ''', (amount2, amount2, 'hexwizards'))
        
        # Створюємо транзакцію
        c.execute('''
            INSERT INTO salary_transactions 
            (nickname, amount, transaction_type, multiplier, original_amount, percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('hexwizards', amount2, 'Возврат', 2, 12.0, 65))
        
        print(f"   ✅ Додано: +{amount2}$")
        
        # Загальна додана сума
        total_added = amount1 + amount2
        print(f"\n💰 Загальна додана сума: +{total_added}$")
        
        conn.commit()
        
        # Перевіряємо результат
        print("\n4. Оновлений стан:")
        c.execute("SELECT * FROM worker_salary WHERE nickname='hexwizards'")
        updated_worker = c.fetchone()
        
        if updated_worker:
            print(f"   Всього заробив: {updated_worker[2]}$")
            print(f"   За місяць: {updated_worker[3]}$")
        
        # Перевіряємо всі транзакції
        print("\n5. Всі транзакції hexwizards:")
        c.execute("SELECT * FROM salary_transactions WHERE nickname='hexwizards' ORDER BY timestamp DESC")
        transactions = c.fetchall()
        
        for i, trans in enumerate(transactions, 1):
            print(f"   {i}. {trans[3]}: +{trans[2]}$ (x{trans[4]}, {trans[6]}%) - {trans[7]}")
        
        print(f"\n✅ Зарплата успішно оновлена!")
        print(f"   Тепер в меню буде показано: {updated_worker[2]}$ (загальна) та {updated_worker[3]}$ (за місяць)")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_missing_salary()
