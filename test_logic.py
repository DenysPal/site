#!/usr/bin/env python3
"""
Тест логіки роботи з page_code
"""

def test_page_code_logic():
    """Тестує логіку роботи з page_code"""
    
    print("🧪 Тестуємо логіку роботи з page_code...")
    
    # Симулюємо різні сценарії
    scenarios = [
        {
            "name": "page_code в URL",
            "url_page": "1-1",
            "storage_page": None,
            "expected": "1-1"
        },
        {
            "name": "page_code в sessionStorage",
            "url_page": None,
            "storage_page": "2-2",
            "expected": "2-2"
        },
        {
            "name": "page_code в URL і sessionStorage (URL має пріоритет)",
            "url_page": "3-3",
            "storage_page": "4-4",
            "expected": "3-3"
        },
        {
            "name": "немає page_code",
            "url_page": None,
            "storage_page": None,
            "expected": None
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 Сценарій: {scenario['name']}")
        
        # Симулюємо JavaScript логіку
        pageCodeFromUrl = scenario['url_page']
        pageCodeFromStorage = scenario['storage_page']
        pageCode = pageCodeFromUrl or pageCodeFromStorage
        
        print(f"   URL page_code: {pageCodeFromUrl}")
        print(f"   Storage page_code: {pageCodeFromStorage}")
        print(f"   Результат: {pageCode}")
        print(f"   Очікуваний: {scenario['expected']}")
        
        if pageCode == scenario['expected']:
            print("   ✅ ПРАВИЛЬНО")
        else:
            print("   ❌ НЕПРАВИЛЬНО")
    
    print("\n🔍 Перевірка обробки даних з API:")
    
    # Тестуємо обробку даних з API
    api_data = "28.06.2025 10:00-22:20"
    print(f"   API дані: '{api_data}'")
    
    # Симулюємо JavaScript розділення
    if ' ' in api_data:
        parts = api_data.split(' ')
        date = parts[0]
        time = ' '.join(parts[1:])
    else:
        date = api_data
        time = ''
    
    print(f"   Розділені дані:")
    print(f"     Дата: '{date}'")
    print(f"     Час: '{time}'")
    
    expected_date = "28.06.2025"
    expected_time = "10:00-22:20"
    
    if date == expected_date and time == expected_time:
        print("   ✅ Розділення даних ПРАВИЛЬНЕ")
    else:
        print("   ❌ Розділення даних НЕПРАВИЛЬНЕ")

if __name__ == "__main__":
    test_page_code_logic() 