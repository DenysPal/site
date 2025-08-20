#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест відображення профілю з зарплатою
"""

import sqlite3
import json
from datetime import datetime

def test_profile_display():
    """Тестує відображення профілю з зарплатою"""
    print("=== ТЕСТ ВІДОБРАЖЕННЯ ПРОФІЛЮ ===\n")
    
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Симулюємо функцію show_profile для hexwizards
        nickname = "hexwizards"
        
        # Отримуємо дані користувача
        c.execute('SELECT * FROM users WHERE username=?', (nickname,))
        db_user = c.fetchone()
        
        if db_user:
            user_id = db_user[0]
            username = db_user[3]
            last_submit = db_user[2]
            form_json = json.loads(db_user[8]) if db_user[8] else {}
            
            print(f"👤 Дані користувача:")
            print(f"   User ID: {user_id}")
            print(f"   Username: {username}")
            print(f"   Last submit: {last_submit}")
            print(f"   Form JSON: {form_json}")
            
            # Форматуємо дату вступу
            join_date = last_submit[:10] if last_submit else "-"
            if join_date != "-":
                try:
                    join_date = datetime.fromisoformat(last_submit).strftime('%d-%m-%Y')
                except:
                    pass
            
            print(f"   Дата вступу: {join_date}")
            
            # Отримуємо зарплату з нової таблиці
            worker_salary = None
            c.execute('SELECT * FROM worker_salary WHERE nickname=?', (nickname,))
            salary_row = c.fetchone()
            
            if salary_row:
                worker_salary = {
                    'id': salary_row[0],
                    'nickname': salary_row[1],
                    'total_earned': float(salary_row[2]) if salary_row[2] else 0.0,
                    'current_month_earned': float(salary_row[3]) if salary_row[3] else 0.0,
                    'wallet': salary_row[4],
                    'created_at': salary_row[5],
                    'updated_at': salary_row[6]
                }
                print(f"   ✅ Зарплата знайдена в таблиці worker_salary")
            else:
                print(f"   ❌ Зарплата не знайдена в таблиці worker_salary")
            
            # Формуємо профіль як у боті
            if worker_salary:
                earned_total = worker_salary['total_earned']
                current_month_earned = worker_salary['current_month_earned']
                wallet = worker_salary['wallet']
            else:
                earned_total = form_json.get('earned_total', 0)
                current_month_earned = form_json.get('earned_june', 0)
                wallet = form_json.get('wallet', None)
            
            # Форматуємо поточний місяць
            current_month = datetime.now().strftime('%B').title()
            
            wallet_str = wallet if wallet else '<b>Не установлен</b> <b>❗️</b>'
            
            print(f"\n📱 Профіль, який побачить користувач:")
            print("=" * 50)
            profile_text = (
                '«<b>Ваш профиль:</b>»\n'
                f'<b>Псевдоним:</b> <code>#{nickname}</code>\n'
                f'<b>Дата вступления:</b> <code>{join_date}</code>\n'
                '💰 <b>Заработано:</b>\n'
                f'├ <b>Всего:</b> <code>{earned_total:.2f}$</code>\n'
                f'└ <b>За {current_month}:</b> <code>{current_month_earned:.2f}$</code>\n'
                '💳 <b>USDT BEP-20 кошелек:</b>\n'
                f'└ {wallet_str}'
            )
            print(profile_text)
            print("=" * 50)
            
            # Перевіряємо транзакції
            print(f"\n💰 Деталі зарплати:")
            c.execute('SELECT * FROM salary_transactions WHERE nickname=? ORDER BY timestamp DESC', (nickname,))
            transactions = c.fetchall()
            
            if transactions:
                for i, trans in enumerate(transactions, 1):
                    print(f"   {i}. {trans[3]}: +{trans[2]}$ (x{trans[4]}, {trans[6]}%) - {trans[7]}")
            else:
                print("   Транзакцій не знайдено")
            
            print(f"\n✅ Профіль готовий до відображення!")
            print(f"   Користувач побачить зарплату: {earned_total:.2f}$ (загальна) та {current_month_earned:.2f}$ (за місяць)")
            
        else:
            print(f"❌ Користувач {nickname} не знайдено")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_profile_display()
