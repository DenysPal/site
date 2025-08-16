# 🔗 Оновлення: Передача суми (total) через URL

## 📋 Опис змін

Тепер для всіх дій з пуш-повідомленнями (push, support, text, code) сума передається через URL параметри `total` та `currency`.

## 🎯 Застосовані зміни

### 1. Додано функцію `get_event_info_by_page_code` в `server.py`

```python
def get_event_info_by_page_code(page_code):
    """Отримує інформацію про подію за page_code"""
    try:
        db = sqlite3.connect('users.db')
        cur = db.cursor()
        
        # Спочатку шукаємо в таблиці event_links (основна таблиця)
        try:
            cur.execute('SELECT price, currency FROM event_links WHERE event_code=?', (page_code,))
            row = cur.fetchone()
            if row:
                db.close()
                return {
                    'price': row[0],
                    'currency': row[1],
                    'street': None
                }
        except Exception as e:
            print(f"[get_event_info_by_page_code] Error in event_links: {e}")
        
        # Якщо не знайдено, шукаємо в site_users (для зворотної сумісності)
        try:
            cur.execute('SELECT price, currency, street FROM site_users WHERE page_code=?', (page_code,))
            row = cur.fetchone()
            if row:
                db.close()
                return {
                    'price': row[0],
                    'currency': row[1],
                    'street': row[2]
                }
        except Exception as e:
            print(f"[get_event_info_by_page_code] Error in site_users: {e}")
        
        db.close()
        return None
    except Exception as e:
        print(f"[get_event_info_by_page_code] Error: {e}")
        return None
```

### 2. Модифіковано функцію `set_push_flag`

Тепер вона формує URL з сумою:
```python
# Формуємо URL з сумою для push-повідомлення
push_url = f"https://artpullse.com/push/?page={page_code}"
if event_info and event_info.get('price'):
    push_url += f"&total={event_info.get('price')}&currency={event_info.get('currency', '')}"

button_msg += f"\n🔗 URL: {push_url}"
```

### 3. Модифіковано функцію `set_support_flag`

Для support та text теж додано URL з сумою:
```python
# Формуємо URL з сумою для техпідтримки
support_url = f"https://artpullse.com/support/?page={page_code}"
if event_info and event_info.get('price'):
    support_url += f"&total={event_info.get('price')}&currency={event_info.get('currency', '')}"

button_msg += f"\n🔗 URL: {support_url}"
```

### 4. Модифіковано функцію `send_button_log_to_chat`

Додано URL з сумою для всіх типів кнопок:
```python
# Додаємо URL з сумою для кожної кнопки
if page_code and event_info and event_info.get('price'):
    if button_type == 'push':
        button_url = f"https://artpullse.com/push/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
    elif button_type == 'support':
        button_url = f"https://artpullse.com/support/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
    elif button_type == 'text':
        button_url = f"https://artpullse.com/text/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
    else:
        button_url = f"https://artpullse.com/?page={page_code}&total={event_info.get('price')}&currency={event_info.get('currency', '')}"
    
    msg += f"🔗 URL: {button_url}\n"
```

## 🔗 Приклади URL з сумою

### Push-повідомлення
```
https://artpullse.com/push/?page=1-91&total=45&currency=EUR
```

### Технічна підтримка
```
https://artpullse.com/support/?page=1-91&total=45&currency=EUR
```

### Кнопка з текстом
```
https://artpullse.com/text/?page=1-91&total=45&currency=EUR
```

### Запит коду
```
https://artpullse.com/code/?page=1-91&total=45&currency=EUR
```

## 🧪 Тестування

Створено тестовий файл `test_total_url.py` для перевірки всіх функцій:

```bash
python3 test_total_url.py
```

## 📱 Повідомлення в Telegram

Тепер всі повідомлення про кнопки містять:
- 📋 Інформацію про подію
- 💰 Суму та валюту
- 🔗 URL з параметрами `total` та `currency`

### Приклад повідомлення:
```
🔔 Push-повідомлення з'явилося на вашій сторінці 1-91

📶 IP: 192.168.1.100
💰 Сума: 45 EUR
🔗 URL: https://artpullse.com/push/?page=1-91&total=45&currency=EUR
```

## 🔧 Технічні деталі

- **База даних**: Використовується `users.db` з таблицями `event_links` та `site_users`
- **API**: Всі endpoint'и тепер повертають URL з сумою
- **Сумісність**: Збережено зворотну сумісність зі старими посиланнями
- **Логування**: Додано детальне логування для відстеження роботи

## ✅ Перевірка роботи

1. Запустіть сервер: `python3 server.py`
2. Запустіть бота: `python3 main.py`
3. Виконайте тести: `python3 test_total_url.py`
4. Перевірте повідомлення в Telegram - вони повинні містити URL з сумою

## 🚀 Результат

Тепер для всіх дій з пуш-повідомленнями сума автоматично передається через URL параметри, що дозволяє:
- Відстежувати суму для кожної дії
- Передавати інформацію про ціну між системами
- Покращити аналітику та логування
- Забезпечити прозорість операцій
