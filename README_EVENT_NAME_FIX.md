# Виправлення проблеми з event_name в логах

## Опис проблеми

Функція `format_order_start_message` в `main.py` не могла правильно отримати назву події з бази даних, тому в логах замість назви виставки показувалося "Выставка".

## Що було виправлено

### 1. Покращено функцію `get_event_name_from_page_code`

**Файл:** `main.py` (рядки 83-145)

- Додано пошук назви події в таблиці `event_links`
- Додано пошук назви події в таблиці `site_users`
- Збережено стару логіку як fallback

### 2. Додано можливість передавати `event_name` безпосередньо

**Файли:** `main.py`, `server.py`

- В `payment_notify` - для повідомлень про початок оформлення замовлення
- В `code_notify` - для повідомлень про запит коду
- В `send_payment_data` - через `server.py`
- В `send_code` - через `server.py`

### 3. Автоматичне отримання `event_name` з бази даних

**Файл:** `server.py`

Якщо `event_name` не передано, система автоматично спробує отримати його з бази даних.

## Як використовувати

### Варіант 1: Передавати `event_name` безпосередньо

```javascript
// Фронтенд може передавати event_name
fetch('/send_payment_data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Іван Петренко',
        page_code: '1-15',
        event_name: 'Terroir and Traditions',  // ← Нова можливість
        // ... інші поля
    })
});
```

### Варіант 2: Автоматичне отримання з бази

```javascript
// Якщо event_name не передано, система отримає його автоматично
fetch('/send_payment_data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'Іван Петренко',
        page_code: '1-15',
        // event_name відсутній - буде отримано з бази
    })
});
```

## Структура бази даних

### Таблиця `event_links`
```sql
CREATE TABLE event_links (
    id INTEGER PRIMARY KEY,
    event_code TEXT UNIQUE,
    event_name TEXT,  -- ← Назва події
    price TEXT,
    currency TEXT,
    user_id INTEGER
);
```

### Таблиця `site_users`
```sql
CREATE TABLE site_users (
    id INTEGER PRIMARY KEY,
    page_code TEXT,
    event_name TEXT,  -- ← Назва події
    price TEXT,
    currency TEXT,
    -- інші поля...
);
```

## Fallback логіка

Якщо `event_name` не знайдено в базі, система використовує стару логіку:

1. **За серією:** `1-15` → "Terroir and Traditions"
2. **За ключовими словами:** `gotong-royong` → "Gotong Royong"
3. **За замовчуванням:** "Выставка"

## Тестування

### Запуск тестів
```bash
python3 test_event_name.py
```

### Ручне тестування
```bash
# Тест payment_notify з event_name
curl -X POST http://127.0.0.1:8081/payment_notify \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Тестовий користувач",
    "page_code": "1-15",
    "event_name": "Terroir and Traditions"
  }'
```

## Переваги нового підходу

1. **Надійність** - назва події передається безпосередньо
2. **Швидкість** - не потрібно робити додаткові запити до бази
3. **Гнучкість** - можна передавати будь-яку назву події
4. **Зворотна сумісність** - стара логіка продовжує працювати

## Файли, що були змінені

- `main.py` - покращено `get_event_name_from_page_code`, додано підтримку `event_name`
- `server.py` - покращено `get_event_name_from_page_code`, додано підтримку `event_name`
- `EVENT_NAME_USAGE_EXAMPLES.md` - приклади використання
- `test_event_name.py` - скрипт для тестування
- `README_EVENT_NAME_FIX.md` - цей файл з інструкціями

## Висновок

Тепер система може правильно показувати назви подій в логах двома способами:
1. **Пряма передача** - фронтенд передає `event_name`
2. **Автоматичне отримання** - система отримує назву з бази даних

Це вирішує проблему з показом "Выставка" замість справжньої назви події.
