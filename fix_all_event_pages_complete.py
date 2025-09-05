#!/usr/bin/env python3
"""
Повний скрипт для виправлення всіх сторінок івентів - додає правильну обробку page_code
Включає спеціальну обробку для Snucie та інших особливих випадків
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

def fix_standard_page_code_handling(content, event_name, event_index):
    """Виправляє стандартну обробку page_code"""
    
    # Шукаємо стандартний патерн
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
    
    if re.search(old_pattern, content, re.MULTILINE):
        content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE)
        return content, True
    
    return content, False

def fix_alternative_page_code_handling(content, event_name):
    """Виправляє альтернативні патерни обробки page_code"""
    
    # Патерн для getParam функції
    old_pattern2 = r'''  let page_code = getParam\('page'\);
  if \(!page_code\) \{
    page_code = sessionStorage\.getItem\('page_code'\);
  \}'''
    
    new_code2 = f'''  let page_code = getParam('page');
  
  // Якщо page_code немає в URL, очищаємо застарілі дані з sessionStorage
  if (!page_code) {{
    console.warn('[{event_name.upper()}-ALT] No page_code in URL, clearing stale sessionStorage data');
    sessionStorage.removeItem('page_code');
    sessionStorage.removeItem('ticket_price');
    sessionStorage.removeItem('ticket_currency');
    // Не використовуємо sessionStorage fallback для критичних даних
    page_code = null;
  }} else {{
    // Оновлюємо sessionStorage тільки якщо page_code є в URL
    sessionStorage.setItem('page_code', page_code);
    console.log('[{event_name.upper()}-ALT] Using page_code from URL:', page_code);
  }}'''
    
    if re.search(old_pattern2, content, re.MULTILINE):
        content = re.sub(old_pattern2, new_code2, content, flags=re.MULTILINE)
        return content, True
    
    return content, False

def fix_snucie_special_cases(content):
    """Спеціальні виправлення для Snucie"""
    
    # Виправляємо неправильний eventIdx в другому блоці
    content = re.sub(r'const eventIdx = 3; // Snucie', 'const eventIdx = 2; // Snucie (правильний індекс)', content)
    
    # Додаємо діагностику для всіх блоків
    content = re.sub(r'console\.log\(\'Loading data for page_code:\', page_code, \'eventIndex:\', eventIndex\);', 
                     'console.log(\'[SNUCIE] Loading data for page_code:\', page_code, \'eventIndex:\', eventIndex);', content)
    
    return content

def add_cache_busting(content):
    """Додає cache busting до API запитів"""
    
    # Додаємо timestamp до API запитів для запобігання кешуванню
    api_patterns = [
        r"fetch\('/api/event_date\?page=' \+ encodeURIComponent\(page_code\) \+ '&event=' \+ eventIndex\)",
        r"fetch\('/api/event_time\?page=' \+ encodeURIComponent\(page_code\) \+ '&event=' \+ eventIndex\)",
        r"fetch\('/api/event_places\?page=' \+ encodeURIComponent\(page_code\) \+ '&event=' \+ eventIndex\)",
        r"fetch\('/api/latest_event_data\?page=' \+ encodeURIComponent\(page_code\)\)"
    ]
    
    replacements = [
        "fetch('/api/event_date?page=' + encodeURIComponent(page_code) + '&event=' + eventIndex + '&_cb=' + Date.now())",
        "fetch('/api/event_time?page=' + encodeURIComponent(page_code) + '&event=' + eventIndex + '&_cb=' + Date.now())",
        "fetch('/api/event_places?page=' + encodeURIComponent(page_code) + '&event=' + eventIndex + '&_cb=' + Date.now())",
        "fetch('/api/latest_event_data?page=' + encodeURIComponent(page_code) + '&_cb=' + Date.now())"
    ]
    
    for pattern, replacement in zip(api_patterns, replacements):
        content = re.sub(pattern, replacement, content)
    
    return content

def fix_page_code_handling(file_path, event_name, event_index):
    """Виправляє обробку page_code на сторінці івенту"""
    
    if not os.path.exists(file_path):
        print(f"❌ Файл не знайдено: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixed = False
    
    # Стандартна обробка
    content, standard_fixed = fix_standard_page_code_handling(content, event_name, event_index)
    if standard_fixed:
        fixed = True
    
    # Альтернативна обробка
    content, alt_fixed = fix_alternative_page_code_handling(content, event_name)
    if alt_fixed:
        fixed = True
    
    # Спеціальні виправлення для Snucie
    if event_name == 'snucie':
        content = fix_snucie_special_cases(content)
        fixed = True
    
    # Додаємо cache busting
    content = add_cache_busting(content)
    
    # Записуємо файл тільки якщо були зміни
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Виправлено: {event_name} (index {event_index})")
        return True
    else:
        print(f"⚠️  Не потребує змін: {event_name}")
        return False

def main():
    """Головна функція"""
    base_dir = Path(__file__).parent / 'events-art.com'
    
    print("🔧 Повне виправлення обробки page_code на всіх сторінках івентів...")
    print("=" * 70)
    
    fixed_count = 0
    total_count = len(EVENT_PAGES)
    
    for event_name, event_index in EVENT_PAGES.items():
        file_path = base_dir / event_name / 'index.html'
        
        if fix_page_code_handling(file_path, event_name, event_index):
            fixed_count += 1
    
    print("=" * 70)
    print(f"📊 Результат: оброблено {fixed_count} з {total_count} сторінок")
    
    print("\n🎯 Що було виправлено:")
    print("✅ Правильна обробка page_code з URL")
    print("✅ Очищення застарілих даних з sessionStorage")
    print("✅ Діагностичні логи для відстеження проблем")
    print("✅ Cache busting для API запитів")
    print("✅ Спеціальні виправлення для Snucie")
    
    print("\n🧪 Тестування:")
    print("Зайдіть на сторінки івентів з правильним page_code:")
    for event_name in EVENT_PAGES.keys():
        print(f"  http://metanoia-gallery.com/{event_name}/?page=1-13")

if __name__ == '__main__':
    main()
