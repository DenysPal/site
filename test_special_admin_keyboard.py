#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тест для проверки работы функции get_user_keyboard для специальных админов
"""

from config import SPECIAL_ADMIN_IDS
from main import get_user_keyboard

def test_special_admin_keyboard():
    """Тестируем, что специальные админы получают правильную клавиатуру"""
    print("=== Тест клавиатуры для специальных админов ===")
    print(f"SPECIAL_ADMIN_IDS: {SPECIAL_ADMIN_IDS}")
    
    for admin_id in SPECIAL_ADMIN_IDS:
        print(f"\nТестируем admin_id: {admin_id}")
        try:
            kb = get_user_keyboard(admin_id)
            print(f"Клавиатура получена: {kb}")
            print(f"Тип клавиатуры: {type(kb)}")
            
            # Проверяем, что это special_admin_menu_kb
            if hasattr(kb, 'keyboard'):
                print(f"Кнопки в клавиатуре:")
                for row in kb.keyboard:
                    for button in row:
                        print(f"  - {button.text}")
            else:
                print("Клавиатура не имеет атрибута 'keyboard'")
                
        except Exception as e:
            print(f"Ошибка при получении клавиатуры: {e}")
    
    print("\n=== Тест завершен ===")

if __name__ == "__main__":
    test_special_admin_keyboard()
