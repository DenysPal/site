#!/usr/bin/env python3
"""
Скрипт для виправлення всіх сторінок івентів - додає правильну обробку page_code
"""

import os
import re
from pathlib import Path

# Список сторінок івентів та їх індексів
EVENT_PAGES = {
    'terroir-and-traditions': 0,
    'collection-co–selection': 1,
    'snucie': 2,
    'art-that-saves-lives': 3,
    'gotong-royong': 4,
    'anna-konik': 5,
    'uncensored': 6,
    'jacek-adamas': 7
}

def fix_page_code_handling(file_path, event_name, event_index):
    """Виправляє обробку page_code на сторінці івенту"""
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не знайдено: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Шукаємо старий код обробки page_code
    old_pattern = r'''  const params = new URLSearchParams\(window\.location\.search\);
  let page_code = params\.get\('page'\);
  if \(!page_code\) \{
    page_code = sessionStorage\.getItem\('page_code'\);
  \}'''
    
    # Новий код з правильною обробкою
    new_code = f'''  const params = new URLSearchParams(window.location.search);
  let page_code = params.get('page');
  
  // Якщо page_code немає в URL, очищаємо застарілі дані з sessionStorage
  if (!page_code) {{
    console.warn('[{event_name.upper()}] No page_code in URL, clearing stale sessionStorage data');
    sessionStorage.removeItem('page_code');
    sessionStorage.removeItem('ticket_price');
    sessionStorage.removeItem('ticket_currency');
    // Не використовуємо sessionStorage fallback для критичних даних
    page_code = null;
  }} else {{
    // Оновлюємо sessionStorage тільки якщо page_code є в URL
    sessionStorage.setItem('page_code', page_code);
    console.log('[{event_name.upper()}] Using page_code from URL:', page_code);
  }}'''
    
    # Замінюємо старий код на новий
    if re.search(old_pattern, content, re.MULTILINE):
        content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE)
        
        # Записуємо оновлений файл
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Виправлено: {event_name} (index {event_index})")
        return True
    else:
        print(f"⚠️  Не знайдено шаблон для заміни в: {event_name}")
        return False

def main():
    """Головна функція"""
    base_dir = Path(__file__).parent / 'events-art.com'
    
    print("🔧 Виправлення обробки page_code на всіх сторінках івентів...")
    print("=" * 60)
    
    fixed_count = 0
    total_count = len(EVENT_PAGES)
    
    for event_name, event_index in EVENT_PAGES.items():
        file_path = base_dir / event_name / 'index.html'
        
        if fix_page_code_handling(file_path, event_name, event_index):
            fixed_count += 1
    
    print("=" * 60)
    print(f"📊 Результат: виправлено {fixed_count} з {total_count} сторінок")
    
    if fixed_count == total_count:
        print("🎉 Всі сторінки успішно виправлені!")
    else:
        print("⚠️  Деякі сторінки потребують ручного виправлення")

if __name__ == '__main__':
    main()
