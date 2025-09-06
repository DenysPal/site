#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import sys
import os

# Додаємо поточну папку до шляху
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import validate_ticket_data

def test_validation():
    """Тест валідації даних квитка"""
    print("🧪 Тестування валідації даних квитка...")
    
    # Тестові дані
    test_cases = [
        ("Test User", "21:00", "23.05", "40 €", "Test Address"),  # Валідні дані
        ("", "21:00", "23.05", "40 €", "Test Address"),  # Порожнє ім'я
        ("Test User", "", "23.05", "40 €", "Test Address"),  # Порожній час
        ("Test User", "21:00", "", "40 €", "Test Address"),  # Порожня дата
        ("Test User", "21:00", "23.05", "", "Test Address"),  # Порожня ціна
        ("Test User", "21:00", "23.05", "40 €", ""),  # Порожня адреса
    ]
    
    for i, (name, time, date, price, address) in enumerate(test_cases):
        print(f"\n📋 Тест {i+1}: {name}, {time}, {date}, {price}, {address}")
        errors = validate_ticket_data(name, time, date, price, address)
        if errors:
            print(f"❌ Помилки: {errors}")
        else:
            print("✅ Валідація пройшла")

if __name__ == "__main__":
    test_validation()
