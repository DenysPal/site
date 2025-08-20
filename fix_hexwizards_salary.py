#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Виправлення зарплати для hexwizards згідно з очікуванням
"""

import sqlite3
from datetime import datetime

def fix_hexwizards_salary():
    """Виправляє зарплату для hexwizards"""
    print("=== ВИПРАВЛЕННЯ ЗАРПЛАТИ ДЛЯ HEXWIZARDS ===")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Поточний стан
        print("\n1. Поточний стан:")
        c.execute("SELECT * FROM worker_salary WHERE nickname='hexwizards'")
        worker = c.fetchone()
        
        if worker:
            print(f"   Поточна зарплата: {worker[2]}$")
            print(f"   За місяць: {worker[3]}$")
        
        # Розрахунок згідно з очікуванням: 23$ × 2 = 46$
        original_amount = 23.0
        multiplier = 2
        expected_amount = original_amount * multiplier  # 46$
        
        print(f"\n2. Розрахунок згідно з очікуванням:")
        print(f"   Оригінальна сума: {original_amount}$")
        print(f"   Множник: x{multiplier}")
        print(f"   Очікувана сума: {expected_amount}$")
        print(f"   Відсоток: 65% (для типу 'Возврат')")
        print(f"   Фінальна зарплата: {expected_amount * 0.65:.2f}$")
        
        # Оновлюємо зарплату
        print("\n3. Оновлення зарплати:")
        
        # Видаляємо попередню транзакцію
        c.execute("DELETE FROM salary_transactions WHERE nickname='hexwizards' AND amount=29.9")
        print("   ✅ Попередня транзакція видалена")
        
        # Оновлюємо зарплату воркера
        new_amount = expected_amount * 0.65  # 46$ × 65% = 29.9$
        c.execute('''
            UPDATE worker_salary 
            SET total_earned = ?, 
                current_month_earned = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE nickname = ?
        ''', (new_amount, new_amount, 'hexwizards'))
        
        # Створюємо нову транзакцію
        c.execute('''
            INSERT INTO salary_transactions 
            (nickname, amount, transaction_type, multiplier, original_amount, percentage)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', ('hexwizards', new_amount, 'Возврат', multiplier, expected_amount, 65))
        
        conn.commit()
        print("   ✅ Зарплата оновлена!")
        
        # Перевіряємо результат
        print("\n4. Фінальний результат:")
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
        
        print(f"\n✅ Зарплата для hexwizards виправлена!")
        print(f"   Оригінальна сума: {original_amount}$ × {multiplier} = {expected_amount}$")
        print(f"   Фінальна зарплата: {expected_amount}$ × 65% = {new_amount:.2f}$")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_hexwizards_salary()
