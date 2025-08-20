#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для тестування системи зарплати воркерів
"""

import sqlite3
import json
from datetime import datetime

def test_salary_system():
    """Тестує систему зарплати"""
    print("=== ТЕСТ СИСТЕМИ ЗАРПЛАТИ ВОРКЕРІВ ===")
    
    try:
        # Підключаємося до бази даних
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Перевіряємо структуру таблиць
        print("\n1. Перевірка структури таблиць:")
        
        # Таблиця worker_salary
        c.execute("PRAGMA table_info(worker_salary)")
        worker_columns = c.fetchall()
        print("   Таблиця worker_salary:")
        for col in worker_columns:
            print(f"     {col[1]} ({col[2]})")
        
        # Таблиця salary_transactions
        c.execute("PRAGMA table_info(salary_transactions)")
        trans_columns = c.fetchall()
        print("   Таблиця salary_transactions:")
        for col in trans_columns:
            print(f"     {col[1]} ({col[2]})")
        
        # Тестуємо створення воркера
        print("\n2. Тест створення воркера:")
        test_nickname = "testworker"
        
        # Перевіряємо, чи існує воркер
        c.execute('SELECT * FROM worker_salary WHERE nickname=?', (test_nickname,))
        existing_worker = c.fetchone()
        
        if existing_worker:
            print(f"   ✅ Воркер {test_nickname} вже існує")
        else:
            # Створюємо тестового воркера
            c.execute('''
                INSERT INTO worker_salary (nickname, wallet) 
                VALUES (?, ?)
            ''', (test_nickname, "test_wallet_address"))
            conn.commit()
            print(f"   ✅ Створено тестового воркера {test_nickname}")
        
        # Тестуємо нарахування зарплати
        print("\n3. Тест нарахування зарплати:")
        
        # Симулюємо різні типи транзакцій
        test_transactions = [
            {
                'nickname': test_nickname,
                'amount': 75.0,  # 100 * 75% / 100
                'transaction_type': 'Оплата',
                'multiplier': 1,
                'original_amount': 100.0,
                'percentage': 75
            },
            {
                'nickname': test_nickname,
                'amount': 130.0,  # 100 * 65% / 100 * 2
                'transaction_type': 'Возврат',
                'multiplier': 2,
                'original_amount': 100.0,
                'percentage': 65
            },
            {
                'nickname': test_nickname,
                'amount': 110.0,  # 200 * 55% / 100
                'transaction_type': 'Возврат с прозвоном',
                'multiplier': 1,
                'original_amount': 200.0,
                'percentage': 55
            }
        ]
        
        for i, trans in enumerate(test_transactions, 1):
            # Додаємо транзакцію
            c.execute('''
                INSERT INTO salary_transactions 
                (nickname, amount, transaction_type, multiplier, original_amount, percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (trans['nickname'], trans['amount'], trans['transaction_type'], 
                  trans['multiplier'], trans['original_amount'], trans['percentage']))
            
            # Оновлюємо зарплату воркера
            c.execute('''
                UPDATE worker_salary 
                SET total_earned = total_earned + ?, 
                    current_month_earned = current_month_earned + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE nickname = ?
            ''', (trans['amount'], trans['amount'], trans['nickname']))
            
            print(f"   ✅ Транзакція {i}: {trans['transaction_type']} +{trans['amount']:.2f}$ (x{trans['multiplier']}, {trans['percentage']}%)")
        
        conn.commit()
        
        # Перевіряємо результат
        print("\n4. Перевірка результатів:")
        c.execute('SELECT * FROM worker_salary WHERE nickname=?', (test_nickname,))
        worker = c.fetchone()
        
        if worker:
            print(f"   Воркер: {worker[1]}")
            print(f"   Всього заробив: {worker[2]}$")
            print(f"   За місяць: {worker[3]}$")
            print(f"   Кошелек: {worker[4]}")
        
        # Перевіряємо транзакції
        c.execute('SELECT * FROM salary_transactions WHERE nickname=? ORDER BY timestamp DESC', (test_nickname,))
        transactions = c.fetchall()
        
        print(f"   Кількість транзакцій: {len(transactions)}")
        for i, trans in enumerate(transactions, 1):
            print(f"   {i}. {trans[3]}: +{trans[2]}$ (x{trans[4]}, {trans[6]}%) - {trans[7]}")
        
        # Тестуємо функції
        print("\n5. Тест функцій:")
        
        # Функція get_worker_salary
        def get_worker_salary(nickname):
            c.execute('SELECT * FROM worker_salary WHERE nickname=?', (nickname,))
            row = c.fetchone()
            if row:
                return {
                    'id': row[0],
                    'nickname': row[1],
                    'total_earned': float(row[2]) if row[2] else 0.0,
                    'current_month_earned': float(row[3]) if row[3] else 0.0,
                    'wallet': row[4],
                    'created_at': row[5],
                    'updated_at': row[6]
                }
            return None
        
        worker_data = get_worker_salary(test_nickname)
        if worker_data:
            print(f"   ✅ get_worker_salary: {worker_data['nickname']} - {worker_data['total_earned']}$")
        
        # Функція get_worker_transactions
        def get_worker_transactions(nickname, limit=10):
            c.execute('''
                SELECT * FROM salary_transactions 
                WHERE nickname = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (nickname, limit))
            rows = c.fetchall()
            transactions = []
            for row in rows:
                transactions.append({
                    'id': row[0],
                    'nickname': row[1],
                    'amount': float(row[2]) if row[2] else 0.0,
                    'transaction_type': row[3],
                    'multiplier': row[4],
                    'original_amount': float(row[5]) if row[5] else 0.0,
                    'percentage': row[6],
                    'timestamp': row[7]
                })
            return transactions
        
        transactions_data = get_worker_transactions(test_nickname, 5)
        print(f"   ✅ get_worker_transactions: {len(transactions_data)} транзакцій")
        
        print("\n✅ Тест системи зарплати завершено успішно!")
        
    except Exception as e:
        print(f"❌ Помилка при тестуванні: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_salary_system()
