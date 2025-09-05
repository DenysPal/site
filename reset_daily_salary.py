#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import datetime

def reset_daily_earnings():
    """Скидає щоденні заробітки всіх воркерів"""
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Скидаємо щоденні заробітки
        c.execute('UPDATE worker_salary SET current_day_earned = 0.0')
        conn.commit()
        
        print(f"✅ [{datetime.datetime.now()}] Щоденні заробітки всіх воркерів скинуті")
        
        # Показуємо статистику
        c.execute('SELECT nickname, current_day_earned FROM worker_salary')
        workers = c.fetchall()
        
        print(f"📊 Статистика після скидання:")
        for nickname, daily in workers:
            print(f"   #{nickname}: {daily:.2f}$")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ [{datetime.datetime.now()}] Помилка при скиданні щоденних заробітків: {e}")
        return False

if __name__ == "__main__":
    reset_daily_earnings()
