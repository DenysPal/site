#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Швидка перевірка синтаксису main.py
"""

import py_compile
import os

def check_syntax():
    """Перевіряє синтаксис main.py"""
    print("🔍 Перевіряю синтаксис main.py...")
    
    if not os.path.exists('main.py'):
        print("❌ Файл main.py не знайдено")
        return False
    
    try:
        py_compile.compile('main.py', doraise=True)
        print("✅ Синтаксис main.py правильний!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Помилка синтаксису: {e}")
        return False
    except Exception as e:
        print(f"❌ Неочікувана помилка: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Перевірка синтаксису")
    print("=" * 30)
    
    if check_syntax():
        print("\n✅ main.py готовий до запуску!")
    else:
        print("\n❌ main.py має помилки синтаксису")
