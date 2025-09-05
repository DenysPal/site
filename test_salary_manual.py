#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os

# Додаємо поточну директорію до шляху
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_salary_system():
    """Тестує систему зарплати вручну"""
    try:
        # Підключаємося до бази даних
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        print("🔍 Тестуємо систему зарплати...")
        
        # 1. Перевіряємо таблиці
        print("\n1. Перевіряємо таблиці:")
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('worker_salary', 'salary_transactions')")
        tables = c.fetchall()
        print(f"   Знайдено таблиці: {[t[0] for t in tables]}")
        
        # 2. Перевіряємо структуру таблиці worker_salary
        print("\n2. Структура таблиці worker_salary:")
        c.execute("PRAGMA table_info(worker_salary)")
        columns = c.fetchall()
        for col in columns:
            print(f"   {col[1]} ({col[2]})")
        
        # 3. Перевіряємо записи для hexwizards
        print("\n3. Записи для hexwizards:")
        c.execute("SELECT * FROM worker_salary WHERE nickname='hexwizards'")
        row = c.fetchone()
        if row:
            print(f"   ID: {row[0]}")
            print(f"   Nickname: {row[1]}")
            print(f"   Total earned: {row[2]}$")
            print(f"   Current month: {row[3]}$")
            print(f"   Wallet: {row[4]}")
            print(f"   Created: {row[5]}")
            print(f"   Updated: {row[6]}")
        else:
            print("   ❌ Запис для hexwizards не знайдено!")
        
        # 4. Перевіряємо транзакції
        print("\n4. Транзакції для hexwizards:")
        c.execute("SELECT * FROM salary_transactions WHERE nickname='hexwizards' ORDER BY timestamp DESC LIMIT 5")
        transactions = c.fetchall()
        if transactions:
            for i, trans in enumerate(transactions, 1):
                print(f"   {i}. {trans[3]} x{trans[4]} = {trans[2]}$ (з {trans[5]}$ по {trans[6]}%) - {trans[7]}")
        else:
            print("   ❌ Транзакції для hexwizards не знайдено!")
        
        # 5. Тестуємо функцію нарахування зарплати
        print("\n5. Тестуємо нарахування зарплати:")
        
        # Симулюємо повідомлення "Новый Возврат x2 🧑‍🏭Воркер: #hexwizards 💰Сумма: 23.0$"
        test_message = """Новый Возврат x2
🧑‍🏭Воркер: #hexwizards
💰Сумма: 23.0$
👨‍💻Вбивер: #d
👨‍💻Саппорт: #d"""
        
        print(f"   Тестове повідомлення: {test_message}")
        
        # Парсимо повідомлення
        lines = test_message.strip().split('\n')
        first_line = lines[0].strip()
        
        # Визначаємо тип та множник
        if "Новый Возврат" in first_line and "прозвон" in first_line:
            transaction_type = "Возврат с прозвоном"
            percentage = 55
        elif "Новый Возврат" in first_line:
            transaction_type = "Возврат"
            percentage = 65
        elif "Новая Оплата" in first_line:
            transaction_type = "Оплата"
            percentage = 75
        else:
            transaction_type = "Невідомий"
            percentage = 0
        
        # Вибираємо множник
        multiplier = 1
        if 'x' in first_line:
            try:
                multiplier_str = first_line.split('x')[-1].strip()
                multiplier = int(multiplier_str)
            except:
                multiplier = 1
        
        # Парсимо дані воркера та суми
        worker_nickname = None
        amount = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('🧑‍🏭Воркер:'):
                worker_nickname = line.split('#')[-1].strip()
            elif line.startswith('💰Сумма:'):
                amount_str = line.split('$')[0].split(':')[-1].strip()
                try:
                    amount = float(amount_str)
                except:
                    amount = 0
        
        print(f"   Розпізнано:")
        print(f"     Тип: {transaction_type}")
        print(f"     Відсоток: {percentage}%")
        print(f"     Множник: x{multiplier}")
        print(f"     Воркер: {worker_nickname}")
        print(f"     Сума: {amount}$")
        
        if worker_nickname and amount:
            # Розраховуємо зарплату
            original_amount = amount
            final_amount = (amount * percentage / 100) * multiplier
            
            print(f"   Розрахунок: {amount}$ × {percentage}% × {multiplier} = {final_amount}$")
            
            # Нараховуємо зарплату
            try:
                # Отримуємо або створюємо запис воркера
                c.execute('SELECT * FROM worker_salary WHERE nickname=?', (worker_nickname,))
                worker = c.fetchone()
                if not worker:
                    c.execute('INSERT INTO worker_salary (nickname, wallet) VALUES (?, ?)', (worker_nickname, None))
                    print(f"   ✅ Створено запис для {worker_nickname}")
                
                # Оновлюємо зарплату
                c.execute('''
                    UPDATE worker_salary 
                    SET total_earned = total_earned + ?, 
                        current_month_earned = current_month_earned + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE nickname = ?
                ''', (final_amount, final_amount, worker_nickname))
                
                # Створюємо запис про транзакцію
                c.execute('''
                    INSERT INTO salary_transactions 
                    (nickname, amount, transaction_type, multiplier, original_amount, percentage, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (worker_nickname, final_amount, transaction_type, multiplier, original_amount, percentage))
                
                conn.commit()
                print(f"   ✅ Зарплату нараховано: +{final_amount}$")
                
                # Перевіряємо оновлені дані
                c.execute('SELECT * FROM worker_salary WHERE nickname=?', (worker_nickname,))
                updated_worker = c.fetchone()
                if updated_worker:
                    print(f"   📊 Оновлені дані:")
                    print(f"     Total earned: {updated_worker[2]}$")
                    print(f"     Current month: {updated_worker[3]}$")
                
            except Exception as e:
                print(f"   ❌ Помилка нарахування: {e}")
        else:
            print("   ❌ Не вдалося розпізнати дані воркера або суми")
        
        conn.close()
        print("\n✅ Тест завершено!")
        
    except Exception as e:
        print(f"❌ Помилка тесту: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_salary_system()
