#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Демонстрація роботи системи зарплати воркерів
"""

import sqlite3
from datetime import datetime

def demo_salary_system():
    """Демонструє роботу системи зарплати"""
    print("=== ДЕМОНСТРАЦІЯ СИСТЕМИ ЗАРПЛАТИ ===\n")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Показуємо поточних воркерів
        print("👥 Поточні воркери:")
        c.execute('SELECT nickname, total_earned, current_month_earned, wallet FROM worker_salary')
        workers = c.fetchall()
        
        if not workers:
            print("   Воркерів поки немає")
        else:
            for worker in workers:
                nickname, total, monthly, wallet = worker
                print(f"   #{nickname}: {total}$ (місяць: {monthly}$) - {wallet or 'Без кошелька'}")
        
        print("\n📊 Статистика транзакцій:")
        c.execute('''
            SELECT transaction_type, COUNT(*), SUM(amount), AVG(amount)
            FROM salary_transactions 
            GROUP BY transaction_type
        ''')
        stats = c.fetchall()
        
        if not stats:
            print("   Транзакцій поки немає")
        else:
            for stat in stats:
                trans_type, count, total_amount, avg_amount = stat
                print(f"   {trans_type}: {count} транзакцій, всього: {total_amount}$ (середнє: {avg_amount:.2f}$)")
        
        print("\n💰 Приклади розрахунків зарплати:")
        examples = [
            ("Новая Оплата x1", 100, 75, "75% від суми"),
            ("Новая Оплата x2", 100, 150, "75% від суми × 2"),
            ("Новый Возврат x1", 100, 65, "65% від суми"),
            ("Новый Возврат x3", 100, 195, "65% від суми × 3"),
            ("Новый Возврат с прозвоном x1", 200, 110, "55% від суми"),
            ("Новый Возврат с прозвоном x5", 200, 550, "55% від суми × 5")
        ]
        
        for example, amount, result, explanation in examples:
            print(f"   {example}: {amount}$ → {result}$ ({explanation})")
        
        print("\n🔧 Команди для тестування:")
        print("   /salary_info - інформація про зарплату")
        print("   /test_salary - тест системи (тільки для адмінів)")
        print("   /worker_stats - статистика воркерів (тільки для адмінів)")
        print("   /reset_monthly - скидання місячних заробітків (тільки для адмінів)")
        
        print("\n✅ Система готова до роботи!")
        print("   Просто надішліть повідомлення в канал виплат і зарплата буде нарахована автоматично!")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    demo_salary_system()
