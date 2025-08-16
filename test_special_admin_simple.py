#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой тест для проверки работы функции get_user_keyboard
"""

# Импортируем только необходимые части
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import SPECIAL_ADMIN_IDS

def test_special_admin_ids():
    """Тестируем, что SPECIAL_ADMIN_IDS правильно импортированы"""
    print("=== Тест SPECIAL_ADMIN_IDS ===")
    print(f"SPECIAL_ADMIN_IDS: {SPECIAL_ADMIN_IDS}")
    print(f"Тип: {type(SPECIAL_ADMIN_IDS)}")
    print(f"Длина: {len(SPECIAL_ADMIN_IDS)}")
    
    for admin_id in SPECIAL_ADMIN_IDS:
        print(f"  - {admin_id} (тип: {type(admin_id)})")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_special_admin_ids()
